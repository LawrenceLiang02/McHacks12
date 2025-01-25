import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

export const DataVisualization = ({ data: propData, companyName, height, width }) => {


    // Function to choose colors based on company name
    const getColorForGraph = (companyName) => {
      switch (companyName) {
        case "A":
          return { stroke: "#8884d8", fill: "url(#colorUv)" };
        case "B":
          return { stroke: "#82ca9d", fill: "url(#colorPv)" };
        case "C":
          return { stroke: "#ff7300", fill: "url(#colorCw)" };
        case "D":
          return { stroke: "#ff0000", fill: "url(#colorDx)" };
        case "E":
          return { stroke: "#0000ff", fill: "url(#colorEy)" };
        default:
          return { stroke: "#8884d8", fill: "url(#colorUv)" };
      }
    };

    if (propData.length === 0) {
      return <div>Waiting for data...</div>;
    }

    return (
      <ResponsiveContainer width={height} height={width}>
        <AreaChart width={350} height={100} data={propData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }} isAnimationActive={false}>
          <defs>
            <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorPv" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#82ca9d" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorCw" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ff7300" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#ff7300" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorDx" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ff0000" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#ff0000" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorEy" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#0000ff" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#0000ff" stopOpacity={0} />
            </linearGradient>
          </defs>
          <YAxis domain={[0, 200]} tick={{fontSize: 20}}/>
          <CartesianGrid strokeDasharray="3 3" />
          <Tooltip />
          
          {/* Format X-Axis to show seconds (or timestamp converted to time) */}
          <XAxis 
                dataKey="time"
                tickFormatter={(tick) => `${tick}s`}  // Format to show seconds
                tick={{ 
                    angle: -45,  // Rotate text by -45 degrees to make it inclined
                    fontSize: 20,  // Set font size to 10px (you can adjust this value)
                    textAnchor: 'end'  // Align text to the end after rotation
                }}
                height={100}
                />
          
          {/* Render the graph with dynamic colors */}
          <Area
            type="monotone"
            dataKey="askPriceAvg"  // Use actualPriceAvg for Y-axis
            stroke={getColorForGraph(companyName).stroke}
            fill={getColorForGraph(companyName).fill}
            fillOpacity={0.8}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    );
};
