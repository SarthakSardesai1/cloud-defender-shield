import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const TrafficMonitor = () => {
  const [trafficData, setTrafficData] = useState<any[]>([]);

  useEffect(() => {
    // Simulate real-time traffic data
    const interval = setInterval(() => {
      setTrafficData(prev => {
        const newData = [...prev, {
          time: new Date().toLocaleTimeString(),
          traffic: Math.floor(Math.random() * 1000),
        }].slice(-20);
        return newData;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2 className="text-xl font-cyber font-bold text-white mb-4">Network Traffic Monitor</h2>
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trafficData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="time" stroke="#fff" />
            <YAxis stroke="#fff" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1a237e',
                border: '1px solid #0288d1',
                color: '#fff'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="traffic" 
              stroke="#00ff00" 
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TrafficMonitor;