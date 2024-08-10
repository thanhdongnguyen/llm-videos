from flask import g
from loguru import logger
from os.path import join, dirname
from sqlalchemy import Select
import chromadb
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core import DocumentSummaryIndex, SimpleDirectoryReader
from llama_index.readers.chroma import ChromaReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.text_splitter import SentenceSplitter

from llm_videos.models.account_config import AccountConfig
from llm_videos.models.videos import Videos
from llm_videos.models.users_upload import UsersUpload
from llm_videos.errors.code import get_error


class SummaryService:
    def __init__(self, session, chromaDB):
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
        print(f"Handler summary: {video_id}_{lang}")
        # reader = ChromaReader(f"{video_id}_{lang}", persist_directory=join(dirname(__file__), '..', 'chroma'))
        # docs = reader.load_data()
        #
        docs = SimpleDirectoryReader(input_files=[join(dirname(__file__), '..', 'resources', f"{video_id}_{lang}.srt")], encoding="utf-8").load_data()
        response = get_response_synthesizer(response_mode="tree_summarize")

        text_spliter = SentenceSplitter(chunk_size=1024, chunk_overlap=10)

        docs_summary = DocumentSummaryIndex.from_documents(
            documents=docs,
            response_synthesizer=response,
            show_progress=True,
            transformations=[text_spliter],
        )
        print("docs_summary:", docs_summary)
        query = docs_summary.as_query_engine(response_mode="tree_summarize")
        print("query:", query)

        handler = query.query(f"Summary all content and convert to language: {lang}")
        print("handler:", handler)

        return handler.response

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
