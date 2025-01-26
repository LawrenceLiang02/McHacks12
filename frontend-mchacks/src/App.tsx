import { useState } from "react";
import "./App.css";
import WebSocketComponent from "./components/WebSocketComponent";
import { CustomTooltip, ChartComponent } from "./components/TableComponent";

interface NewData {
  timestamp: string;
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
  time: string;
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

function App() {
  const [data, setData] = useState<DataItem[]>([]);
  const [viewLimit, setViewLimit] = useState(20);
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

  const calculateDifference = (
    dataList: DataItem[],
    field: string
  ): number | null => {
    if (dataList.length === 0) return null;
  
    const firstValue = dataList[0][field];
    const lastValue = dataList[dataList.length - 1][field];
  
    if (firstValue !== undefined && lastValue !== undefined) {
      return (lastValue - firstValue).toFixed(4);
    }
  
    return null;
  };

  return (
    <>
      <div className="w-screen min-h-screen flex flex-col items-center">
        {/* Header */}
        <div className="w-full py-4 bg-cyan-950 flex flex-row justify-start px-12">
          <p className="text-4xl font-bold text-white capitalize">buy high sell low &#8482;</p>
        </div>
        <div className="w-full py-2 bg-red-500 flex flex-row justify-around">
          <p className="text-2xl font-bold text-white">SELL SELL SELL</p>
        </div>

        {/* Stock Displays */}
        <div className="w-full h-full flex flex-row justify-around">
          {["A", "B", "C", "D", "E"].map((stock, index) => (
            <div key={index} className="stock-header-display">
              Stock {stock}
              <p className={
                    calculateDifference(data, "askPriceAvg") > 0
                      ? "text-green-500"
                      : "text-red-500"
                  }>
                {data[data.length - 1]?.askPriceAvg.toFixed(2)} ({calculateDifference(data, "askPriceAvg")})
              </p>
            </div>
          ))}
        </div>

        {/* Analytics Section */}
        <div className="w-full px-40 pt-4">
          <div className="w-full bg-gray-100 flex flex-col items-center p-2 rounded-lg drop-shadow-lg">
            <p className="font-semibold text-black">Analytics</p>
          </div>
        </div>

        {/* Chart and WebSocket */}
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

          {/* Reusable Chart */}
          <ChartComponent
            data={displayedData}
            onClick={handleChartClick}
            frozenData={frozenData}
          />
        </div>
      </div>
    </>
  );
}

export default App;
