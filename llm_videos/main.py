from os import environ, path
from os.path import join, dirname
import os, sys

sys.path.append(os.path.abspath(join(dirname(__file__), path.pardir)))

from flask import Flask, request, g
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from walrus import Database
from flask_http_middleware import MiddlewareManager
from loguru import logger
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
import chromadb
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.storage.chat_store.redis import RedisChatStore

from llm_videos.middleware.auth import AuthMiddleware
from llm_videos.errors.code import get_error

from llm_videos.schemas.register import RegisterSchema
from llm_videos.schemas.login import LoginSchema
from llm_videos.schemas.account import AccountUpdateSchema, UpdateConfigSchema
from llm_videos.schemas.video import ProcessYoutubeSchema, SummarizeVideoSchema
from llm_videos.schemas.chat import ChatSchema

"""
Service
"""
from llm_videos.services.user_service import UserService
from llm_videos.services.handler_video import HandlerVideoService
from llm_videos.services.account_config import AccountConfigService
from llm_videos.services.summarize import SummaryService
from llm_videos.services.chat import ChatService

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# init tracing
from langtrace_python_sdk import langtrace

if environ['LANGTRACE_API_KEY'] is not None:
    langtrace.init(api_key=environ['LANGTRACE_API_KEY'])

app = Flask(__name__)

db_user = environ["DB_USER"]
db_pass = environ["DB_PASS"]
db_host = environ["DB_HOST"]
db_port = environ["DB_PORT"]
db_name = environ["DB_DATABASE"]
port = int(environ["PORT"])
engine = create_engine(f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")
session = Session(engine)

db = Database(host=environ["REDIS_HOST"], port=int(environ["REDIS_PORT"]), db=0)
chromaDB = chromadb.PersistentClient(path=join(dirname(__file__), "chroma"), database="llm_videos")

chatStore = RedisChatStore(redis_url=f"redis://{environ['REDIS_HOST']}:{environ['REDIS_PORT']}/0", ttl=86400)

logger.add("logs/llm_videos.log", rotation="1 day", format="{time} {level} {message}", level="INFO")

Settings.llm = OpenAI(model="gpt-4", temperature=1, max_tokens=2000)

app.wsgi_app = MiddlewareManager(app)
app.wsgi_app.add_middleware(AuthMiddleware, engine=engine, cache=db.cache(), routes=[
    "/v1/account/info",
    "/v1/account/update",
    "/v1/account/config",
    "/v1/account/config/update",
    "/v1/video/youtube/process",
    "/v1/video/summarize",
    "/v1/video/chat/completion"
])


@app.errorhandler(Exception)
def error_handler(e):
    logger.error(f"Internal server error: {e}")
    return get_error(500), 500


@app.route("/v1/user/register", methods=["POST"])
def register():
    try:
        schema = RegisterSchema()
        form = schema.load(request.json)
    except:
        return get_error(17)

    user_service = UserService(session)

    resp = user_service.register(form)
    return resp


@app.route("/v1/user/login", methods=["POST"])
def login():
    try:
        schema = LoginSchema()
        form = schema.load(request.json)
    except:
        return get_error(17)

    user_service = UserService(session)

    resp = user_service.login(form)
    return resp


@app.route("/v1/account/info", methods=["GET"])
def getAccountInfo():
    user_id = g.user_id
    if user_id is None:
        return get_error(403)

    user_service = UserService(session)
    account_info = user_service.get_user_info(user_id)

    return account_info


@app.route("/v1/video/youtube/process", methods=["POST"])
def upload_video_youtube():
    try:
        schema = ProcessYoutubeSchema()
        form = schema.load(request.json)
    except:
        return get_error(17)

    video_service = HandlerVideoService(session, chromaDB)

    return video_service.process_youtube_video(form)


@app.route("/v1/account/update", methods=["POST"])
def update_user_info():
    try:
        schema = AccountUpdateSchema()
        form = schema.load(request.json)
    except:
        return get_error(17)

    user_service = UserService(session)

    resp = user_service.update_account_info(form)
    return resp


@app.route("/v1/account/config", methods=["GET"])
def get_config():
    account_config_service = AccountConfigService(session)

    resp = account_config_service.get_account_config()
    return resp


@app.route("/v1/account/config/update", methods=["POST"])
def update_config():
    try:
        schema = UpdateConfigSchema()
        form = schema.load(request.json)
    except:
        return get_error(17)

    account_config_service = AccountConfigService(session)
    return account_config_service.update_config(form)




@app.route("/v1/video/jobs/tracking", methods=["GET"])
def tracking_video_status():
    pass


@app.route("/v1/video/info", methods=["GET"])
def get_video_info():
    video_id = request.args.get("video_id")

    videoService = HandlerVideoService(session, chromaDB)
    return videoService.get_video_info(video_id)

@app.route("/v1/video/subtitle", methods=["GET"])
def get_video_subtitle():
    video_id = request.args.get("video_id")
    lang = request.args.get("lang")

    if video_id is None or lang is None:
        return get_error(17)

    videoService = HandlerVideoService(session, chromaDB)
    return videoService.get_video_subtitle(int(video_id), lang)


@app.route("/v1/video/summarize", methods=["POST"])
def summarize_video():
    try:
        schema = SummarizeVideoSchema()
        form = schema.load(request.json)
    except:
        return get_error(17)

    summarize_service = SummaryService(session, chromaDB)

    resp = summarize_service.get_summary(form.get("video_id"))
    return resp


@app.route("/v1/video/chat/completion", methods=["POST"])
def chat_video():
    try:
        schema = ChatSchema()
        form = schema.load(request.json)
    except:
        return get_error(17)

    chat_service = ChatService(session, chromaDB, chatStore)

    resp = chat_service.completion(form)
    return resp


@app.route("/v1/video/chat/history", methods=["POST"])
def chat_video():
    limit = request.args.get("limit") or 20
    offset = request.args.get("offset") or 0
    video_id = request.args.get("video_id")

    chat_service = ChatService(session, chromaDB, chatStore)

    resp = chat_service.history(int(video_id), limit, offset)
    return resp


if __name__ == "__main__":
    app.run(port=4001, debug=True)
