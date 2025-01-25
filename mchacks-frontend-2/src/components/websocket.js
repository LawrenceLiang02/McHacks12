import React, { useState, useEffect } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

export const CustomWebSocket = ({ updateData }) => {
  const [socketUrl] = useState('ws://127.0.0.1:5000/stream');
  const { lastMessage, readyState } = useWebSocket(socketUrl, {
    onOpen: () => console.log('Connected'),
    onClose: () => console.log('Disconnected'),
    shouldReconnect: () => false,  // Disable auto-reconnect
    onMessage: (message) => updateData(JSON.parse(message.data)), // Directly handle messages
  });
};
