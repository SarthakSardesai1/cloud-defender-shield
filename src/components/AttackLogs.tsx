import React, { useEffect, useState } from 'react';
import { ScrollArea } from "@/components/ui/scroll-area";

interface Log {
  id: number;
  timestamp: string;
  type: string;
  source: string;
  status: string;
}

const AttackLogs = () => {
  const [logs, setLogs] = useState<Log[]>([]);

  useEffect(() => {
    // Simulate incoming logs
    const interval = setInterval(() => {
      const attackTypes = ['UDP Flood', 'TCP SYN', 'ICMP Flood', 'HTTP Flood'];
      const statuses = ['Blocked', 'Detected', 'Mitigated'];
      
      const newLog: Log = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString(),
        type: attackTypes[Math.floor(Math.random() * attackTypes.length)],
        source: `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
        status: statuses[Math.floor(Math.random() * statuses.length)]
      };

      setLogs(prev => [newLog, ...prev].slice(0, 10));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2 className="text-xl font-cyber font-bold text-white mb-4">Attack Logs</h2>
      
      <ScrollArea className="h-[300px]">
        <div className="space-y-2">
          {logs.map((log) => (
            <div 
              key={log.id}
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
          ))}
        </div>
      </ScrollArea>
    </div>
  );
};

export default AttackLogs;