import logo from './logo.svg';
import './App.css';
import { DataVisualization } from './components/data_visualization' 
import { CustomWebSocket } from './components/websocket'
import { useState } from 'react';
function App() {
  const [data, setData] = useState([]);

  const companyNames = ["A", "B", "C", "D", "E"];
  const updateData = (newData) => {
    setData((prevData) => [
      ...prevData,
      { 
        time: new Date(newData.timestamp).toLocaleTimeString(),  // Use the timestamp from the new data
        askPriceAvg: newData.askPriceAvg,  // Use the actualPriceAvg from the new data
      },
    ]);
  };

  return (
    <div className="App">
      <header className="App-header">
        <CustomWebSocket updateData={updateData} />
        <div className="grid-container">
          {companyNames.map((company, index) => (
            <div key={index} className="grid-item">
              <h3 >Graph for Company {company}</h3>
              <DataVisualization height={500} width={300} data={data} companyName={company} />
            </div>
          ))}
        </div>
        
      </header>
    </div>
  );
}

export default App;
