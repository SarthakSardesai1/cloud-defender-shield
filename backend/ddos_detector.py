import numpy as np
from sklearn.preprocessing import StandardScaler
from collections import deque
import time

class DDoSDetector:
    def __init__(self):
        self.request_window = deque(maxlen=100)
        self.scaler = StandardScaler()
        self.threshold = 0.8
        
    def extract_features(self, request):
        """Extract features from a request for analysis"""
        return [
            request.get('request_per_second', 0),
            request.get('bytes_transferred', 0),
            request.get('connection_duration', 0)
        ]
    
    def is_attack(self, request):
        """Determine if current traffic pattern indicates a DDoS attack"""
        features = self.extract_features(request)
        self.request_window.append(features)
        
        if len(self.request_window) < 50:  # Need minimum data points
            return False
            
        # Convert to numpy array for analysis
        X = np.array(list(self.request_window))
        
        # Simple statistical analysis
        mean_rps = np.mean(X[:, 0])
        std_rps = np.std(X[:, 0])
        
        # If current RPS is significantly higher than mean
        current_rps = features[0]
        z_score = (current_rps - mean_rps) / (std_rps + 1e-10)
        
        return z_score > self.threshold