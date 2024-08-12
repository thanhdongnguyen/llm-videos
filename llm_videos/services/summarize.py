from flask import g
from loguru import logger
from os.path import join, dirname
from sqlalchemy import Select
import chromadb
from chromadb.api import ClientAPI
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import VectorStoreIndex

from llm_videos.models.account_config import AccountConfig
from llm_videos.models.videos import Videos
from llm_videos.models.users_upload import UsersUpload
from llm_videos.errors.code import get_error


class SummaryService:
    def __init__(self, session, chromaDB: ClientAPI):
        self.session = session
        self.chormaDB = chromaDB

    def __get_target_language(self) -> str:
        try:
            u = Select(AccountConfig).where(AccountConfig.user_id == g.user_id)
            s = self.session.scalars(u).first()
        except:
            return "en"

        if s is None:
            return "en"

        return s.target_language

    def __verify_user_uploaded(self, video_id: str, user_id: str) -> bool:
        try:
            u = Select(UsersUpload).where(UsersUpload.video_id == video_id).where(UsersUpload.user_id == user_id)
            s = self.session.scalars(u).first()
        except:
            return False

        if s is None:
            return False
        return True

    def __handler_summary(self, video_id: str, lang: str):
        collection = self.chormaDB.get_collection(f"{video_id}_{lang}")

        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context)
        index = index.as_query_engine()
        query = index.query(f"Summary of content of video and convert to language: {lang}")

        return query.response

    def get_summary(self, video_id):
        user_id = g.user_id
        target_language = self.__get_target_language()

        if self.__verify_user_uploaded(video_id, user_id) is False:
            return get_error(19)

        u = Select(Videos).where(Videos.id == video_id)
        s = self.session.scalars(u).first()
        if s is None:
            return get_error(19)

        summary = self.__handler_summary(video_id, target_language)

        return {
            "success": True,
            "video_id": video_id,
            "summary": summary
        }
