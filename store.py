from database import session, base
from model import serverTable
import json 

def store_in_db(obj):
    db=session()
    try:
        new_entry=serverTable(
            gateway_id=obj.gateway_id,
            gateway_location=obj.gateway_location,
            node_id=obj.esp_data.node_id,
            gateway_time=obj.esp_data.gateway_time,
            data=json.dumps(obj.esp_data.esp_data)
        )
        db.add(new_entry)
        db.commit()
    finally:
        db.close()

    return "Stored in database!!"
