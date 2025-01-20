from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import random
from typing import List, Dict
import numpy as np

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated traffic data
class TrafficMonitor:
    def __init__(self):
        self.baseline_traffic = 100
        self.current_requests = 0
        self.attack_threshold = 500

    def analyze_traffic(self) -> Dict:
        # Simulate traffic analysis
        self.current_requests = random.randint(50, 1000)
        is_attack = self.current_requests > self.attack_threshold
        return {
            "traffic_level": self.current_requests,
            "is_attack": is_attack,
            "timestamp": datetime.now().isoformat()
        }

# Initialize traffic monitor
traffic_monitor = TrafficMonitor()

@app.get("/api/traffic")
async def get_traffic():
    return traffic_monitor.analyze_traffic()

@app.get("/api/system-status")
async def get_system_status():
    return {
        "cpu_usage": random.randint(20, 80),
        "memory_usage": random.randint(30, 90),
        "network_load": random.randint(10, 60),
        "active_servers": 4,
        "response_time": random.randint(10, 50)
    }

@app.get("/api/attack-logs")
async def get_attack_logs():
    attack_types = ['UDP Flood', 'TCP SYN', 'ICMP Flood', 'HTTP Flood']
    statuses = ['Blocked', 'Detected', 'Mitigated']
    
    logs = []
    for _ in range(5):
        logs.append({
            "id": random.randint(1000, 9999),
            "timestamp": datetime.now().isoformat(),
            "type": random.choice(attack_types),
            "source": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "status": random.choice(statuses)
        })
    return logs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)