# The-Server-System

Central server for the **IoT Gateway Architecture**.

This server receives data from IoT gateways, stores it in a database, and will provide a future **dashboard and device management interface**.

The goal of this system is to simulate **industrial IoT infrastructure**, where multiple edge gateways send sensor data to a centralized server.

---

# Architecture

```
IoT Nodes (ESP32 / Arduino / STM32)
        │
        │ JSON HTTP
        ▼
Gateway Device
(Local buffer + scheduler)
        │
        │ Forwarded packets
        ▼
Central Server (this project)
        │
        ▼
Database Storage
        │
        ▼
Future Web Dashboard / UI
```

---

# Server Responsibilities

The server acts as the **central data collector and storage system**.

Main tasks:

• Receive sensor data from gateways
• Validate incoming packets
• Store data in the server database
• Provide health endpoint for gateways
• Provide API endpoints for future UI dashboard

---

# Packet Structure

Gateways send packets in the following format:

```json
{
  "gateway_id": "GW01",
  "gateway_location": "Lab-A",
  "esp_data": {
    "node_id": "temp_node_01",
    "gateway_time": "2026-03-09T10:00:00",
    "esp_data": {
      "temperature": 25,
      "humidity": 60
    }
  }
}
```

This structure is validated using **Pydantic models**.

---

# Database Schema

The server stores incoming data in a table with fields such as:

* gateway_id
* gateway_location
* node_id
* gateway_time
* stored_at
* sensor data (JSON)

This allows:

• Tracking data by gateway
• Tracking data by node
• Timestamped sensor records

---

# API Endpoints

### Receive Gateway Data

```
POST /<post_auth>
```

Used by gateways to send sensor packets.

---

### Gateway Health Check

```
GET /GateWay/Health
```

Used by gateways to verify server connectivity.

Example response:

```
{
  "status": 200,
  "msg": "connection working!!!"
}
```

---

# Cloudflare Tunnel Support

The server automatically starts a **Cloudflare tunnel** when the application starts.

This allows remote access to the server without exposing ports directly.

---

# Installation

Clone repository

```
git clone https://github.com/<your-username>/The-Server-System.git
cd The-Server-System
```

Create virtual environment

```
python -m venv env
```

Activate environment

Linux / Mac

```
source env/bin/activate
```

Windows

```
env\Scripts\activate
```

Install dependencies

```
pip install -r requirements.txt
```

---

# Running the Server

Start the FastAPI server

```
uvicorn gateway_app:app --host 0.0.0.0 --port 9000
```

Server will start:

• API endpoints
• Cloudflare tunnel

---

# Project Structure

```
The-Server-System
│
├── gateway_app.py
├── database.py
├── model.py
├── store.py
├── template.py
├── server_details.py
├── requirements.txt
└── UI.py (planned)
```

---

# Planned Features

The server system is still under development.

Upcoming components:

### Web Dashboard

`UI.py`

Will provide:

• Gateway monitoring
• Node status
• Sensor data visualization
• Historical data charts

---

### Device Management

Future support for:

• Node registration
• Gateway authentication
• Device configuration

---

### Data Visualization

Dashboard will allow:

• Temperature graphs
• Sensor history
• Node activity tracking

---

# Purpose of the Project

This project aims to replicate **real-world IoT infrastructure concepts**, including:

• Edge gateway architectures
• Centralized IoT servers
• Device telemetry pipelines
• Scalable sensor data storage

---

# Related Project

This server works together with the gateway system:

**The-GateWay-System**

Gateway collects node data and forwards it to this server.

---
