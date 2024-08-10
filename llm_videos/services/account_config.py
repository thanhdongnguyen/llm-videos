from flask import g
import time
from sqlalchemy.orm import Session
from sqlalchemy import Select

from llm_videos.models.account_config import AccountConfig


class AccountConfigService:
    def __init__(self, session):
        self.session = session
    def get_account_config(self):
        user_id = g.user_id

        try:
            u = Select(AccountConfig).where(AccountConfig.user_id == user_id)
            s = self.session.scalars(u).first()
        except:
            self.__init_default_config()
            return {
                "success": True,
                "target_language": "en"
            }

        if s is None:
            self.__init_default_config()
            return {
                "success": True,
                "target_language": "en"
            }

        return {
            "success": True,
            "target_language": s.target_language
        }

    def __init_default_config(self):
        new_config = AccountConfig(user_id=g.user_id, target_language="en", created_at=int(time.time()), updated_at=int(time.time()))
        self.session.add(new_config)
        self.session.commit()
        return

    def update_config(self, form):
        user_id = g.user_id
        try:
            u = Select(AccountConfig).where(AccountConfig.user_id == user_id)
            s = self.session.scalars(u).first()
        except:
            return {
                "success": False
            }

        if "target_language" in form:
            s.target_language = form["target_language"]
        s.updated_at = int(time.time())
        self.session.commit()

        return {
            "success": True
        }