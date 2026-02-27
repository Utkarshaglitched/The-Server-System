from fastapi import FastAPI
from template import GatewayPacket
from server_details import gateway_post_url,post_auth
from store import store_in_db
app=FastAPI()

@app.post(f"/{gateway_post_url}/{post_auth}")
def recieve(packet: GatewayPacket):
    status=store_in_db(packet)
    print(status)