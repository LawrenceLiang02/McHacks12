import logo from './logo.svg';
import './App.css';
import { DataVisualization } from './components/data_visualization' 
import { CustomWebSocket } from './components/websocket'
import { useState } from 'react';
function App() {
  const [data, setData] = useState([]);

  // Update the data when a new WebSocket message is received
  const updateData = (newData) => {
    setData((prevData) => [
      ...prevData,
      { name: new Date().toLocaleTimeString(), uv: newData.uv, pv: newData.pv },
    ]);
  };
  return (
    <div className="App">
      <header className="App-header">
        <CustomWebSocket updateData={updateData} />
        <DataVisualization data={data} />
      </header>
    </div>
  );
}

export default App;
