from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.orm import sessionmaker, declarative_base

database_url="sqlite:///gateway.db"

eng=create_engine(database_url,connect_args={"check_same_thread":False})

session=sessionmaker(bind=eng)

base=declarative_base()