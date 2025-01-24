import React from 'react';
import TrafficMonitor from '../components/TrafficMonitor';
import DDoSDetection from '../components/DDoSDetection';
import SystemStatus from '../components/SystemStatus';
import AttackLogs from '../components/AttackLogs';
import { Card } from '@/components/ui/card';

const Index = () => {
  return (
    <div className="min-h-screen bg-cyber-gradient p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-cyber font-bold text-white mb-2">DDoS Protection System</h1>
        <p className="text-gray-300">Real-time Network Security Monitoring</p>
      </header>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-cyber-dark/80 p-6 rounded-lg border border-cyber-accent/20">
          <TrafficMonitor />
        </Card>
        
        <Card className="bg-cyber-dark/80 p-6 rounded-lg border border-cyber-accent/20">
          <DDoSDetection />
        </Card>
        
        <Card className="bg-cyber-dark/80 p-6 rounded-lg border border-cyber-accent/20">
          <SystemStatus />
        </Card>
        
        <Card className="bg-cyber-dark/80 p-6 rounded-lg border border-cyber-accent/20">
          <AttackLogs />
        </Card>
      </div>
    </div>
  );
};

export default Index;