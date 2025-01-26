import React, { useEffect } from "react";

interface WebSocketComponentProps {
  updateData: (data: any) => void; // Function to pass parsed WebSocket data
}

const WebSocketComponent: React.FC<WebSocketComponentProps> = ({ updateData }) => {
  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:5000/stream");

    ws.onopen = () => {
      console.log("WebSocket connection established");
    };

    ws.onmessage = (event: MessageEvent) => {
      try {
        const parsedData = JSON.parse(event.data);
        updateData(parsedData);
      } catch (error) {
        console.error("Failed to parse message data: ", error);
      }
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };

    ws.onerror = (event: Event) => {
      console.error("WebSocket error: ", event);
    };

    // Cleanup on component unmount
    return () => {
      ws.close();
      console.log("WebSocket connection closed on cleanup");
    };
  }, []); // Dependency array ensures the effect runs only once on mount

  return null; // No UI rendering
};

export default WebSocketComponent;
