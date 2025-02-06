
from collections import defaultdict
import time
import logging
from typing import Set, Dict, List

class DefenseMechanisms:
    def __init__(self):
        self.blacklist: Set[str] = set()
        self.rate_limits: Dict[str, float] = defaultdict(float)
        self.connection_tracker: Dict[str, List[float]] = defaultdict(list)
        self.blacklist_duration = 300  # 5 minutes
        self.rate_limit_window = 60  # 1 minute
        self.max_requests_per_window = 1000  # Increased from 100 to 1000 for normal usage
        
    def _apply_defense(self, ip: str, attack_type: str) -> None:
        if not ip or ip == 'unknown':
            return
            
        current_time = time.time()
        
        if attack_type in ['syn_flood', 'http_flood']:
            self.blacklist.add(ip)
            logging.info(f"IP {ip} blacklisted for {attack_type}")
            
        self.rate_limits[ip] = current_time
        self.connection_tracker[ip].append(current_time)
        self._cleanup_defense_lists()
    
    def _cleanup_defense_lists(self) -> None:
        current_time = time.time()
        
        self.blacklist = {ip for ip in self.blacklist 
                         if current_time - self.rate_limits.get(ip, 0) < self.blacklist_duration}
        
        self.rate_limits = {ip: time for ip, time in self.rate_limits.items() 
                          if current_time - time < self.rate_limit_window}
        
        for ip in list(self.connection_tracker.keys()):
            self.connection_tracker[ip] = [t for t in self.connection_tracker[ip] 
                                        if current_time - t < self.rate_limit_window]
            if not self.connection_tracker[ip]:
                del self.connection_tracker[ip]
                
    def check_rate_limit(self, ip: str) -> bool:
        if ip == 'unknown':
            return False
            
        current_time = time.time()
        recent_requests = len([t for t in self.connection_tracker.get(ip, [])
                             if current_time - t < self.rate_limit_window])
        
        return recent_requests > self.max_requests_per_window
        
    def is_blacklisted(self, ip: str) -> bool:
        return ip in self.blacklist

