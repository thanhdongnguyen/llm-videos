from flask import g
from chromadb.api import ClientAPI
from sqlalchemy import Select
from sqlalchemy.orm import Session
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.chat_engine.types import ChatMode
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.storage.chat_store.redis import RedisChatStore
import time

from llm_videos.models.chats import Chats
from llm_videos.models.videos import Videos
from llm_videos.models.account_config import AccountConfig
from llm_videos.errors.code import get_error


class ChatService:

    def __init__(self, session: Session, chromaDB: ClientAPI, chatStore: RedisChatStore):
        self.session = session
        self.chromaDB = chromaDB
        self.chatStore = chatStore
        self.chat_mode = ChatMode.CONDENSE_PLUS_CONTEXT

    def __handler_convertion(self, video_id: int, lang: str, query: str):
        user_id = g.user_id
        collection_name = f"{video_id}_{lang}"
        collection = self.chromaDB.get_collection(collection_name)
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        chat_memory = ChatMemoryBuffer.from_defaults(
            token_limit=3000,
            chat_store=self.chatStore,
            chat_store_key=f"{user_id}_{video_id}"
        )

        system_prompt = (f"You are a explain assistant. You are helping a user understand the content of a video. "
                         f"Mission of you only answer the question of user relate content video. And you answer "
                         f"question of user in language: {lang}.")

        vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context)
        index = vector_index.as_chat_engine(
            chat_mode=self.chat_mode,
            system_prompt=system_prompt,
            verbose=False,
            memory=chat_memory,
        )
        res = index.chat(message=query)

        return res.response

    def completion(self, form):
        user_id = g.user_id
        video_id = form.get("video_id")
        channel_id = f"{user_id}_{video_id}"

        u = Select(Videos).where(Videos.id == video_id)
        video = self.session.scalars(u).first()
        if video is None:
            return get_error(19)

        u = Select(AccountConfig).where(AccountConfig.user_id == user_id)
        account_config = self.session.scalars(u).first()
        target_language = "en"
        if account_config is not None:
            target_language = account_config.target_language

        new_chat_user = Chats(
            channel_id=channel_id,
            video_id=video_id,
            user_id=user_id,
            message=form.get("query"),
            type="human",
            status="success",
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        self.session.add(new_chat_user)

        new_chat_system = Chats(
            channel_id=channel_id,
            video_id=video_id,
            user_id=user_id,
            type="system",
            status="pending",
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        self.session.add(new_chat_system)

        self.session.commit()

        res = ""
        try:
            res = self.__handler_convertion(video_id, target_language, form.get("query"))
        except Exception as e:
            new_chat_system.message = "system error: " + str(e)
            new_chat_system.status = "error"
            new_chat_system.updated_at = int(time.time())

        self.session.commit()

        return {
            "success": True,
            "channel_id": channel_id,
            "reply": res
        }

    def history(self, video_id: int, limit: int, offset: int):
        user_id = g.user_id

        u = Select(Videos).where(Videos.id == video_id)
        video = self.session.scalars(u).first()

        if video is None:
            return get_error(19)

        u = Select(Chats).where(Chats.video_id == video_id).where(Chats.user_id == user_id).order_by(
            Chats.created_at.desc()).limit(limit).offset(offset)
        chats = self.session.scalars(u).all()

        return {
            "success": True,
            "data": chats,
            "total": 0
        }
