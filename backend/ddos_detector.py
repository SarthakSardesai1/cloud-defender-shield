
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
        self.attack_stats = {
            'total_attacks': 0,
            'last_attack_time': None,
            'attack_types': {}
        }
        
    def is_attack(self, request: Dict[str, Any]) -> bool:
        try:
            ip = request.get('source_ip', 'unknown')
            
            # Check if IP is blacklisted
            if self.defense.is_blacklisted(ip):
                self._update_attack_stats('blacklisted_ip')
                logging.info(f"Blocked request from blacklisted IP: {ip}")
                return True
            
            # Check rate limits - now much higher threshold
            if self.defense.check_rate_limit(ip):
                self._update_attack_stats('rate_limit_exceeded')
                self.defense._apply_defense(ip, 'rate_limit_exceeded')
                return True
            
            features = self.detector.extract_features(request)
            self.detector.request_window.append(features)
            
            # Extreme threshold values that would only trigger during actual attacks
            # Volume-based attack detection (over 2000 RPS)
            if features[0] > 2000:
                self._update_attack_stats('http_flood')
                self.defense._apply_defense(ip, 'http_flood')
                self._log_attack(request, 1.0, "High RPS detected")
                return True
                
            # Bandwidth threshold increased to 1MB per request
            if features[1] > 1000000:
                self._update_attack_stats('bandwidth_flood')
                self.defense._apply_defense(ip, 'bandwidth_flood')
                self._log_attack(request, 1.0, "High bandwidth usage detected")
                return True

            # SYN flood detection (extremely high threshold)
            if request.get('syn_count', 0) > 500:
                self._update_attack_stats('syn_flood')
                self.defense._apply_defense(ip, 'syn_flood')
                self._log_attack(request, 1.0, "SYN flood detected")
                return True
            
            # Only detect statistical anomalies for very obvious attacks
            if len(self.detector.request_window) >= 100:
                recent_requests = [r[0] for r in list(self.detector.request_window)[-10:]]
                avg_rps = sum(recent_requests) / len(recent_requests)
                if avg_rps > 1500:  # Extremely high sustained RPS
                    self._update_attack_stats('statistical_anomaly')
                    return True
                
            # LSTM-based detection with very high threshold
            X = self.detector.prepare_sequence_data()
            if X is None:
                return False
                
            prediction = self.detector.model.predict(X, verbose=0)[0][0]
            
            # Only trigger for extremely confident predictions
            if prediction > 0.99:
                self._update_attack_stats('ml_detected')
                self.defense._apply_defense(ip, 'anomaly_detected')
                self._log_attack(request, prediction, "LSTM model detected anomaly")
                return True
                
            return False
            
        except Exception as e:
            logging.error(f"Error in DDoS detection: {str(e)}")
            return False
            
    def _update_attack_stats(self, attack_type: str):
        """Update attack statistics for visualization"""
        self.attack_stats['total_attacks'] += 1
        self.attack_stats['last_attack_time'] = time.time()
        self.attack_stats['attack_types'][attack_type] = self.attack_stats['attack_types'].get(attack_type, 0) + 1
            
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
        
    def get_attack_stats(self) -> Dict:
        """Get current attack statistics"""
        return self.attack_stats

