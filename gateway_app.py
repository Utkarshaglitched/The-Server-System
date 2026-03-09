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

@app.post(f"/{post_auth}")
def recieve(packet: GatewayPacket):
    status=store_in_db(packet)
    print(status)

    return status

@app.get("/GateWay/Health")
def check():
    print("server connection health check intended!!")
    
    return {"status": 200, "msg": "connection working!!!"} 