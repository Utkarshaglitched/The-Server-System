from fastapi import FastAPI,UploadFile, File, Form
from fastapi.responses import FileResponse
from template import GatewayPacket
from server_details import post_auth
from store import store_in_db
from contextlib import asynccontextmanager
import subprocess
from sqlalchemy import distinct
from database import session
from model import serverTable,firmwareTable
import json
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import os


db = session()

@asynccontextmanager
async def run_cloudflare(app: FastAPI):
    print("Starting cloudflare.....")
    process = subprocess.Popen(["cloudflared", "tunnel", "run", "iot-tunnel"])
    yield
    print("Stopping cloudflare.....")
    process.terminate()

app = FastAPI(lifespan=run_cloudflare)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(f"/{post_auth}")
def recieve(packet: GatewayPacket):
    status = store_in_db(packet)
    print(status)
    return status



@app.get("/GateWay/Health")
def check():
    return {"status": 200, "msg": "connection working!!!"}



@app.get("/GateWay/registered")
def registered():
    location = db.query(distinct(serverTable.gateway_location)).all()
    loc = [l[0] for l in location]
    return {"data": loc}



@app.get("/GateWay/{loc}/gateways")
def get_gateways(loc: str):
    gateways = db.query(distinct(serverTable.gateway_id)).filter(
        serverTable.gateway_location == loc
    ).all()

    gateway_list = [g[0] for g in gateways]

    return {"gateways": gateway_list}



@app.get("/GateWay/{loc}/{gateway_id}")
def get_nodes(loc: str, gateway_id: str):
    nodes = db.query(distinct(serverTable.node_id)).filter(
        serverTable.gateway_location == loc,
        serverTable.gateway_id == gateway_id
    ).all()

    node_list = [n[0] for n in nodes]

    return {"nodes": node_list}



@app.get("/GateWay/{loc}/{gateway_id}/{node}")
def get_node_logs(loc: str, gateway_id: str, node: str):
    data = db.query(serverTable).filter(
        serverTable.gateway_location == loc,
        serverTable.gateway_id == gateway_id,
        serverTable.node_id == node
    ).order_by(serverTable.gateway_time.desc()).all()

    return [
        {
            "gateway_id": d.gateway_id,
            "node_id": d.node_id,
            "data": json.loads(d.data),
            "time": d.gateway_time
        }
        for d in data
    ]

HEARTBEAT_INTERVAL = 15  
BUFFER = 120           
THRESHOLD = HEARTBEAT_INTERVAL + BUFFER
@app.get("/active/{loc}/{_gateway_id_}")
def heartbeat_check(loc: str, _gateway_id_: str):

    entry = db.query(serverTable).filter(
        serverTable.gateway_location == loc,
        serverTable.gateway_id == _gateway_id_,
        serverTable.node_id == "__heartbeat__"  
    ).order_by(serverTable.stored_at.desc()).first()

    if not entry:
        return {
            "gateway_id": _gateway_id_,
            "status": "offline",
            "last_seen": None
        }

    now = datetime.utcnow()
    last_seen = entry.stored_at

    diff = (now - last_seen).total_seconds()

    if diff <= THRESHOLD:
        status = "online"
    else:
        status = "offline"

        
    return {
        "gateway_id": _gateway_id_,
        "status": status,
        "last_seen": last_seen,
        "delay_seconds": int(diff),
        "threshold":int(THRESHOLD)
    }


@app.get("/activate/{loc}/{_gateway_id_}/{node}")
def active_node(loc: str, _gateway_id_: str, node: str):

    entry = db.query(serverTable).filter(
        serverTable.gateway_location == loc,
        serverTable.gateway_id == _gateway_id_,
        serverTable.node_id == node
    ).order_by(serverTable.stored_at.desc()).first()

    if not entry:
        return {
            "node": node,
            "status": "offline",
            "last_seen": None
        }

    now = datetime.utcnow()
    last_seen = entry.stored_at

    diff = (now - last_seen).total_seconds()

    if diff <= THRESHOLD:
        status = "online"
    else:
        status = "offline"

    return {
        "node": node,
        "status": status,
        "last_seen": last_seen,
        "delay_seconds": int(diff),
        "threshold": int(THRESHOLD)
    }

firmware_dir="firmware"
os.makedirs(firmware_dir,exist_ok=True)

@app.get("/firmware/{loc}/{gateway}")
def send_url_data(loc:str,gateway:str):
    entries = db.query(firmwareTable).filter(
        firmwareTable.target_gtw_loc == loc,
        firmwareTable.target_gtw == gateway
    ).order_by(firmwareTable.id.desc()).all()

    if not entries:
        return{
            "status":"No firmware update right now"
        }
    response=[]
    for i in entries:
        file_name=os.path.basename(i.firmware_path)
        response.append(
            {
                "target_node":i.target_gtw_nodeID,
                "file_name":file_name,
                "download_url":f"/firmware/download/{file_name}"
            }
        )
    return{
        "count":len(response),
        "data": response
    }

@app.get("/download/firmware/{file_name}")
def firmware_download(file_name:str):
    path=os.path.join(firmware_dir,file_name)
    if not os.path.exists(path):
        return {"error": "file not found"}

    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=file_name
    )





@app.post("/firmware/details")
async def details(
    file: UploadFile =File(...),
    Target_Gateway: str=Form(...),
    Target_GateWayLoc: str= Form(...),
    Target_NodeID: str=Form(...)):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    extension=file.filename.split(".")[-1]

    newName=f"{timestamp}.{extension}"
    File_Path=os.path.join(firmware_dir,newName)

    with open(File_Path, "wb") as f:
        content = await file.read()
        f.write(content)
    try:
        new_data_in_db=firmwareTable(
            target_gtw=Target_Gateway,
            target_gtw_loc=Target_GateWayLoc,
            target_gtw_nodeID=Target_NodeID,
            firmware_path=File_Path
        )

        db.add(new_data_in_db)
    except Exception as e:
        return {"msg":e}
    finally:
        db.commit()
        return{"status":200,"msg":"File Stored in db"}