from pydantic import BaseModel
from typing import Dict
from datetime import datetime



class ESPDataModel(BaseModel):
    node_id: str
    gateway_time: datetime
    esp_data: Dict 

class GatewayPacket(BaseModel):
    gateway_id: str
    gateway_location: str
    esp_data: ESPDataModel