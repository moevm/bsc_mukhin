from sqlalchemy import SmallInteger, PrimaryKeyConstraint, Column, String, UniqueConstraint, BigInteger, DateTime, \
    ForeignKeyConstraint, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.sqlite import JSON

Base = declarative_base()


class Account(Base):
    __tablename__ = 'account'

    id = Column(SmallInteger, autoincrement=True)
    name = Column(String, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='account_pkey'),
        UniqueConstraint('name', name='name_uniqueness'),
    )


class Settings(Base):
    __tablename__ = 'settings'

    param = Column(String, primary_key=True)
    value = Column(String, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('param', name='settings_pkey'),
    )


class Meeting(Base):
    __tablename__ = 'meeting'

    id = Column(BigInteger, primary_key=True)

    __table_args__ = (
        PrimaryKeyConstraint('param', name='meeting_pkey'),
    )


class MeetingConfig(Base):
    __tablename__ = 'meeting_config'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    meeting_id = Column(BigInteger)
    config = Column(JSON, nullable=False)
    ts = Column(DateTime, nullable=False)

    meeting = relationship('Meeting', lazy='joined')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='meeting_config_pkey'),
        ForeignKeyConstraint(('meeting_id',), ('meeting.id',), name='meeting_config_meeting_id_fkey'),
    )


class Log(Base):
    __tablename__ = 'log'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    meeting_config_id = Column(BigInteger)
    message = Column(JSON, nullable=False)
    ts = Column(DateTime, server_default=func.now())

    meeting = relationship('Meeting', lazy='joined')

    __table_args__ = (
        ForeignKeyConstraint(('meeting_config_id',), ('meeting_config.id',), name='log_meeting_config_id_fkey'),
    )


class Repository:
    instances = {}

    @classmethod
    async def create(cls, db_url: str, **kwargs):
        if db_url in Repository.instances:
            return Repository.instances[db_url]

        instance = cls()
        engine = create_engine(db_url, **kwargs)

        Base.metadata.create_all(engine)
        session = sessionmaker(engine, expire_on_commit=False)

        setattr(instance, 'session', session)
        setattr(instance, 'engine', engine)

        cls.instances[db_url] = instance
        return instance

