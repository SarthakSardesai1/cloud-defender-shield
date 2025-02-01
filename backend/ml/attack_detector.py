import numpy as np
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from collections import deque
import logging
from typing import List, Optional, Dict, Any

class AttackDetector:
    def __init__(self):
        self.request_window = deque(maxlen=100)
        self.scaler = StandardScaler()
        self.attack_threshold = 0.8
        self.syn_flood_threshold = 100
        self.setup_lstm_model()
        
    def setup_lstm_model(self):
        self.model = Sequential([
            LSTM(64, input_shape=(100, 3), return_sequences=True),
            LSTM(32),
            Dense(1, activation='sigmoid')
        ])
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
    def extract_features(self, request: Dict[str, Any]) -> List[float]:
        rps = float(request.get('request_per_second', 0))
        bytes_transferred = float(request.get('bytes_transferred', 0))
        conn_duration = float(request.get('connection_duration', 0))
        return [rps, bytes_transferred, conn_duration]
        
    def prepare_sequence_data(self) -> Optional[np.ndarray]:
        if len(self.request_window) < 100:
            return None
            
        X = np.array(list(self.request_window))[-100:]
        
        if X.shape != (100, 3):
            return None
            
        X_scaled = self.scaler.fit_transform(X)
        X_reshaped = X_scaled.reshape(1, 100, 3)
        return X_reshaped
        
    def basic_detection(self, features: List[float]) -> bool:
        current_rps = features[0]
        if len(self.request_window) > 10:
            mean_rps = np.mean([x[0] for x in self.request_window])
            std_rps = np.std([x[0] for x in self.request_window])
            z_score = (current_rps - mean_rps) / (std_rps + 1e-10)
            
            if z_score > 3:
                return True
        return False