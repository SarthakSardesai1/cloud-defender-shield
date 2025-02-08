
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Play, Stop } from 'lucide-react';
import { useToast } from "@/components/ui/use-toast";

const BACKEND_URL = 'http://localhost:8000';

const AttackSimulator = () => {
  const [isAttacking, setIsAttacking] = useState(false);
  const [attackType, setAttackType] = useState('http_flood');
  const [intensity, setIntensity] = useState([50]);
  const { toast } = useToast();
  const [intervalId, setIntervalId] = useState<NodeJS.Timeout | null>(null);

  const simulateAttack = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/traffic`, {
        method: 'GET',
        headers: {
          'X-Test-Attack': 'true',
          'X-Attack-Type': attackType,
          'X-Attack-Intensity': intensity[0].toString()
        }
      });
      
      if (!response.ok) {
        throw new Error('Attack simulation failed');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Attack simulation error:', error);
      throw error;
    }
  };

  const startAttack = () => {
    setIsAttacking(true);
    toast({
      title: "Attack Simulation Started",
      description: `Running ${attackType} attack at ${intensity[0]}% intensity`,
    });

    // Start periodic attacks
    const id = setInterval(async () => {
      try {
        await simulateAttack();
      } catch (error) {
        console.error('Attack simulation error:', error);
      }
    }, 1000);

    setIntervalId(id);
  };

  const stopAttack = () => {
    if (intervalId) {
      clearInterval(intervalId);
      setIntervalId(null);
    }
    setIsAttacking(false);
    toast({
      title: "Attack Simulation Stopped",
      description: "Testing complete",
    });
  };

  return (
    <Card className="p-4 bg-black/20 border border-red-500/20">
      <h3 className="text-lg font-semibold text-white mb-4">Attack Simulator</h3>
      
      <div className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm text-gray-400">Attack Type</label>
          <Select
            value={attackType}
            onValueChange={setAttackType}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select attack type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="http_flood">HTTP Flood</SelectItem>
              <SelectItem value="syn_flood">SYN Flood</SelectItem>
              <SelectItem value="bandwidth_flood">Bandwidth Flood</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <label className="text-sm text-gray-400">Attack Intensity</label>
          <Slider
            value={intensity}
            onValueChange={setIntensity}
            max={100}
            step={1}
            className="py-4"
          />
          <div className="text-sm text-gray-400 text-right">
            {intensity[0]}%
          </div>
        </div>

        <div className="flex justify-end gap-2">
          {!isAttacking ? (
            <Button
              onClick={startAttack}
              className="bg-red-600 hover:bg-red-700"
            >
              <Play className="w-4 h-4 mr-2" />
              Start Attack
            </Button>
          ) : (
            <Button
              onClick={stopAttack}
              variant="outline"
              className="border-red-500 text-red-500 hover:bg-red-950"
            >
              <Stop className="w-4 h-4 mr-2" />
              Stop Attack
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
};

export default AttackSimulator;
