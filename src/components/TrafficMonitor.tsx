import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useQuery } from '@tanstack/react-query';

interface TrafficData {
  traffic_level: number;
  is_attack: boolean;
  timestamp: string;
}

const TrafficMonitor = () => {
  const [trafficHistory, setTrafficHistory] = useState<TrafficData[]>([]);

  const { data: trafficData } = useQuery({
    queryKey: ['traffic'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/traffic');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json() as Promise<TrafficData>;
    },
    refetchInterval: 1000,
  });

  useEffect(() => {
    if (trafficData) {
      setTrafficHistory(prev => {
        const newHistory = [...prev, trafficData].slice(-20); // Keep last 20 data points
        return newHistory;
      });
    }
  }, [trafficData]);

  return (
    <div>
      <h2 className="text-xl font-cyber font-bold text-white mb-4">Network Traffic Monitor</h2>
      <div className="text-sm text-gray-300 mb-2">
        Monitoring requests per second (RPS) across all servers
      </div>
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trafficHistory}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="timestamp" 
              stroke="#fff"
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis 
              stroke="#fff"
              label={{ 
                value: 'Requests/Second', 
                angle: -90, 
                position: 'insideLeft',
                style: { fill: '#fff' }
              }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1a237e',
                border: '1px solid #0288d1',
                color: '#fff'
              }}
              labelFormatter={(value) => `Time: ${new Date(value).toLocaleTimeString()}`}
              formatter={(value: number) => [`${value} RPS`, 'Traffic']}
            />
            <Line 
              type="monotone" 
              dataKey="traffic_level" 
              stroke="#00ff00" 
              strokeWidth={2}
              dot={false}
              name="Traffic"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      {trafficData?.is_attack && (
        <div className="mt-2 text-red-500 font-semibold">
          ⚠️ Abnormal traffic detected - Possible DDoS attack in progress
        </div>
      )}
    </div>
  );
};

export default TrafficMonitor;