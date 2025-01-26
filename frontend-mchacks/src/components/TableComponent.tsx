import { Area, AreaChart, CartesianGrid, ReferenceLine, Tooltip, XAxis, YAxis } from "recharts";

export const CustomTooltip = ({
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
        <p className="text-gray-600">Ask Price: {displayedData.askPriceAvg?.toFixed(2) ?? "N/A"}</p>
        <p className="text-gray-600">Bid Price: {displayedData.bidPriceAvg?.toFixed(2) ?? "N/A"}</p>
        <p className="text-gray-600">Ask Volume: {displayedData.askVolumeAvg?.toFixed(2) ?? "N/A"}</p>
        <p className="text-gray-600">Bid Volume: {displayedData.bidVolumeAvg?.toFixed(2) ?? "N/A"}</p>
      </div>
    );
  }

  return null;
};

export const ChartComponent = ({
  data,
  onClick,
  frozenData,
}: {
  data: any[];
  onClick: (e: any) => void;
  frozenData: { label: string; data: any } | null;
}) => {
  const firstAskPrice = data.length > 0 ? data[0].askPriceAvg : null;

  return (
    <AreaChart
      width={window.innerWidth - 70}
      height={450}
      data={data}
      margin={{ top: 10, right: 60, left: 30, bottom: 50 }}
      onClick={onClick}
    >
      <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
      <XAxis dataKey="time" angle={-45} tick={{ fontSize: 16, textAnchor: "end" }} />
      <YAxis domain={["dataMin - 0.05", "dataMax + 0.05"]} tickFormatter={(value) => value.toFixed(2)} />
      <Tooltip
        offset={20}
        content={<CustomTooltip active={!frozenData} frozenData={frozenData} />}
      />
      {firstAskPrice !== null && (
        <ReferenceLine
          y={firstAskPrice}
          stroke="red"
          strokeDasharray="10 3"
          label={{
            value: `Initial Value: ${firstAskPrice.toFixed(4)}`,
            position: "insideLeft",
            fontSize: 12,
            fill: "red",
            dy: -10
          }}
        />
      )}
      <Area type="monotone" dataKey="askPriceAvg" stroke="#8884d8" dot={false} />
    </AreaChart>
  );
};
