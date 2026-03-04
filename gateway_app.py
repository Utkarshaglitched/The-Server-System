from fastapi import FastAPI
from template import GatewayPacket
from server_details import gateway_post_url,post_auth
from store import store_in_db
from contextlib import asynccontextmanager
import subprocess

@asynccontextmanager
async def run_cloudflare(app:FastAPI):
    print("Starting cloudflare.....")
    process=subprocess.Popen(["cloudflared", "tunnel", "run", "iot-server"])

    yield

    print("Stopping cloudflare.....") 
    process.terminate()

app=FastAPI(lifespan=run_cloudflare)

@app.post("/gateway_send")
def recieve(packet: GatewayPacket):
    status=store_in_db(packet)
    print(status)

    return status
