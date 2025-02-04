from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import random
from typing import List, Dict
import numpy as np
from ddos_detector import DDoSDetector
from load_balancer import LoadBalancer
from recovery_system import RecoverySystem
from cloud_integration import CloudIntegration
from resource_optimizer import ResourceOptimizer
import logging
import tensorflow as tf

# Disable TensorFlow warnings
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='ddos_protection.log'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000", 
        "http://127.0.0.1:5173",
        "https://6f3e5c78-1e96-4934-8dc5-b30fbda757bc.lovableproject.com",
        "https://*.lovableproject.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ddos_detector = DDoSDetector()
load_balancer = LoadBalancer([
    "server1.example.com",
    "server2.example.com",
    "server3.example.com",
    "server4.example.com"
])
recovery_system = RecoverySystem()
cloud_integration = CloudIntegration()
resource_optimizer = ResourceOptimizer()

@app.middleware("http")
async def ddos_protection_middleware(request: Request, call_next):
    """Enhanced middleware with cloud optimization"""
    try:
        # Get cloud metrics
        cloud_metrics = cloud_integration.get_resource_metrics()
        
        # Check if scaling is needed
        if cloud_integration.should_scale(cloud_metrics):
            logger.info("Resource scaling triggered based on metrics")
            optimized_resources = resource_optimizer.optimize_allocation({
                "cpu": cloud_metrics.cpu_usage,
                "memory": cloud_metrics.memory_usage,
                "network": cloud_metrics.network_throughput
            })
            
        # Extract request information
        request_info = {
            "source_ip": request.client.host,
            "request_per_second": 1,
            "bytes_transferred": len(await request.body()),
            "connection_duration": 0,
            "syn_count": random.randint(0, 150)
        }
        
        # Check for DDoS attack
        if ddos_detector.is_attack(request_info):
            logger.warning(f"DDoS attack detected from {request_info['source_ip']}")
            raise HTTPException(status_code=429, detail="Too many requests")
            
        # Apply load balancing
        selected_server = load_balancer.get_next_server()
        if not selected_server:
            raise HTTPException(status_code=503, detail="No available servers")
            
        response = await call_next(request)
        return response
        
    except Exception as e:
        logger.error(f"Error in DDoS protection middleware: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/traffic")
async def get_traffic():
    """Get current traffic metrics and attack status"""
    try:
        # Generate simulated traffic data
        current_traffic = random.randint(50, 1000)
        
        # Check if current traffic indicates an attack
        is_attack = ddos_detector.is_attack({
            "source_ip": "0.0.0.0",
            "request_per_second": current_traffic,
            "bytes_transferred": random.randint(1000, 10000),
            "connection_duration": random.randint(1, 10),
            "syn_count": random.randint(0, 150)
        })
        
        return {
            "traffic_level": current_traffic,
            "is_attack": is_attack,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting traffic data: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching traffic data")

@app.get("/api/system-metrics")
async def get_system_metrics():
    """Get enhanced system metrics including cloud and optimization data"""
    cloud_metrics = cloud_integration.get_resource_metrics()
    optimization_metrics = resource_optimizer.get_optimization_metrics()
    
    return {
        "cloud_metrics": {
            "cpu_usage": cloud_metrics.cpu_usage,
            "memory_usage": cloud_metrics.memory_usage,
            "network_throughput": cloud_metrics.network_throughput,
            "container_health": cloud_metrics.container_health
        },
        "optimization_metrics": optimization_metrics,
        "system_status": {
            "cpu_usage": random.randint(20, 80),
            "memory_usage": random.randint(30, 90),
            "network_load": load_balancer.get_average_load(),
            "active_servers": sum(1 for healthy in load_balancer.server_health.values() if healthy),
            "response_time": random.randint(10, 50)
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
