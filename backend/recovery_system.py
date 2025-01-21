import json
from datetime import datetime
from typing import Dict, List
import logging
import os
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecoverySystem:
    def __init__(self, snapshot_dir: str = "snapshots"):
        self.snapshot_dir = snapshot_dir
        self.snapshots = []
        self.max_snapshots = 5
        self._ensure_snapshot_directory()
        
    def _ensure_snapshot_directory(self):
        """Ensure snapshot directory exists"""
        if not os.path.exists(self.snapshot_dir):
            os.makedirs(self.snapshot_dir)
            
    def create_snapshot(self, system_state: Dict) -> Dict:
        """Create a new system state snapshot"""
        timestamp = datetime.now().isoformat()
        snapshot = {
            "timestamp": timestamp,
            "state": system_state,
            "id": len(self.snapshots)
        }
        
        # Save snapshot to file
        snapshot_path = os.path.join(self.snapshot_dir, f"snapshot_{snapshot['id']}.json")
        with open(snapshot_path, 'w') as f:
            json.dump(snapshot, f)
        
        self.snapshots.append(snapshot)
        if len(self.snapshots) > self.max_snapshots:
            self._remove_oldest_snapshot()
            
        logger.info(f"Created snapshot {snapshot['id']} at {timestamp}")
        return snapshot
    
    def _remove_oldest_snapshot(self):
        """Remove oldest snapshot when limit is reached"""
        oldest = self.snapshots.pop(0)
        oldest_path = os.path.join(self.snapshot_dir, f"snapshot_{oldest['id']}.json")
        if os.path.exists(oldest_path):
            os.remove(oldest_path)
        logger.info(f"Removed oldest snapshot {oldest['id']}")
    
    def rollback_to_snapshot(self, snapshot_id: int) -> Dict:
        """Rollback system to a previous snapshot"""
        for snapshot in self.snapshots:
            if snapshot["id"] == snapshot_id:
                logger.info(f"Rolling back to snapshot {snapshot_id}")
                return {
                    "success": True,
                    "message": "System rolled back successfully",
                    "state": snapshot["state"]
                }
                
        logger.error(f"Snapshot {snapshot_id} not found")
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