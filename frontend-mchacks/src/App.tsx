import { useState } from "react";
import "./App.css";
import WebSocketComponent from "./components/WebSocketComponent";
import { CartesianGrid, Legend, Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";

interface NewData {
  timestamp: string; // Incoming timestamp as a string
  askPriceAvg: number; // Incoming average price
}

interface DataItem {
  time: string; // Formatted time
  askPriceAvg: number; // Average price
}

function App() {
  const [data, setData] = useState<DataItem[]>([]);
  const [viewLimit, setViewLimit] = useState(20)

  const updateData = (newData: NewData) => {
    setData((prevData) => {
      const previousAskPriceAvg =
        prevData.length > 0 ? prevData[prevData.length - 1].askPriceAvg : 0;
  
      return [
        ...prevData,
        {
          time: new Date(newData.timestamp).toLocaleTimeString(),
          askPriceAvg: newData.askPriceAvg !== 0 ? newData.askPriceAvg : previousAskPriceAvg,
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
        <div className="w-full py-4 bg-red-500 flex flex-row justify-around">
          <p className="text-6xl font-bold text-white">SELL SELL SELL</p>
        </div>

        <div className="w-full h-full flex flex-row justify-around">
          <div className="stock-header-display">
            Stock A
            {difference !== null && (
              <p
                className={`font-bold ${
                  difference > 0 ? "text-green-500" : "text-red-500"
                }`}
              >
                {difference > 0 ? "+" : ""}
                {difference.toFixed(4)}
              </p>
            )}
          </div>
          <div className="stock-header-display">stock B</div>
          <div className="stock-header-display">stock C</div>
          <div className="stock-header-display">stock D</div>
          <div className="stock-header-display">stock E</div>
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
                <option value={data.length}>All</option>
              </select>
            </label>
          </div>

          <div className="w-auto h-auto">
            <LineChart
              width={window.innerWidth - 70}
              height={500}
              data={displayedData}
              margin={{ top: 10, right: 60, left: 30, bottom: 50 }}
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
              <Tooltip />
              {/* <Legend /> */}
              <Line
                type="monotone"
                dataKey="askPriceAvg"
                stroke="#8884d8"
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </div>
        </div>

      </div>
    </>
  );
}

export default App;
