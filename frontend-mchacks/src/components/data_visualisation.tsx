import React from 'react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';

interface DataVisualizationProps {
  data: Array<{ time: number; askPriceAvg: number }>;
  companyName: string;
  height: string | number;
  width: string | number;
}

const DataVisualization: React.FC<DataVisualizationProps> = ({ data, companyName, height, width }) => {
  // Function to choose colors based on company name
  const getColorForGraph = (companyName: string): { stroke: string; fill: string } => {
    switch (companyName) {
      case 'A':
        return { stroke: '#8884d8', fill: 'url(#colorUv)' };
      case 'B':
        return { stroke: '#82ca9d', fill: 'url(#colorPv)' };
      case 'C':
        return { stroke: '#ff7300', fill: 'url(#colorCw)' };
      case 'D':
        return { stroke: '#ff0000', fill: 'url(#colorDx)' };
      case 'E':
        return { stroke: '#0000ff', fill: 'url(#colorEy)' };
      default:
        return { stroke: '#8884d8', fill: 'url(#colorUv)' };
    }
  };

  if (data.length === 0) {
    return <div>Waiting for data...</div>;
  }

  return (
    <ResponsiveContainer width={width} height={height}>
      <AreaChart
        width={350}
        height={100}
        data={data}
        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
      >
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
        <YAxis domain={[0, 200]} tick={{ fontSize: 20 }} />
        <CartesianGrid strokeDasharray="3 3" />
        <Tooltip />
        <XAxis
          dataKey="time"
          tickFormatter={(tick: number) => `${tick}s`}
          tick={{
            fontSize: 20,
            textAnchor: 'end',
          }}
          height={100}
        />
        <Area
          type="monotone"
          dataKey="askPriceAvg"
          stroke={getColorForGraph(companyName).stroke}
          fill={getColorForGraph(companyName).fill}
          fillOpacity={0.8}
          isAnimationActive={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
};

export default DataVisualization;
