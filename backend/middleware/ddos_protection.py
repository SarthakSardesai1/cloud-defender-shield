from fastapi import Request, HTTPException
from typing import Callable, Awaitable
import logging
from ddos_detector import DDoSDetector
from load_balancer import LoadBalancer

logger = logging.getLogger(__name__)

class DDoSProtectionMiddleware:
    def __init__(self, ddos_detector: DDoSDetector, load_balancer: LoadBalancer):
        self.ddos_detector = ddos_detector
        self.load_balancer = load_balancer
        
    async def __call__(
        self, 
        request: Request, 
        call_next: Callable[[Request], Awaitable[Response]]
    ):
        try:
            # Extract request information safely
            client_host = request.client.host if request.client else "unknown"
            
            # Build request info dict
            request_info = {
                "source_ip": client_host,
                "request_per_second": 1,
                "bytes_transferred": 0,
                "connection_duration": 0,
                "syn_count": 0
            }
            
            # Try to get body size if available
            try:
                body = await request.body()
                request_info["bytes_transferred"] = len(body)
            except Exception:
                logger.debug("Could not read request body")
            
            # Check for DDoS attack
            if self.ddos_detector.is_attack(request_info):
                logger.warning(f"DDoS attack detected from {client_host}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests"}
                )
            
            # Apply load balancing
            distribution = self.load_balancer.distribute_request()
            if distribution["status"] == "rejected":
                logger.warning(f"Request rejected: {distribution['reason']}")
                return JSONResponse(
                    status_code=503,
                    content={"detail": distribution["reason"]}
                )
            
            # Process the request
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Error in DDoS protection middleware: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )