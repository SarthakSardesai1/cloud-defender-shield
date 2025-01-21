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
        self.request_window = deque(maxlen=1000)
        self.scaler = StandardScaler()
        self.pow_validator = ProofOfWork()
        self.setup_lstm_model()
        self.attack_threshold = 0.8
        
    def setup_lstm_model(self):
        self.model = Sequential([
            LSTM(64, input_shape=(100, 3), return_sequences=True),
            LSTM(32),
            Dense(1, activation='sigmoid')
        ])
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
    def extract_features(self, request):
        return [
            request.get('request_per_second', 0),
            request.get('bytes_transferred', 0),
            request.get('connection_duration', 0)
        ]
    
    def prepare_sequence_data(self):
        if len(self.request_window) < 100:
            return None
        
        X = np.array(list(self.request_window))
        X = self.scaler.fit_transform(X)
        X = X.reshape(1, 100, 3)
        return X
    
    def is_attack(self, request):
        """Determine if current traffic pattern indicates a DDoS attack"""
        features = self.extract_features(request)
        self.request_window.append(features)
        
        # Basic statistical analysis
        if len(self.request_window) < 100:
            return self._basic_detection(features)
            
        # LSTM-based detection
        X = self.prepare_sequence_data()
        if X is None:
            return False
            
        prediction = self.model.predict(X, verbose=0)[0][0]
        
        if prediction > self.attack_threshold:
            self._log_attack(request, prediction)
            return True
            
        return False
    
    def _basic_detection(self, features):
        """Fallback detection method when not enough data for LSTM"""
        current_rps = features[0]
        if len(self.request_window) > 10:
            mean_rps = np.mean([x[0] for x in self.request_window])
            std_rps = np.std([x[0] for x in self.request_window])
            z_score = (current_rps - mean_rps) / (std_rps + 1e-10)
            return z_score > 3
        return False
    
    def _log_attack(self, request, confidence):
        """Log detected attacks"""
        attack_info = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'source_ip': request.get('source_ip', 'unknown'),
            'confidence': float(confidence),
            'request_rate': request.get('request_per_second', 0),
            'bytes': request.get('bytes_transferred', 0)
        }
        logging.warning(f"DDoS Attack Detected: {attack_info}")