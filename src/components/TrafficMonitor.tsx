
import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useQuery } from '@tanstack/react-query';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useToast } from "@/components/ui/use-toast";
import { Shield, AlertTriangle } from 'lucide-react';

interface TrafficData {
  traffic_level: number;
  is_attack: boolean;
  timestamp: string;
  attack_stats?: {
    total_attacks: number;
    last_attack_time: number | null;
    attack_types: Record<string, number>;
  };
}

const BACKEND_URL = 'http://localhost:8000';

const TrafficMonitor = () => {
  const [trafficHistory, setTrafficHistory] = useState<TrafficData[]>([]);
  const { toast } = useToast();
  const [attackCount, setAttackCount] = useState(0);

  const { data: trafficData, error } = useQuery({
    queryKey: ['traffic'],
    queryFn: async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/traffic`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Traffic data received:', data);
        return data as TrafficData;
      } catch (error) {
        console.error('Error fetching traffic data:', error);
        throw error;
      }
    },
    refetchInterval: 1000,
  });

  useEffect(() => {
    if (trafficData) {
      setTrafficHistory(prev => {
        const newHistory = [...prev, trafficData].slice(-20);
        return newHistory;
      });

      if (trafficData.is_attack) {
        setAttackCount(prev => prev + 1);
        toast({
          title: "⚠️ DDoS Attack Detected!",
          description: `Traffic spike detected. Protection measures active.`,
          variant: "destructive",
        });
      }
    }
  }, [trafficData, toast]);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-cyber font-bold text-white mb-4">Network Traffic Monitor</h2>
      
      {/* Attack Statistics Panel */}
      <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-4 mb-4">
        <div className="flex items-center gap-2 mb-2">
          <Shield className="text-red-500" />
          <h3 className="text-lg font-semibold text-white">Attack Statistics</h3>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-gray-300">Attacks Detected</p>
            <p className="text-2xl font-bold text-red-500">{attackCount}</p>
          </div>
          <div>
            <p className="text-gray-300">Current Status</p>
            <p className={`text-lg font-semibold ${trafficData?.is_attack ? 'text-red-500' : 'text-green-500'}`}>
              {trafficData?.is_attack ? 'Under Attack' : 'Normal'}
            </p>
          </div>
        </div>
        {trafficData?.attack_stats && (
          <div className="mt-2">
            <p className="text-gray-300">Attack Types:</p>
            <div className="grid grid-cols-2 gap-2 mt-1">
              {Object.entries(trafficData.attack_stats.attack_types).map(([type, count]) => (
                <div key={type} className="flex justify-between">
                  <span className="text-gray-400">{type}:</span>
                  <span className="text-red-400">{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Failed to fetch traffic data. Using fallback data.
          </AlertDescription>
        </Alert>
      )}

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
              stroke={trafficData?.is_attack ? "#ff0000" : "#00ff00"}
              strokeWidth={2}
              dot={false}
              name="Traffic"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {trafficData?.is_attack && (
        <div className="mt-4 bg-red-900/20 border border-red-500 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="text-red-500" />
            <span className="text-red-500 font-semibold">
              DDoS Attack in Progress
            </span>
          </div>
          <p className="text-gray-300 mt-2">
            Abnormal traffic patterns detected. Protection measures are active.
          </p>
        </div>
      )}
    </div>
  );
};

export default TrafficMonitor;
