// src/App.jsx
import { useState } from "react";
import AuthPage from "./pages/AuthPage";
import ChatListPage from "./pages/ChatListPage";

function App() {
  const [token] = useState(localStorage.getItem("token"));

  return token ? <ChatListPage /> : <AuthPage />;
}

export default App;