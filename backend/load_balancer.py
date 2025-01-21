import time
from collections import defaultdict
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenBucket:
    def __init__(self, capacity: int, fill_rate: float):
        self.capacity = capacity
        self.fill_rate = fill_rate
        self.tokens = capacity
        self.last_update = time.time()
        
    def consume(self, tokens: int) -> bool:
        now = time.time()
        # Add tokens based on time passed
        time_passed = now - self.last_update
        self.tokens += time_passed * self.fill_rate
        self.tokens = min(self.tokens, self.capacity)
        self.last_update = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

class LoadBalancer:
    def __init__(self, servers: List[str]):
        self.servers = servers
        self.current_index = 0
        self.server_loads = defaultdict(int)
        self.server_health = {server: True for server in servers}
        self.token_buckets = {
            server: TokenBucket(capacity=1000, fill_rate=100)
            for server in servers
        }
        
    def get_next_server(self) -> str:
        """Advanced round-robin with health checks and load consideration"""
        attempts = 0
        while attempts < len(self.servers):
            selected_server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            
            if self.server_health[selected_server] and \
               self.server_loads[selected_server] < self.get_average_load() * 1.2:
                return selected_server
                
            attempts += 1
            
        # Fallback to least loaded server if no optimal server found
        return min(self.server_loads.items(), key=lambda x: x[1])[0]
    
    def get_average_load(self) -> float:
        if not self.server_loads:
            return 0
        return sum(self.server_loads.values()) / len(self.servers)
    
    def can_handle_request(self, server: str, request_size: int = 1) -> bool:
        """Check if server can handle more requests using token bucket"""
        return self.token_buckets[server].consume(request_size)
    
    def distribute_request(self, request_size: int = 1) -> Dict:
        server = self.get_next_server()
        
        if not self.server_health[server]:
            logger.warning(f"Server {server} is unhealthy, looking for alternative")
            return {"server": None, "status": "rejected", "reason": "unhealthy_server"}
            
        if not self.can_handle_request(server, request_size):
            logger.warning(f"Rate limit exceeded for server {server}")
            return {"server": None, "status": "rejected", "reason": "rate_limit"}
            
        self.server_loads[server] += request_size
        logger.info(f"Request distributed to server {server}")
        return {"server": server, "status": "accepted"}
    
    def update_server_health(self, server: str, is_healthy: bool):
        """Update server health status"""
        self.server_health[server] = is_healthy
        if not is_healthy:
            logger.warning(f"Server {server} marked as unhealthy")