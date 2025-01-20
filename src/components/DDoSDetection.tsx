import React, { useEffect, useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Shield, AlertTriangle } from 'lucide-react';

const DDoSDetection = () => {
  const [threatLevel, setThreatLevel] = useState(0);
  const [isUnderAttack, setIsUnderAttack] = useState(false);

  useEffect(() => {
    // Simulate threat detection
    const interval = setInterval(() => {
      const newThreatLevel = Math.random() * 100;
      setThreatLevel(newThreatLevel);
      setIsUnderAttack(newThreatLevel > 70);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2 className="text-xl font-cyber font-bold text-white mb-4">DDoS Detection Status</h2>
      
      <div className="space-y-4">
        <div>
          <div className="flex justify-between mb-2">
            <span className="text-white">Threat Level</span>
            <span className="text-cyber-secondary">{Math.round(threatLevel)}%</span>
          </div>
          <Progress value={threatLevel} className="h-2" />
        </div>

        {isUnderAttack && (
          <Alert variant="destructive" className="bg-red-900/50 border-red-500">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Attack Detected!</AlertTitle>
            <AlertDescription>
              High volume of suspicious traffic detected. Mitigation measures active.
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-2 gap-4 mt-4">
          <div className="bg-cyber-light p-4 rounded-lg">
            <div className="flex items-center gap-2">
              <Shield className="text-cyber-secondary" />
              <span className="text-white">Protection Status</span>
            </div>
            <span className="text-cyber-secondary">Active</span>
          </div>
          
          <div className="bg-cyber-light p-4 rounded-lg">
            <div className="flex items-center gap-2">
              <AlertTriangle className="text-cyber-secondary" />
              <span className="text-white">Blocked Attacks</span>
            </div>
            <span className="text-cyber-secondary">{Math.floor(Math.random() * 1000)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DDoSDetection;