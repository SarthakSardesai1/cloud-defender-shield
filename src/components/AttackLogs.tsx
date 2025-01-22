import React from 'react';
import { ScrollArea } from "@/components/ui/scroll-area";
import { useQuery } from '@tanstack/react-query';

interface Log {
  timestamp: string;
  type: string;
  source: string;
  status: string;
}

const AttackLogs = () => {
  const { data: logs = [], isLoading } = useQuery({
    queryKey: ['attack-logs'],
    queryFn: async () => {
      const response = await fetch('/api/attack-logs');
      if (!response.ok) {
        throw new Error('Failed to fetch attack logs');
      }
      return response.json();
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  if (isLoading) {
    return (
      <div className="text-white">
        Loading attack logs...
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-cyber font-bold text-white mb-4">Attack Logs</h2>
      
      <ScrollArea className="h-[300px]">
        <div className="space-y-2">
          {logs.length === 0 ? (
            <div className="text-gray-400 text-center p-4">
              No attacks detected
            </div>
          ) : (
            logs.map((log, index) => (
              <div 
                key={index}
                className="bg-cyber-light p-3 rounded-lg border border-cyber-accent/20"
              >
                <div className="flex justify-between mb-1">
                  <span className="text-cyber-secondary text-sm">{log.timestamp}</span>
                  <span className={`text-sm ${
                    log.status === 'Blocked' ? 'text-green-400' :
                    log.status === 'Detected' ? 'text-yellow-400' :
                    'text-blue-400'
                  }`}>
                    {log.status}
                  </span>
                </div>
                <div className="text-white">{log.type}</div>
                <div className="text-gray-400 text-sm">Source: {log.source}</div>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
};

export default AttackLogs;