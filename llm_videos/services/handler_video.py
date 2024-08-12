from sqlalchemy.orm import Session
from sqlalchemy import Select
from loguru import logger
from flask import g
import time
import os
from os.path import join, dirname
import chromadb
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.text_splitter import SentenceSplitter

from llm_videos.tools.youtube import get_video_info, download_youtube_subtitle
from llm_videos.models.videos import Videos
from llm_videos.models.video_subtitles import VideoSubtitles
from llm_videos.models.users_upload import UsersUpload
from llm_videos.models.account_config import AccountConfig
from llm_videos.translate.systran import SysTran


class HandlerVideoService:
    def __init__(self, session, chromaDB):
        self.session = session
        self.chromaDB = chromaDB

    def __init_video_ytb(self, url):
        video_info = get_video_info(url)
        if video_info == {}:
            return None

        new_video = Videos(
            video_url=url,
            title=video_info["title"],
            thumbnail_url=video_info["thumbnail"],
            description=video_info["description"],
            lang=video_info["lang"],
            video_id=video_info["video_id"],
            created_at=int(time.time()),
            updated_at=int(time.time())
        )
        self.session.add(new_video)
        self.session.commit()

        return new_video

    def __handler_vector_subtitle(self, video_id: int, lang: str, content: str):
        collection_name = f"{video_id}_{lang}"
        try:
            exists = self.chromaDB.get_collection(collection_name)
            if exists is not None:
                return
        except:
            pass

        print(f"Create collection: {collection_name}, video_id: {video_id}, lang: {lang}")

        collection = self.chromaDB.get_or_create_collection(f"{video_id}_{lang}")
        vector_store = ChromaVectorStore(chroma_collection=collection, collection_name=collection_name)
        file_path = self.__save_file_subtitle(content, video_id, lang)

        print(f"File path: {file_path}")
        docs = SimpleDirectoryReader(input_files=[file_path], encoding="utf-8").load_data()

        context = StorageContext.from_defaults(
            vector_store=vector_store,
        )

        spliter = SentenceSplitter(chunk_size=1024, chunk_overlap=10)
        VectorStoreIndex.from_documents(
            documents=docs, storage_context=context,
            transformations=[spliter],
            show_progress=True,
        )
        return

    def process_youtube_video(self, form):

        user_id = g.user_id
        try:
            u = Select(Videos).where(Videos.video_url == form["youtube_url"])
            video_info = self.session.scalars(u).first()
        except:
            video_info = self.__init_video_ytb(form["youtube_url"])

        if video_info is None:
            video_info = self.__init_video_ytb(form["youtube_url"])

        print(f"Video info: {video_info}")
        vsub = Select(VideoSubtitles).where(VideoSubtitles.video_id == video_info.id).where(
            VideoSubtitles.language == video_info.lang)
        dsub = self.session.scalars(vsub).first()

        if dsub is None:
            subtitle_default = download_youtube_subtitle(video_info.video_url, video_info.lang)
            if subtitle_default is None:
                return {
                    "success": False
                }
            self.__handler_vector_subtitle(video_info.id, video_info.lang, subtitle_default)

            new_sub = VideoSubtitles(
                video_id=video_info.id,
                language=video_info.lang,
                content=subtitle_default,
                created_at=int(time.time()),
                updated_at=int(time.time())
            )
            self.session.add(new_sub)
            self.session.commit()

        videoU = Select(UsersUpload).where(UsersUpload.video_id == video_info.id).where(UsersUpload.user_id == user_id)
        dvideoU = self.session.scalars(videoU).first()
        if dvideoU is None:
            new_videoU = UsersUpload(
                video_id=video_info.id,
                user_id=user_id,
                created_at=int(time.time()),
                updated_at=int(time.time())
            )
            self.session.add(new_videoU)
            self.session.commit()

        handler_sub_target = self.__handler_target_lang_subtitle(video_info.id, video_info.video_url, video_info.lang)
        # if handler_sub_target is None:
        #     self.__handler_translate_subtitles(video_info.id, video_info.lang)

        return {
            "success": True
        }

    def __handler_target_lang_subtitle(self, id, url, lang):
        user_id = g.user_id

        vConfig = Select(AccountConfig).where(AccountConfig.user_id == user_id)
        dConfig = self.session.scalars(vConfig).first()

        if dConfig is None:
            return None

        if lang == dConfig.target_language:
            return None

        subtitle = download_youtube_subtitle(url, dConfig.target_language)
        if subtitle is None:
            return None
        self.__handler_vector_subtitle(id, dConfig.target_language, subtitle)

        vsub = Select(VideoSubtitles).where(VideoSubtitles.video_id == id).where(
            VideoSubtitles.language == dConfig.target_language)
        dsub = self.session.scalars(vsub).first()

        if dsub is None:
            new_sub = VideoSubtitles(
                video_id=id,
                language=dConfig.target_language,
                content=subtitle,
                created_at=int(time.time()),
                updated_at=int(time.time())
            )
            self.session.add(new_sub)
            self.session.commit()

        return True

    def __handler_translate_subtitles(self, id, lang):
        user_id = g.user_id

        vConfig = Select(AccountConfig).where(AccountConfig.user_id == user_id)
        dConfig = self.session.scalars(vConfig).first()

        if dConfig is None:
            return None

        vsub = Select(VideoSubtitles).where(VideoSubtitles.video_id == id).where(VideoSubtitles.language == lang)
        dsub = self.session.scalars(vsub).first()

        if dsub is None:
            return None

        file_path = self.__save_file_subtitle(dsub.content, id, lang)

        translate_provider = SysTran()

        resp = translate_provider.translate_file(file_path, lang, dConfig.target_language)

        logger.info(f"Translate subtitle: {resp}")

        return True

    def __save_file_subtitle(self, content: str, id: int, lang: str):
        output_path = join(dirname(__file__), '..', 'resources')

        file_path = f"{output_path}/{id}_{lang}.srt"
        if os.path.exists(file_path):
            return file_path

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        return file_path
