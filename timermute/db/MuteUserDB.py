# coding: utf-8
import re

from sqlalchemy import asc, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from timermute.db.Base import Base
from timermute.db.Model import MuteUser


class MuteUserDB(Base):
    def __init__(self, db_fullpath: str = "mute.db"):
        super().__init__(db_fullpath)

    def select(self):
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        result = session.query(MuteUser).all()
        session.close()
        return result

    def upsert(self, record: str | MuteUser):
        if isinstance(record, str):
            screen_name = str(record)
            record = MuteUser(screen_name, "muted", self.now(), self.now())

        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        res = -1

        try:
            q = session.query(MuteUser).filter(MuteUser.screen_name == record.screen_name).with_for_update()
            p = q.one()
        except NoResultFound:
            # INSERT
            session.add(record)
            res = 0
        else:
            # UPDATE
            # id以外を更新する
            p.screen_name = record.screen_name
            p.status = record.status
            p.created_at = record.created_at
            p.updated_at = record.updated_at
            res = 1

        session.commit()
        session.close()
        return res

    def delete(self, key):
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        res = -1

        target = session.query(MuteUser).filter(MuteUser.screen_name == key).first()
        session.delete(target)
        res = 0

        session.commit()
        session.close()
        return res

    def mute(self, key):
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        res = -1

        target = session.query(MuteUser).filter(MuteUser.screen_name == key).first()
        target.status = "muted"
        res = 0

        session.commit()
        session.close()
        return res

    def unmute(self, key):
        Session = sessionmaker(bind=self.engine, autoflush=False)
        session = Session()
        res = -1

        target = session.query(MuteUser).filter(MuteUser.screen_name == key).first()
        target.status = "unmuted"
        res = 0

        session.commit()
        session.close()
        return res