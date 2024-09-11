from typing import List, Union
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, close_all_sessions

from src.config.settings import config



engine = create_engine(
    config['SQLALCHEMY_DATABASE_URL'],
    # SQLite requires the next arg:
    # connect_args={"check_same_thread": False},
    echo=config['SQLALCHEMY_DATABASE_ECHO'],
    pool_pre_ping=True,
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)

"""
# SQLite requires next decorator in order to use foreign key
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""


# The new base class will be given a metaclass that produces appropriate Table objects and makes the appropriate
# mapper() calls based on the information provided declarative in the class and any subclasses of the class:
Base = declarative_base()

# The 'sessionmaker' factory generates new Session objects when called
SessionLocalFactory = sessionmaker(bind=engine, autocommit=True, autoflush=False)


class DatabaseService:
    def __init__(self):
        print("Initializing DatabaseService instance")
        self.session_factory = SessionLocalFactory

    def __del__(self):
        print("Closing all connections...")
        close_all_sessions()

    @staticmethod
    def init_database():
        print("Initializing database...")
        Base.metadata.create_all(engine)
        close_all_sessions()

    def query_all(self, model, query_filter=None) -> List[Base]:
        with self.session_factory() as session:
            result = session.query(model)
            if query_filter:
                result = result.filter_by(**query_filter)
        return result.all()

    def query_one(self, model, query_filter=None) -> Union[Base, None]:
        with self.session_factory() as session:
            result = session.query(model)
            if query_filter:
                result = result.filter_by(**query_filter)
            one = result.first()
        return one

    def delete(self, model, query_filter) -> int:
        try:
            with self.session_factory() as session:
                with session.begin():
                    print(f'Deleting from DB {query_filter}')
                    r = session.query(model).filter_by(**query_filter).delete()
        except SQLAlchemyError as e:
            print(f'Error deleting from DB. Detail: {e}')
            r = 0
        return r

    def add(self, model_instance: Base) -> None:
        try:
            with self.session_factory() as session:
                with session.begin():
                    print(f"Adding '{model_instance}' into DB.")
                    merged = session.merge(model_instance)
                    session.add(merged)
        except SQLAlchemyError as e:
            print(f"Error adding into DB. Detail: {e}")
        else:
            print(f"Add successful.")