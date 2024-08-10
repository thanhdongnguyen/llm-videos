from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
import certifi, os
from os.path import join, dirname
from loguru import logger

os.environ["SSL_CERT_FILE"] = certifi.where()
output_path = join(dirname(__file__), '..', 'resources')


def download_youtube_video(url: str) -> str:
    try:
        yt = YouTube(url)

        file_path = f"{output_path}/{yt.video_id}.mp4"

        if os.path.exists(file_path):
            return file_path

        yt.streams.first().download(output_path, filename=yt.video_id)
        return file_path
    except:
        return ""


def get_video_info(url: str) -> dict:
    yt = YouTube(url)
    lang = "en"
    return {
        "video_id": yt.video_id,
        "title": yt.title,
        "thumbnail": yt.thumbnail_url,
        "description": yt.description,
        "lang": lang,
    }


def download_youtube_subtitle(url: str, lang: str = "en") -> str:
    try:

        yt = YouTube(url)
        id = yt.video_id
        # file_path = f"{output_path}/{id}.srt"
        #
        #
        #
        # if os.path.exists(file_path):
        #     return file_path

        data = YouTubeTranscriptApi.get_transcript(id, languages=[lang], preserve_formatting=True)
        format = SRTFormatter()


        resp = format.format_transcript(data)

        return resp

        # with open(file_path, 'w', encoding='utf-8') as file:
        #     file.write(resp)
        #
        # return file_path
    except Exception as e:
        logger.error(f"Download subtitle error: {e}")
        return None
