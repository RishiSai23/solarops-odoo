import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { DirectorDataProvider } from './context/DirectorDataContext';
import './index.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <DirectorDataProvider>
        <App />
      </DirectorDataProvider>
    </BrowserRouter>
  </React.StrictMode>
);
