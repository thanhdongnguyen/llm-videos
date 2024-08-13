from sqlalchemy.orm import Session
from loguru import logger
from os.path import join, dirname
from os import environ
from sqlalchemy import create_engine
import os
import time
import schedule

from llm_videos.models.background_jobs import BackgroundJobs
from llm_videos.models.videos import Videos
from llm_videos.translate.systran import SysTran
from llm_videos.models.video_subtitles import VideoSubtitles

db_user = environ["DB_USER"]
db_pass = environ["DB_PASS"]
db_host = environ["DB_HOST"]
db_port = environ["DB_PORT"]
db_name = environ["DB_DATABASE"]
port = int(environ["PORT"])
engine = create_engine(f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
session = Session(engine)

class VideoProcessing:

    def __init__(self, session: Session):
        self.session = session
        self.translator = SysTran()

    def process(self):
        background_jobs = self.session.query(BackgroundJobs).filter(BackgroundJobs.status == "pending").all()

        for job in background_jobs:
            status = self.translator.check_status_file(job.job_id)
            if status == "error":
                job.status = "error"
            elif status == "success":
                try:
                    res_file = self.translator.get_file_aysnc(job.job_id)
                except Exception as e:
                    logger.info(f"Job Processing, Get Status Error: {str(e)}")
                    continue
                text = res_file.message
                job.status = "success"

                new_video_subtitle = VideoSubtitles(
                    video_id=job.video_id,
                    language=job.target_language,
                    content=text,
                    created_at=int(time.time()),
                    updated_at=int(time.time())
                )
                self.session.add(new_video_subtitle)

        self.session.commit()
        return


v = VideoProcessing(session)
schedule.every(1).minutes.do(v.process)

while True:
    schedule.run_pending()
    time.sleep(1)

