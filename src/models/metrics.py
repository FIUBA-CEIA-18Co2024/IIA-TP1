from src.services.databases import Base
from src.config.settings import config
from sqlalchemy import Column, Integer, String, Float, DateTime



class Metrics(Base):
    __tablename__ = config["DATABASE_TABLE_METRICS"]

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, unique=True)
    model_name = Column(String(200))
    disks = Column(Integer)
    movements = Column(Integer)
    frontiers = Column(Integer)
    memory_allocation = Column(Float)
    execution_time = Column(Float)
    comments = Column(String(1000))
    
    def __repr__(self):
        return f"<{self.__class__.__name__} id: '{self.id}' model_name: '{self.model_name}'  timestamp: '{self.timestamp}'>"

    def __str__(self):
        return self.__repr__()
    