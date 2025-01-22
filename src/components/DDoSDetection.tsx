import React from 'react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Shield, AlertTriangle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

interface SystemStatus {
  cpu_usage: number;
  memory_usage: number;
  network_load: number;
  active_servers: number;
  response_time: number;
}

interface TrafficData {
  traffic_level: number;
  is_attack: boolean;
  timestamp: string;
}

const DDoSDetection = () => {
  const { data: trafficData } = useQuery<TrafficData>({
    queryKey: ['traffic'],
    queryFn: async () => {
      const response = await fetch('/api/traffic');
      if (!response.ok) {
        throw new Error('Failed to fetch traffic data');
      }
      return response.json();
    },
    refetchInterval: 2000
  });

  const { data: systemStatus } = useQuery<SystemStatus>({
    queryKey: ['system-status'],
    queryFn: async () => {
      const response = await fetch('/api/system-status');
      if (!response.ok) {
        throw new Error('Failed to fetch system status');
      }
      return response.json();
    },
    refetchInterval: 2000
  });

  const threatLevel = systemStatus?.network_load || 0;
  const isUnderAttack = trafficData?.is_attack || false;

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
            <span className="text-cyber-secondary">
              {systemStatus?.active_servers ? 'Active' : 'Initializing...'}
            </span>
          </div>
          
          <div className="bg-cyber-light p-4 rounded-lg">
            <div className="flex items-center gap-2">
              <AlertTriangle className="text-cyber-secondary" />
              <span className="text-white">Response Time</span>
            </div>
            <span className="text-cyber-secondary">
              {systemStatus?.response_time || 0}ms
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DDoSDetection;