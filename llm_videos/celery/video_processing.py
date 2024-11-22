from os import environ, path
from os.path import join, dirname
import os, sys, time, schedule

sys.path.append(os.path.abspath(join(dirname(__file__), "..", path.pardir)))

from sqlalchemy.orm import Session
from loguru import logger
from sqlalchemy import create_engine
from dotenv import load_dotenv
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.text_splitter import SentenceSplitter
import chromadb
from walrus import Database
from celery import Celery

logger.add(f"{dirname(__file__)}/../logs/llm_videos.log", rotation="1 day", format="{time} {level} {message}",
           level="INFO")
dotenv_path = join(dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

from llm_videos.models.users_upload import UsersUpload
from llm_videos.models.videos import Videos
from llm_videos.models.video_subtitles import VideoSubtitles
from llm_videos.models.account_config import AccountConfig
from llm_videos.models.background_jobs import BackgroundJobs
from llm_videos.tools.file import save_file_subtitle
from llm_videos.translate.systran import SysTran

broker = f"redis://{environ['REDIS_HOST']}:{environ['REDIS_PORT']}/0"
db_user = environ["DB_USER"]
db_pass = environ["DB_PASS"]
db_host = environ["DB_HOST"]
db_port = environ["DB_PORT"]
db_name = environ["DB_DATABASE"]
port = int(environ["PORT"])
engine = create_engine(f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
session = Session(engine, expire_on_commit=False, autoflush=True)

app = Celery('video_processing', broker=broker)

db = Database(host=environ["REDIS_HOST"], port=int(environ["REDIS_PORT"]), db=0)
chromaDB = chromadb.PersistentClient(path=join(dirname(__file__), '..', "chroma"))


@app.task(name='video_processing.handler_vector_subtitle')
def handler_index_video_ytb(video_id, user_id, user_upload_id):
    user_upload = session.query(UsersUpload).where(UsersUpload.id == user_upload_id).first()
    if user_upload is None:
        return

    logger.info(f"Start index video: {video_id}")

    if user_upload.status == "success":
        return
    try:
        video_info = session.query(Videos).where(Videos.id == video_id).first()
        if video_info is None:
            return

        logger.info(f"Video info: {video_info}")


        video_subtitles = session.query(VideoSubtitles).where(VideoSubtitles.video_id == video_id).where(
            VideoSubtitles.language == video_info.lang).first()
        if video_subtitles is None:
            return

        logger.info(f"Video subtitle: {video_subtitles}")

        flag_index = False
        flag_tran = False
        if user_upload.vector_index_status == "pending":
            index = __handler_vector_subtitle(video_id, video_info.lang, video_subtitles.content)
            if index is not None:
                user_upload.vector_index_status = "success" if index else "error"
                user_upload.updated_at = int(time.time())
                session.commit()
                if index:
                    flag_index = True

        if user_upload.translate_processing_status == "pending":
            tran = __handler_translate_target_lang_subtitle(user_id, video_id, video_subtitles.content, video_info.lang)
            if tran is not None:
                user_upload.translate_processing_status = "success" if tran else "error"
                user_upload.updated_at = int(time.time())
                session.commit()
                if tran:
                    flag_tran = True

        if flag_tran and flag_index:
            user_upload.status = "success"
            user_upload.updated_at = int(time.time())
            session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Celery - Error index video: {video_id}, error: {str(e)}")
        user_upload = session.query(UsersUpload).where(UsersUpload.id == user_upload_id).first()
        user_upload.status = "error"
        user_upload.vector_index_status = "error"
        user_upload.translate_processing_status = "error"
        user_upload.updated_at = int(time.time())
        session.commit()
    return


def __handler_vector_subtitle(video_id: int, lang: str, content: str):
    collection_name = f"{video_id}_{lang}"
    try:
        exists = chromaDB.get_collection(collection_name)
        if exists is not None:
            return True
    except:
        logger.info(f"get_collection error: {collection_name}")

    print(f"Create collection: {collection_name}, video_id: {video_id}, lang: {lang}")

    collection = chromaDB.get_or_create_collection(f"{video_id}_{lang}")
    vector_store = ChromaVectorStore(chroma_collection=collection, collection_name=collection_name)
    file_path = save_file_subtitle(content, video_id, lang)

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
    return True


def __handler_translate_target_lang_subtitle(user_id, video_id, content, lang):
    dConfig = __get_account_config(user_id)
    if lang == dConfig.target_language:
        return None

    dSub = session.query(VideoSubtitles).where(VideoSubtitles.video_id == video_id).where(
        VideoSubtitles.language == dConfig.target_language).first()
    if dSub is not None:
        return None

    dJob = session.query(BackgroundJobs).where(BackgroundJobs.video_id == video_id).where(
        BackgroundJobs.target_language == dConfig.target_language).first()
    if dJob is not None and dJob.status != "error":
        return None

    file_path = save_file_subtitle(content, video_id, dConfig.target_language)
    translator = SysTran()
    res = translator.translate_file(file_path, lang, dConfig.target_language)

    logger.info(f"Translate subtitle: {res}")

    if res["success"] is False:
        return False

    new_job = BackgroundJobs(
        video_id=video_id,
        user_id=user_id,
        job_id=res["request_id"],
        target_language=dConfig.target_language,
        status="pending",
        created_at=int(time.time()),
        updated_at=int(time.time())
    )
    session.add(new_job)
    session.commit()
    return True


def __get_account_config(user_id):
    dConfig = session.query(AccountConfig).where(AccountConfig.user_id == user_id).first()
    if dConfig is None:
        return None
    return dConfig
