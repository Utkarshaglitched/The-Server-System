from fastapi import FastAPI
from template import GatewayPacket
from server_details import gateway_post_url

app=FastAPI()

@app.post(f"{gateway_post_url}")
def recieve(packet: GatewayPacket):
    pass