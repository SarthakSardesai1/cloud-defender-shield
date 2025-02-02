import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/components/ui/use-toast";

interface TrafficData {
  traffic_level: number;
  is_attack: boolean;
  timestamp: string;
}

const API_URL = import.meta.env.VITE_API_URL || window.location.origin;

const TrafficMonitor = () => {
  const [trafficHistory, setTrafficHistory] = useState<TrafficData[]>([]);
  const { toast } = useToast();

  // Generate fallback data for development and error cases
  const generateFallbackData = (): TrafficData => ({
    traffic_level: Math.floor(Math.random() * (1000 - 50) + 50),
    is_attack: Math.random() > 0.9,
    timestamp: new Date().toISOString()
  });

  // Initialize with some fallback data
  useEffect(() => {
    const initialData = Array.from({ length: 10 }, () => generateFallbackData());
    setTrafficHistory(initialData);
  }, []);

  const { data: trafficData, error, isError } = useQuery({
    queryKey: ['traffic'],
    queryFn: async () => {
      try {
        const response = await fetch(`${API_URL}/api/traffic`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json() as Promise<TrafficData>;
      } catch (error) {
        console.error('Error fetching traffic data:', error);
        return generateFallbackData();
      }
    },
    refetchInterval: 1000,
    retry: 3,
    onError: () => {
      toast({
        title: "Connection Error",
        description: "Unable to connect to monitoring server. Showing simulated data.",
        variant: "destructive",
      });
    }
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
      {isError && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>
            Unable to connect to monitoring server. Showing simulated data.
          </AlertDescription>
        </Alert>
      )}
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