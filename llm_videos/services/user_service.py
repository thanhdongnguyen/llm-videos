from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from llm_videos.models.users import Users
from llm_videos.models.authentication import Authentication
from llm_videos.tools.bcrypt import hash_password, verify_password
from llm_videos.tools.string import random_string
from ..errors.code import get_error
import time
from loguru import logger


from flask import g


class UserService:

    def __init__(self, session):
        self.session = session

    def register(self, form) -> dict:
        email = form["email"]
        password = form["password"]

        u = select(Users).where(Users.email == email)
        s = self.session.scalars(u).first()

        if s is not None:
            return get_error(10)

        current_time = time.time()
        new_user = Users(email=email, password=hash_password(password), source_register="manual",
                         created_at=current_time, updated_at=current_time)
        self.session.add(new_user)
        self.session.commit()

        return {"success": True}

    def login(self, form):
        email = form["email"]
        password = form["password"]

        try:
            u = select(Users).where(Users.email == email)
            s = self.session.scalars(u).one()
        except:
            return get_error(11)

        logger.info(f"User: {s.email}, Password: {s.password}")
        if s is None:
            return get_error(11)

        if verify_password(password, s.password) is False:
            return get_error(12)

        u = delete(Authentication).where(Authentication.user_id == s.user_id)
        self.session.execute(u)

        access_token = random_string(32)
        current_time = time.time()
        new_auth = Authentication(user_id=s.user_id, access_token=access_token, expired_at=current_time + (86400 * 10),
                                  created_at=current_time, updated_at=current_time)
        self.session.add(new_auth)
        self.session.commit()

        return {
            "success": True,
            "access_token": access_token,
        }

    def get_user_info(self, user_id: int) -> dict:
        u = select(Users).where(Users.user_id == user_id)
        s = self.session.scalars(u).one()

        if s is None:
            return get_error(15)

        return {
            "success": True,
            "email": s.email,
            "source_register": s.source_register,
            "avatar": s.avatar,
            "user_id": s.user_id,
            "created_at": s.created_at,
            "updated_at": s.updated_at
        }

    def __find_diff_account(self, email: str, user_id: int):
        try:
            u = select(Users).where(Users.email == email).where(Users.user_id != user_id)
            s = self.session.scalars(u).one()
        except:
            return True

        return False

    def update_account_info(self, form):
        user_id = g.user_id

        if "email" in form:
            diff_account = self.__find_diff_account(form["email"], user_id)
            if diff_account is False:
                return get_error(18)

        logger.info(f"Update account, user_id: {user_id}")
        u = select(Users).where(Users.user_id == user_id)
        s = self.session.scalars(u).one()

        if s is None:
            return get_error(15)

        logger.info(f"Update account: {s.email}, user_id: {user_id}")
        if "email" in form:
            s.email = form["email"]
        if "avatar" in form:
            s.avatar = form["avatar"]

        s.updated_at = time.time()
        self.session.commit()

        return {"success": True}
