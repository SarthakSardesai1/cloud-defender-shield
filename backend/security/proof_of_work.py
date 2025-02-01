import hashlib

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