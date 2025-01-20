import json
from datetime import datetime
from typing import Dict, List

class RecoverySystem:
    def __init__(self):
        self.snapshots = []
        self.max_snapshots = 5
        
    def create_snapshot(self, system_state: Dict) -> Dict:
        """Create a new system state snapshot"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "state": system_state,
            "id": len(self.snapshots)
        }
        
        self.snapshots.append(snapshot)
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots.pop(0)
            
        return snapshot
    
    def rollback_to_snapshot(self, snapshot_id: int) -> Dict:
        """Rollback system to a previous snapshot"""
        for snapshot in self.snapshots:
            if snapshot["id"] == snapshot_id:
                return {
                    "success": True,
                    "message": "System rolled back successfully",
                    "state": snapshot["state"]
                }
                
        return {
            "success": False,
            "message": "Snapshot not found",
            "state": None
        }
    
    def get_available_snapshots(self) -> List[Dict]:
        """Get list of available snapshots"""
        return [{
            "id": snapshot["id"],
            "timestamp": snapshot["timestamp"]
        } for snapshot in self.snapshots]