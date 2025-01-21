from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import random
from typing import List, Dict
import numpy as np
from .ddos_detector import DDoSDetector
from .load_balancer import LoadBalancer
from .recovery_system import RecoverySystem
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='ddos_protection.log'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize protection systems
ddos_detector = DDoSDetector()
load_balancer = LoadBalancer([
    "server1.example.com",
    "server2.example.com",
    "server3.example.com",
    "server4.example.com"
])
recovery_system = RecoverySystem()

@app.middleware("http")
async def ddos_protection_middleware(request: Request, call_next):
    """Middleware to check for DDoS attacks"""
    request_info = {
        "source_ip": request.client.host,
        "request_per_second": 1,  # This should be calculated based on recent requests
        "bytes_transferred": len(await request.body()),
        "connection_duration": 0,  # This should be measured
    }
    
    if ddos_detector.is_attack(request_info):
        logger.warning(f"DDoS attack detected from {request_info['source_ip']}")
        raise HTTPException(status_code=429, detail="Too many requests")
        
    response = await call_next(request)
    return response

@app.get("/api/traffic")
async def get_traffic():
    """Get real-time traffic statistics"""
    return {
        "traffic_level": load_balancer.get_average_load(),
        "is_attack": False,  # This will be set by the DDoS detector
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/system-status")
async def get_system_status():
    """Get real-time system status"""
    return {
        "cpu_usage": random.randint(20, 80),  # Replace with real metrics
        "memory_usage": random.randint(30, 90),
        "network_load": load_balancer.get_average_load(),
        "active_servers": sum(1 for healthy in load_balancer.server_health.values() if healthy),
        "response_time": random.randint(10, 50)  # Replace with real metrics
    }

@app.get("/api/attack-logs")
async def get_attack_logs():
    """Get real attack logs from the system"""
    with open('ddos_attacks.log', 'r') as f:
        logs = f.readlines()[-10:]  # Get last 10 logs
        
    parsed_logs = []
    for log in logs:
        if 'DDoS Attack Detected' in log:
            parsed_logs.append({
                "timestamp": log.split('[')[1].split(']')[0],
                "type": "DDoS Attack",
                "source": log.split('source_ip')[1].split(',')[0].strip(),
                "status": "Blocked"
            })
    
    return parsed_logs

@app.post("/api/create-snapshot")
async def create_snapshot():
    """Create a system state snapshot"""
    system_state = {
        "traffic_stats": load_balancer.server_loads,
        "server_health": load_balancer.server_health,
        "timestamp": datetime.now().isoformat()
    }
    return recovery_system.create_snapshot(system_state)

@app.post("/api/rollback/{snapshot_id}")
async def rollback_to_snapshot(snapshot_id: int):
    """Rollback to a previous system state"""
    return recovery_system.rollback_to_snapshot(snapshot_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)