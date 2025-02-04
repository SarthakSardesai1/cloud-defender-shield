import logging
import time
from typing import Dict, Any
from security.proof_of_work import ProofOfWork
from security.defense_mechanisms import DefenseMechanisms
from ml.attack_detector import AttackDetector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='ddos_attacks.log'
)

class DDoSDetector:
    def __init__(self):
        self.pow_validator = ProofOfWork()
        self.defense = DefenseMechanisms()
        self.detector = AttackDetector()
        self.last_log_time = time.time()
        self.log_interval = 1
        
    def is_attack(self, request: Dict[str, Any]) -> bool:
        try:
            ip = request.get('source_ip', 'unknown')
            
            # Check if IP is blacklisted
            if self.defense.is_blacklisted(ip):
                logging.info(f"Blocked request from blacklisted IP: {ip}")
                return True
            
            # Check rate limits - More sensitive threshold
            if self.defense.check_rate_limit(ip):
                self.defense._apply_defense(ip, 'rate_limit_exceeded')
                return True
            
            features = self.detector.extract_features(request)
            self.detector.request_window.append(features)
            
            # More sensitive thresholds for demonstration
            # Volume-based attack detection - Lower threshold
            if features[0] > 100:  # Reduced from 1000 to 100 RPS
                self.defense._apply_defense(ip, 'http_flood')
                self._log_attack(request, 1.0, "High RPS detected")
                return True
                
            if features[1] > 100000:  # Reduced from 1000000 to 100000 bytes
                self.defense._apply_defense(ip, 'bandwidth_flood')
                self._log_attack(request, 1.0, "High bandwidth usage detected")
                return True

            # SYN flood detection - More sensitive
            if request.get('syn_count', 0) > 50:  # Reduced from default
                self.defense._apply_defense(ip, 'syn_flood')
                self._log_attack(request, 1.0, "SYN flood detected")
                return True
            
            # Basic statistical analysis for small window sizes
            if len(self.detector.request_window) < 100:
                return self.detector.basic_detection(features)
                
            # LSTM-based detection
            X = self.detector.prepare_sequence_data()
            if X is None:
                return self.detector.basic_detection(features)
                
            prediction = self.detector.model.predict(X, verbose=0)[0][0]
            
            # Lower threshold for demonstration
            if prediction > 0.6:  # Reduced from 0.8
                self.defense._apply_defense(ip, 'anomaly_detected')
                self._log_attack(request, prediction, "LSTM model detected anomaly")
                return True
                
            return False
            
        except Exception as e:
            logging.error(f"Error in DDoS detection: {str(e)}")
            return self.detector.basic_detection(features)
            
    def _log_attack(self, request: Dict[str, Any], confidence: float, attack_type: str = "Unknown"):
        attack_info = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'source_ip': request.get('source_ip', 'unknown'),
            'confidence': float(confidence),
            'request_rate': request.get('request_per_second', 0),
            'bytes': request.get('bytes_transferred', 0),
            'attack_type': attack_type
        }
        logging.warning(f"DDoS Attack Detected: {attack_info}")