from database import base,eng
from sqlalchemy import Column,Integer,String,DateTime,Text
from datetime import datetime

class serverTable(base):
    __tablename__="gateway_data"
    id=Column(Integer,primary_key=True)
    gateway_id=Column(String)
    gateway_location=Column(String,index=True)
    node_id = Column(String, index=True)
    gateway_time  = Column(DateTime)
    stored_at = Column(DateTime, default=datetime.utcnow)
    data=Column(Text)

base.metadata.create_all(bind=eng)