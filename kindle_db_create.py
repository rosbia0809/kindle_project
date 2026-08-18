import sqlalchemy
from kindle_database import Base

engine = sqlalchemy.create_engine('sqlite:///kindle.db',echo=True)

Base.metadata.create_all(engine)