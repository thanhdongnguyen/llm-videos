from . import Extract
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter, WebVTTFormatter
from urllib.parse import urlparse, parse_qs
from contextlib import suppress

def get_yt_id(url, ignore_playlist=False):
    # Examples:
    # - http://youtu.be/SA2iWivDJiE
    # - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    # - http://www.youtube.com/embed/SA2iWivDJiE
    # - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    query = urlparse(url)
    if query.hostname == 'youtu.be': return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com', 'music.youtube.com'}:
        if not ignore_playlist:
        # use case: get playlist id not current video in playlist
            with suppress(KeyError):
                return parse_qs(query.query)['list'][0]
        if query.path == '/watch': return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/watch/': return query.path.split('/')[2]
        if query.path[:7] == '/embed/': return query.path.split('/')[2]
        if query.path[:3] == '/v/': return query.path.split('/')[2]

class YoutubeExtract(Extract):

    def __init__(self, config: dict):
        self.config = config

        self.lang = "en"
        if self.config["lang"] is not None:
            self.lang = self.config["lang"]

    def get_sub(self, link: str) -> str:
        video_id = get_yt_id(link)
        path = f"{video_id}.txt"
        trans = YouTubeTranscriptApi.get_transcript(video_id, languages=[self.lang], preserve_formatting=True)
        formater = TextFormatter()
        text_format = formater.format_transcript(trans)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(text_format)

        return path

class DownloadYoutube:

    def __init__(self, config: dict):
        self.config = config

        self.save_path = config["save_path"]

    def download(self, link: str):
        return
