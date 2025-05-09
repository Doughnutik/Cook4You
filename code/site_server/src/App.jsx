// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import {
  AuthPage, 
  ChatListPage, 
  ChatDetailPage 
} from "./pages";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AuthPage />} />
        <Route path="/chats" element={<ChatListPage />} />
        <Route path="/chat/:chatId" element={<ChatDetailPage />} />
      </Routes>
    </Router>
  );
}