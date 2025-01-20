import time
from collections import defaultdict
from typing import List, Dict

class TokenBucket:
    def __init__(self, capacity: int, fill_rate: float):
        self.capacity = capacity
        self.fill_rate = fill_rate
        self.tokens = capacity
        self.last_update = time.time()
        
    def consume(self, tokens: int) -> bool:
        now = time.time()
        # Add tokens based on time passed
        self.tokens += (now - self.last_update) * self.fill_rate
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
        self.token_buckets = {
            server: TokenBucket(capacity=1000, fill_rate=100)
            for server in servers
        }
    
    def get_next_server(self) -> str:
        """Round-robin server selection with load consideration"""
        selected_server = self.servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.servers)
        return selected_server
    
    def can_handle_request(self, server: str) -> bool:
        """Check if server can handle more requests using token bucket"""
        return self.token_buckets[server].consume(1)
    
    def distribute_request(self) -> Dict:
        server = self.get_next_server()
        if self.can_handle_request(server):
            self.server_loads[server] += 1
            return {"server": server, "status": "accepted"}
        return {"server": None, "status": "rejected"}