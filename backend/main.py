from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import random
from typing import Dict
import logging
from ddos_detector import DDoSDetector
from load_balancer import LoadBalancer
from recovery_system import RecoverySystem
from cloud_integration import CloudIntegration
from resource_optimizer import ResourceOptimizer
from middleware.ddos_protection import DDoSProtectionMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='ddos_protection.log'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Initialize components
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add DDoS protection middleware
app.add_middleware(DDoSProtectionMiddleware, ddos_detector=ddos_detector, load_balancer=load_balancer)

@app.get("/api/traffic")
async def get_traffic() -> Dict:
    """Get current traffic metrics and attack status"""
    try:
        current_traffic = random.randint(50, 1000)
        
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system-metrics")
async def get_system_metrics() -> Dict:
    """Get system metrics including cloud and optimization data"""
    try:
        cloud_metrics = await cloud_integration.get_resource_metrics()
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
    except Exception as e:
        logger.error(f"Error getting system metrics: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)