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

from llm_videos.models.background_jobs import BackgroundJobs
from llm_videos.models.videos import Videos
from llm_videos.translate.systran import SysTran
from llm_videos.models.video_subtitles import VideoSubtitles



logger.add(f"{dirname(__file__)}/../logs/llm_videos.log", rotation="1 day", format="{time} {level} {message}", level="INFO")
dotenv_path = join(dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

db_user = environ["DB_USER"]
db_pass = environ["DB_PASS"]
db_host = environ["DB_HOST"]
db_port = environ["DB_PORT"]
db_name = environ["DB_DATABASE"]
port = int(environ["PORT"])
engine = create_engine(f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
session = Session(engine)
chromaDB = chromadb.PersistentClient(path=join(dirname(__file__), "..", "chroma"))

class VideoProcessing:

    def __init__(self, session: Session, chroma):
        self.session = session
        self.translator = SysTran()
        self.chromaDB = chroma

    def __save_file_subtitle(self, content: str, id: int, lang: str):
        output_path = join(dirname(__file__), '..', 'resources')

        file_path = f"{output_path}/{id}_{lang}.srt"
        if os.path.exists(file_path):
            return file_path

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        return file_path

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

    def process(self):
        background_jobs = self.session.query(BackgroundJobs).filter(BackgroundJobs.status == "pending").all()

        logger.info(f"Job Processing, Jobs: {len(background_jobs)}")

        for job in background_jobs:
            status = self.translator.check_status_file(job.job_id)
            logger.info(f"Job Processing, Job ID: {job.job_id}, Status: {status}")
            if status == "error":
                job.status = "error"
            elif status == "finished":
                try:
                    res_file = self.translator.get_file_aysnc(job.job_id)
                    logger.info(f"Job Processing, Get Status: {res_file}")
                except Exception as e:
                    logger.info(f"Job Processing, Get Status Error: {str(e)}")
                    continue
                text = res_file.get("message")
                job.status = "success"

                new_video_subtitle = VideoSubtitles(
                    video_id=job.video_id,
                    language=job.target_language,
                    content=text,
                    created_at=int(time.time()),
                    updated_at=int(time.time())
                )
                self.session.add(new_video_subtitle)
                logger.info(f"Job Processing, Add Subtitle: {new_video_subtitle}")
                self.__handler_vector_subtitle(job.video_id, job.target_language, text)
                logger.info(f"Job Processing, Handler Vector Subtitle")

        self.session.commit()
        return


v = VideoProcessing(session, chromaDB)
schedule.every(1).minutes.do(v.process)

while True:
    schedule.run_pending()
    time.sleep(1)

