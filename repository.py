import json
from typing import Optional

from sqlalchemy import (BigInteger, Boolean, Column, DateTime,
                        ForeignKeyConstraint, Integer, PrimaryKeyConstraint,
                        SmallInteger, String, UniqueConstraint, create_engine,
                        delete, func, insert, select)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class MeetingConfig(Base):
    __tablename__ = 'meeting_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    zoom_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    interval_days = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    host = Column(String, nullable=False)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    scheduled_meetings = relationship('ScheduledMeeting', lazy='subquery', backref='meeting_config')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='meeting_config_pkey'),
        UniqueConstraint('zoom_id', name='meeting_config_uniqueness'),
    )


class ScheduledMeeting(Base):
    __tablename__ = 'scheduled_meeting'

    id = Column(BigInteger().with_variant(Integer, 'sqlite'), primary_key=True, autoincrement=True)
    meeting_config_id = Column(Integer)
    ts = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)

    logs = relationship('Log', lazy='joined')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='meeting_config_pkey'),
        ForeignKeyConstraint(
            ('meeting_config_id',),
            ('meeting_config.id',),
            name='scheduled_meeting_meeting_id_fkey',
            ondelete='CASCADE'),
    )


class Log(Base):
    __tablename__ = 'log'

    id = Column(BigInteger().with_variant(Integer, 'sqlite'), primary_key=True, autoincrement=True)
    scheduled_meeting_id = Column(BigInteger)
    message = Column(JSON, nullable=False)
    ts = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)

    meeting = relationship('ScheduledMeeting', lazy='joined')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='log_pkey'),
        ForeignKeyConstraint(('scheduled_meeting_id',), ('scheduled_meeting.id',), name='log_scheduled_meeting_id_fkey', ondelete='CASCADE'),
    )


class Repository:
    instances = {}

    @classmethod
    def create(cls, db_url: str, **kwargs):
        if db_url in Repository.instances:
            return Repository.instances[db_url]

        instance = cls()
        engine = create_engine(
            db_url,
            json_serializer=lambda obj: json.dumps(obj, default=str),
            **kwargs,
        )

        Base.metadata.create_all(engine)
        session = sessionmaker(engine, expire_on_commit=False)

        setattr(instance, 'session', session)
        setattr(instance, 'engine', engine)

        cls.instances[db_url] = instance
        return instance

    def __init__(self):
        self.session = None
        self.engine = None

    def delete_meeting(self, meeting_id: int):
        stmt = delete(MeetingConfig).where(MeetingConfig.zoom_id == meeting_id)
        with self.session() as session:
            session.execute('PRAGMA foreign_keys = ON;')
            session.execute(stmt)
            session.commit()

    def add_meeting_config(self, meeting_config: dict):
        with self.session() as session:
            session.execute(insert(MeetingConfig).values(meeting_config))
            session.commit()

    def add_scheduled_meeting(self, zoom_id: int, scheduled_meeting: dict):
        with self.session() as session:
            meeting = session.execute(select(MeetingConfig).where(MeetingConfig.zoom_id == zoom_id)).scalar()
            meeting.scheduled_meetings.append(ScheduledMeeting(**scheduled_meeting))
            session.commit()

    def add_log(self, scheduled_meeting_id: int, log: dict):
        with self.session() as session:
            scheduled_meeting = session.execute(select(ScheduledMeeting)\
                                               .where(ScheduledMeeting.id == scheduled_meeting_id)).scalar()
            scheduled_meeting.logs.append(Log(**log))
            session.commit()

    def get_meetings(self) -> list:
        with self.session() as session:
            meetings = session.execute(select(MeetingConfig)).scalars().all()
            return meetings
