import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

const TestPanel = () => {
  const [requestsPerSecond, setRequestsPerSecond] = useState<number>(100);
  const [duration, setDuration] = useState<number>(10);
  const [isAttacking, setIsAttacking] = useState(false);

  const simulateAttack = async () => {
    setIsAttacking(true);
    toast.info(`Starting test attack: ${requestsPerSecond} requests/sec for ${duration} seconds`);

    try {
      // Simulate multiple requests
      const requests = Array(requestsPerSecond).fill(null).map(() => 
        fetch('/api/traffic', {
          method: 'GET',
          headers: {
            'X-Test-Attack': 'true'
          }
        })
      );

      await Promise.all(requests);
      toast.success('Attack simulation completed');
    } catch (error) {
      toast.error('Attack simulation failed');
      console.error('Test error:', error);
    } finally {
      setIsAttacking(false);
    }
  };

  return (
    <div className="bg-cyber-dark/80 p-6 rounded-lg border border-cyber-accent/20">
      <h2 className="text-xl font-cyber font-bold text-white mb-4">Test Panel</h2>
      
      <div className="space-y-4">
        <div>
          <label className="text-white block mb-2">Requests per Second</label>
          <Input
            type="number"
            value={requestsPerSecond}
            onChange={(e) => setRequestsPerSecond(Number(e.target.value))}
            min="1"
            max="10000"
            className="bg-cyber-light text-white"
          />
        </div>

        <div>
          <label className="text-white block mb-2">Duration (seconds)</label>
          <Input
            type="number"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            min="1"
            max="60"
            className="bg-cyber-light text-white"
          />
        </div>

        <Button
          onClick={simulateAttack}
          disabled={isAttacking}
          className="w-full bg-red-600 hover:bg-red-700"
        >
          {isAttacking ? 'Simulating Attack...' : 'Start Attack Simulation'}
        </Button>
      </div>
    </div>
  );
};

export default TestPanel;