import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area} from 'recharts';

export const DataVisualization = () => {
  const [data, setData] = useState([]);
  const [startTime, setStartTime] = useState(null);  // Store the timestamp of the first data point
  
  useEffect(() => {
    const socket = new WebSocket('ws://127.0.0.1:5000/stream');  // Change this URL to your WebSocket server
    
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);

      // Only set the start time on the first message
      if (!startTime) {
        setStartTime(new Date(message.timestamp).getTime());
      }

      const currentTime = new Date(message.timestamp).getTime();
      const elapsedTime = Math.floor((currentTime - startTime) / 1000);  // Calculate elapsed time in seconds

      const newEntry = {
        name: elapsedTime,  // Use elapsed time in seconds as the X-axis value
        uv: message.bidPrice,  // Example: bidPrice is used here for Y-axis
        pv: message.askPrice,  // Example: askPrice is used here for a second line
      };

      setData(prevData => {
        const updatedData = [...prevData, newEntry];
        if (updatedData.length > 10) {
          updatedData.shift();  // Remove the first entry if there are more than 100 points
        }
        return updatedData;
      });
    };

    return () => {
      socket.close();
    };
  }, [startTime]);

  if (data.length === 0) {
    return <div>Waiting for data...</div>;
  }

  return (
    <ResponsiveContainer width={600} height={300}>
      <AreaChart width={530} height={250} data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }} isAnimationActive={false}>
        <defs>
          <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="colorPv" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#82ca9d" stopOpacity={0} />
          </linearGradient>
        </defs>
        <YAxis domain={[0, 200]} />
        <CartesianGrid strokeDasharray="3 3" />
        <Tooltip />
        
        {/* Format X-Axis to show seconds (e.g., 1s, 2s, 3s) */}
        <XAxis 
          dataKey="name"
          tickFormatter={(tick) => `${tick}s`}  // Format to show seconds
        />
        
        <Area type="monotone" dataKey="uv" stroke="#8884d8" fillOpacity={1} fill="url(#colorUv)" isAnimationActive={false} />
        <Area type="monotone" dataKey="pv" stroke="#82ca9d" fillOpacity={1} fill="url(#colorPv)" isAnimationActive={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
};
