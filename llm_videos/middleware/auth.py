from flask_http_middleware import BaseHTTPMiddleware
from flask import jsonify, g
from sqlalchemy import select
from sqlalchemy.orm import Session
from loguru import logger
import time

from ..models.authentication import Authentication
from ..errors.code import get_error


class AuthMiddleware(BaseHTTPMiddleware):

    def __init__(self, engine, cache, routes=None):
        super().__init__()
        if routes is None:
            routes = []
        self.engine = engine
        self.cache = cache
        self.routes = routes
        self.session = Session(engine)

    def __find_access_token(self, access_token):
        logger.info(f"Access Token: {access_token}")
        try:
            u = select(Authentication).where(Authentication.access_token == access_token).where(Authentication.expired_at > int(time.time()))
            s = self.session.scalars(u).first()
        except:
            return None


        if s is None:
            logger.info(f"Not Found Access Token: {access_token}")
            return None
        logger.info(f"Access Token DB: {s.access_token}, user_id: {s.user_id}")
        return s

    def dispatch(self, request, call_next):

        if request.path not in self.routes:
            return call_next(request)

        access_token = request.headers.get("Authorization")

        if access_token is None:
            logger.info("Not Access Token")
            return jsonify(get_error(403))

        accessInfo = self.__find_access_token(access_token)
        if accessInfo is None:
            return jsonify((get_error(403)))

        g.user_id = accessInfo.user_id

        logger.info(f"Pass access token: {access_token}, user_id: {g.user_id}")
        return call_next(request)