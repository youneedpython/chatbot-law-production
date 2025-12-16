import ReactDOM from 'react-dom/client'
import { Routes, Route, Navigate, BrowserRouter } from 'react-router-dom'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route path='/chat/:session_id' element={<App />} />
      <Route path='/chat' element={<App />} />
      <Route path='*' element={<Navigate to='/chat' replace />} />
    </Routes>
  </BrowserRouter>,
)
