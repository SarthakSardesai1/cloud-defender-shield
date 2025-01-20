import React from 'react';
import { Progress } from "@/components/ui/progress";
import { Server, Cpu, HardDrive } from 'lucide-react';

const SystemStatus = () => {
  return (
    <div>
      <h2 className="text-xl font-cyber font-bold text-white mb-4">System Status</h2>
      
      <div className="space-y-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Cpu className="text-cyber-secondary" />
            <span className="text-white">CPU Usage</span>
            <span className="ml-auto text-cyber-secondary">45%</span>
          </div>
          <Progress value={45} className="h-2" />
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2">
            <HardDrive className="text-cyber-secondary" />
            <span className="text-white">Memory Usage</span>
            <span className="ml-auto text-cyber-secondary">62%</span>
          </div>
          <Progress value={62} className="h-2" />
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2">
            <Server className="text-cyber-secondary" />
            <span className="text-white">Network Load</span>
            <span className="ml-auto text-cyber-secondary">28%</span>
          </div>
          <Progress value={28} className="h-2" />
        </div>

        <div className="grid grid-cols-2 gap-4 mt-4">
          <div className="bg-cyber-light p-4 rounded-lg">
            <span className="text-white block mb-1">Active Servers</span>
            <span className="text-cyber-secondary text-xl">4/4</span>
          </div>
          
          <div className="bg-cyber-light p-4 rounded-lg">
            <span className="text-white block mb-1">Response Time</span>
            <span className="text-cyber-secondary text-xl">24ms</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemStatus;