import { useState } from "react";
import "./App.css";
import WebSocketComponent from "./components/WebSocketComponent";
import { Area, AreaChart, CartesianGrid, Legend, Line, LineChart, ReferenceLine, Tooltip, XAxis, YAxis } from "recharts";

interface NewData {
  timestamp: string; // Incoming timestamp as a string
  bidVolumeSum: number;
  bidVolumeAvg: number;
  askVolumeSum: number;
  askVolumeAvg: number;
  actualVolumeSum: number;
  actualVolumeAvg: number;
  bidPriceSum: number;
  bidPriceAvg: number;
  askPriceSum: number;
  askPriceAvg: number;
  actualPriceSum: number;
  actualPriceAvg: number;
}

interface DataItem {
  time: string; // Formatted time
  bidVolumeSum: number;
  bidVolumeAvg: number;
  askVolumeSum: number;
  askVolumeAvg: number;
  actualVolumeSum: number;
  actualVolumeAvg: number;
  bidPriceSum: number;
  bidPriceAvg: number;
  askPriceSum: number;
  askPriceAvg: number;
  actualPriceSum: number;
  actualPriceAvg: number;
}

const CustomTooltip = ({
  active,
  payload,
  label,
  frozenData,
}: {
  active: boolean;
  payload?: any;
  label?: string;
  frozenData: { label: string; data: any } | null;
}) => {
  const displayedData = frozenData
    ? frozenData.data
    : active && payload && payload.length > 0
    ? payload[0].payload
    : null;
  const displayedLabel = frozenData?.label || label;

  if (displayedData) {
    return (
      <div
        className={`p-4 bg-white border-2 rounded shadow-md ${
          frozenData ? "border-yellow-500" : "border-gray-300"
        }`}
      >
        <p className="font-bold text-gray-700">Time: {displayedLabel}</p>
        <p className="text-gray-600">
          Ask Price Avg:{" "}
          {displayedData.askPriceAvg !== undefined
            ? displayedData.askPriceAvg.toFixed(2)
            : "N/A"}
        </p>
        <p className="text-gray-600">
          Bid Price Avg:{" "}
          {displayedData.bidPriceAvg !== undefined
            ? displayedData.bidPriceAvg.toFixed(2)
            : "N/A"}
        </p>
        <p className="text-gray-600">
          Ask Volume Avg:{" "}
          {displayedData.askVolumeAvg !== undefined
            ? displayedData.askVolumeAvg.toFixed(2)
            : "N/A"}
        </p>
        <p className="text-gray-600">
          Bid Volume Avg:{" "}
          {displayedData.bidVolumeAvg !== undefined
            ? displayedData.bidVolumeAvg.toFixed(2)
            : "N/A"}
        </p>
      </div>
    );
  }

  return null;
};

function App() {
  const [data, setData] = useState<DataItem[]>([]);
  const [viewLimit, setViewLimit] = useState(20)
  const [frozenData, setFrozenData] = useState<{ label: string; data: any } | null>(null);
  const handleChartClick = (e: any) => {
    if (e && e.activePayload) {
      const clickedData = {
        label: e.activeLabel,
        data: e.activePayload[0].payload,
      };
      setFrozenData((prev) =>
        prev?.label === clickedData.label ? null : clickedData
      );
    }
  };

  const updateData = (newData: NewData) => {
    setData((prevData) => {
      const previousActualPrice =
        prevData.length > 0 ? prevData[prevData.length - 1].actualPriceAvg : 0;
      const previousAskPrice =
        prevData.length > 0 ? prevData[prevData.length - 1].askPriceAvg : 0;
  
      return [
        ...prevData,
        // {
        //   time: new Date(newData.timestamp).toLocaleTimeString(),
        //   askPriceAvg: newData.askPriceAvg !== 0 ? newData.askPriceAvg : previousAskPriceAvg,
        // },
        {
          time: new Date(newData.timestamp).toLocaleTimeString(),
          bidVolumeSum: newData.bidVolumeSum,
          bidVolumeAvg: newData.bidVolumeAvg,
          askVolumeSum: newData.askVolumeSum,
          askVolumeAvg: newData.askVolumeAvg,
          actualVolumeSum: newData.actualVolumeSum,
          actualVolumeAvg: newData.actualVolumeAvg,
          bidPriceSum: newData.bidPriceSum,
          bidPriceAvg: newData.bidPriceAvg,
          askPriceSum: newData.askPriceSum,
          askPriceAvg: newData.askPriceAvg !== 0 ? newData.askPriceAvg : previousAskPrice,
          actualPriceSum: newData.actualPriceSum,
          actualPriceAvg: newData.actualPriceAvg !== 0 ? newData.actualPriceAvg : previousActualPrice,
        },
      ];
    });
  };

  const displayedData = data.slice(-viewLimit);

  const firstAskPrice = data.length > 0 ? data[0].askPriceAvg : null;
  const lastAskPrice = data.length > 0 ? data[data.length - 1].askPriceAvg : null;
  const difference = firstAskPrice !== null && lastAskPrice !== null 
    ? lastAskPrice - firstAskPrice 
    : null;

  return (
    <>
      <div className="w-screen min-h-screen flex flex-col items-center">
        <div className="w-full py-4 bg-cyan-950 flex flex-row justify-start px-12">
          <p className="text-4xl font-bold text-white capitalize">buy high sell low &#8482;</p>
        </div>
        <div className="w-full py-2 bg-red-500 flex flex-row justify-around">
          <p className="text-2xl font-bold text-white">SELL SELL SELL</p>
        </div>

        <div className="w-full h-full flex flex-row justify-around">
          <div className="stock-header-display">
            Stock A
            {difference !== null && (
              <p
                className={`font-bold ${
                  difference > 0 ? "text-green-500" : "text-red-500"
                }`}
              > {data[data.length - 1].askPriceAvg.toFixed(2)}
                 ({difference > 0 ? "+" : ""}
                {difference.toFixed(4)})
              </p>
            )}
          </div>
          <div className="stock-header-display">stock B</div>
          <div className="stock-header-display">stock C</div>
          <div className="stock-header-display">stock D</div>
          <div className="stock-header-display">stock E</div>
        </div>
          
        <div className="w-full px-40 pt-4">
          <div className="w-full bg-gray-100 flex flex-col items-center p-2 rounded-lg drop-shadow-lg">
            <p className="font-semibold text-black">Analytics</p>
          </div>
          
        </div>

        <div>
          <WebSocketComponent updateData={updateData} />
          <div style={{ margin: "20px 0", textAlign: "center" }}>
            <label htmlFor="viewLimit">
              Seconds to Display:{" "}
              <select
                id="viewLimit"
                value={viewLimit}
                onChange={(e) => setViewLimit(Number(e.target.value))}
              >
                <option value={50}>50</option>
                <option value={100}>100</option>
                <option value={500}>500</option>
                <option value={1000}>1000</option>
                <option value={data.length}>All</option>
              </select>
            </label>
          </div>

          <div className="w-auto h-auto">
            <AreaChart
              width={window.innerWidth - 70}
              height={450}
              data={displayedData}
              margin={{ top: 10, right: 60, left: 30, bottom: 50 }}
              onClick={handleChartClick}
            >
              <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
              <XAxis
                dataKey="time"
                angle={-45}
                label={{ 
                  position: "end",
                  offset: -10 }}
                tick={{ 
                  fontSize: 16,
                  textAnchor: 'end'
                }}
              />
              <YAxis
                label={{
                  angle: -90,
                  position: "insideLeft",
                }}
                domain={['dataMin - 0.05', 'dataMax + 0.05']}
                tickCount={10}
                tickFormatter={(value) => value.toFixed(2)}
              />
              <Tooltip
                content={
                  <CustomTooltip
                    active={!frozenData} // Tooltip should only be active if not frozen
                    frozenData={frozenData}
                  />
                }
              />
              {/* <Legend /> */}
              <Line
                type="monotone"
                dataKey="askPriceAvg"
                stroke="#8884d8"
                dot={false}
                isAnimationActive={false} // Disable animations
              />
              {firstAskPrice !== null && (
                <ReferenceLine
                  y={firstAskPrice}
                  stroke="red"
                  strokeDasharray="10 3"
                  label={{
                    value: `Initial Value: ${firstAskPrice.toFixed(2)}`,
                    position: "insideTopLeft",
                    fontSize: 12,
                  }}
                />
              )}
              <Area
                type="monotone"
                dataKey="askPriceAvg"
                stroke="#8884d8"
                dot={false}
                isAnimationActive={false}
              />
            </AreaChart>
          </div>
        </div>

      </div>
    </>
  );
}

export default App;
