import numpy as np
from sklearn.preprocessing import StandardScaler
from collections import deque
import time
import hashlib
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import logging

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
        self.syn_flood_threshold = 100  # Threshold for SYN flood detection
        self.last_log_time = time.time()
        self.log_interval = 1  # Log every second
        
    def setup_lstm_model(self):
        self.model = Sequential([
            LSTM(64, input_shape=(100, 3), return_sequences=True),
            LSTM(32),
            Dense(1, activation='sigmoid')
        ])
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
    def extract_features(self, request):
        # Enhanced feature extraction with SYN flood detection
        rps = float(request.get('request_per_second', 0))
        bytes_transferred = float(request.get('bytes_transferred', 0))
        conn_duration = float(request.get('connection_duration', 0))
        
        # Additional SYN flood specific features
        syn_count = float(request.get('syn_count', 0))
        if syn_count > self.syn_flood_threshold:
            logging.warning(f"Potential SYN flood detected: {syn_count} SYN packets/sec")
            
        return [rps, bytes_transferred, conn_duration]
    
    def prepare_sequence_data(self):
        if len(self.request_window) < 100:
            return None
            
        X = np.array(list(self.request_window))[-100:]
        
        if X.shape != (100, 3):
            return None
            
        X_scaled = self.scaler.fit_transform(X)
        X_reshaped = X_scaled.reshape(1, 100, 3)
        return X_reshaped
    
    def is_attack(self, request):
        """Determine if current traffic pattern indicates a DDoS attack"""
        try:
            features = self.extract_features(request)
            self.request_window.append(features)
            
            current_time = time.time()
            if current_time - self.last_log_time >= self.log_interval:
                logging.info(f"Traffic metrics - RPS: {features[0]}, Bytes: {features[1]}, Duration: {features[2]}")
                self.last_log_time = current_time
            
            # Check for immediate high-volume indicators
            if features[0] > 1000:  # High RPS
                self._log_attack(request, 1.0, "High RPS detected")
                return True
                
            if features[1] > 1000000:  # High bandwidth usage (1MB/s)
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
                self._log_attack(request, prediction, "LSTM model detected anomaly")
                return True
                
            return False
            
        except Exception as e:
            logging.error(f"Error in DDoS detection: {str(e)}")
            return self._basic_detection(features)
    
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