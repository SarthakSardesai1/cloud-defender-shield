import numpy as np
from sklearn.preprocessing import StandardScaler
from collections import deque, defaultdict
import time
import hashlib
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import logging
import ipaddress
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='ddos_attacks.log'
)

class ProofOfWork:
    def __init__(self, difficulty=4):
        self.difficulty = difficulty
        self.target = '0' * difficulty
        
    def generate_nonce(self, data: str) -> str:
        nonce = 0
        while True:
            hash_attempt = hashlib.sha256(f"{data}{nonce}".encode()).hexdigest()
            if hash_attempt.startswith(self.target):
                return str(nonce)
            nonce += 1
            
    def verify(self, data: str, nonce: str) -> bool:
        hash_check = hashlib.sha256(f"{data}{nonce}".encode()).hexdigest()
        return hash_check.startswith(self.target)

class DDoSDetector:
    def __init__(self):
        self.request_window = deque(maxlen=100)
        self.scaler = StandardScaler()
        self.pow_validator = ProofOfWork()
        self.setup_lstm_model()
        self.attack_threshold = 0.8
        self.syn_flood_threshold = 100
        self.last_log_time = time.time()
        self.log_interval = 1
        
        # Defense mechanisms
        self.blacklist = set()
        self.rate_limits = defaultdict(int)
        self.connection_tracker = defaultdict(list)
        self.blacklist_duration = 300  # 5 minutes
        self.rate_limit_window = 60  # 1 minute
        self.max_requests_per_window = 1000
        
    def setup_lstm_model(self):
        self.model = Sequential([
            LSTM(64, input_shape=(100, 3), return_sequences=True),
            LSTM(32),
            Dense(1, activation='sigmoid')
        ])
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
    def extract_features(self, request):
        rps = float(request.get('request_per_second', 0))
        bytes_transferred = float(request.get('bytes_transferred', 0))
        conn_duration = float(request.get('connection_duration', 0))
        
        # Enhanced SYN flood detection
        syn_count = float(request.get('syn_count', 0))
        if syn_count > self.syn_flood_threshold:
            logging.warning(f"Potential SYN flood detected: {syn_count} SYN packets/sec")
            self._apply_defense(request.get('source_ip', ''), 'syn_flood')
            
        return [rps, bytes_transferred, conn_duration]
    
    def _apply_defense(self, ip: str, attack_type: str):
        """Apply appropriate defense mechanism based on attack type"""
        if not ip or ip == 'unknown':
            return
            
        current_time = time.time()
        
        # Blacklist for severe attacks
        if attack_type in ['syn_flood', 'http_flood']:
            self.blacklist.add(ip)
            logging.info(f"IP {ip} blacklisted for {attack_type}")
            
        # Rate limiting
        self.rate_limits[ip] = current_time
        
        # Connection tracking for TCP-based attacks
        self.connection_tracker[ip].append(current_time)
        
        # Clean up old entries
        self._cleanup_defense_lists()
    
    def _cleanup_defense_lists(self):
        """Clean up expired entries from defense mechanisms"""
        current_time = time.time()
        
        # Clean blacklist
        self.blacklist = {ip for ip in self.blacklist 
                         if current_time - self.rate_limits.get(ip, 0) < self.blacklist_duration}
        
        # Clean rate limits
        self.rate_limits = {ip: time for ip, time in self.rate_limits.items() 
                          if current_time - time < self.rate_limit_window}
        
        # Clean connection tracker
        for ip in list(self.connection_tracker.keys()):
            self.connection_tracker[ip] = [t for t in self.connection_tracker[ip] 
                                        if current_time - t < self.rate_limit_window]
            if not self.connection_tracker[ip]:
                del self.connection_tracker[ip]
    
    def is_attack(self, request):
        """Determine if current traffic pattern indicates a DDoS attack"""
        try:
            ip = request.get('source_ip', 'unknown')
            
            # Check if IP is blacklisted
            if ip in self.blacklist:
                logging.info(f"Blocked request from blacklisted IP: {ip}")
                return True
            
            # Check rate limits
            if self._check_rate_limit(ip):
                self._apply_defense(ip, 'rate_limit_exceeded')
                return True
            
            features = self.extract_features(request)
            self.request_window.append(features)
            
            current_time = time.time()
            if current_time - self.last_log_time >= self.log_interval:
                logging.info(f"Traffic metrics - RPS: {features[0]}, Bytes: {features[1]}, Duration: {features[2]}")
                self.last_log_time = current_time
            
            # Volume-based attack detection
            if features[0] > 1000:  # High RPS
                self._apply_defense(ip, 'http_flood')
                self._log_attack(request, 1.0, "High RPS detected")
                return True
                
            if features[1] > 1000000:  # High bandwidth usage (1MB/s)
                self._apply_defense(ip, 'bandwidth_flood')
                self._log_attack(request, 1.0, "High bandwidth usage detected")
                return True
            
            # Basic statistical analysis for small window sizes
            if len(self.request_window) < 100:
                return self._basic_detection(features)
                
            # LSTM-based detection
            X = self.prepare_sequence_data()
            if X is None:
                return self._basic_detection(features)
                
            prediction = self.model.predict(X, verbose=0)[0][0]
            
            if prediction > self.attack_threshold:
                self._apply_defense(ip, 'anomaly_detected')
                self._log_attack(request, prediction, "LSTM model detected anomaly")
                return True
                
            return False
            
        except Exception as e:
            logging.error(f"Error in DDoS detection: {str(e)}")
            return self._basic_detection(features)
    
    def _check_rate_limit(self, ip: str) -> bool:
        """Check if IP has exceeded rate limits"""
        if ip == 'unknown':
            return False
            
        current_time = time.time()
        recent_requests = len([t for t in self.connection_tracker.get(ip, [])
                             if current_time - t < self.rate_limit_window])
        
        return recent_requests > self.max_requests_per_window
    
    def _basic_detection(self, features):
        """Fallback detection method when not enough data for LSTM"""
        current_rps = features[0]
        if len(self.request_window) > 10:
            mean_rps = np.mean([x[0] for x in self.request_window])
            std_rps = np.std([x[0] for x in self.request_window])
            z_score = (current_rps - mean_rps) / (std_rps + 1e-10)
            
            if z_score > 3:
                self._log_attack(
                    {"source_ip": "unknown", "request_per_second": current_rps},
                    z_score / 10,
                    "Statistical anomaly detected"
                )
                return True
        return False
    
    def prepare_sequence_data(self):
        if len(self.request_window) < 100:
            return None
            
        X = np.array(list(self.request_window))[-100:]
        
        if X.shape != (100, 3):
            return None
            
        X_scaled = self.scaler.fit_transform(X)
        X_reshaped = X_scaled.reshape(1, 100, 3)
        return X_reshaped
    
    def _log_attack(self, request, confidence, attack_type="Unknown"):
        """Enhanced attack logging"""
        attack_info = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'source_ip': request.get('source_ip', 'unknown'),
            'confidence': float(confidence),
            'request_rate': request.get('request_per_second', 0),
            'bytes': request.get('bytes_transferred', 0),
            'attack_type': attack_type
        }
        logging.warning(f"DDoS Attack Detected: {attack_info}")