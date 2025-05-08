// src/pages/ChatListPage.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { isTokenValid } from "../utils/auth";

export default function ChatListPage() {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isTokenValid()) {
      localStorage.removeItem("token");
      navigate(`/`);
      return;
    }

    const token = localStorage.getItem("token");

    fetch("http://localhost:8080/chats", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("не удалось загрузить чаты");
        return res.json();
      })
      .then((data) => {
        setChats(data || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleChatClick = (chatId) => {
    navigate(`/chat/${chatId}`);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-2xl mx-auto bg-white shadow-md rounded-2xl p-6">
        <h1 className="text-2xl font-bold mb-4">Ваши чаты</h1>
        {loading ? (
          <p>Загрузка...</p>
        ) : chats.length === 0 ? (
          <p className="text-gray-600">Чатов пока нет.</p>
        ) : (
          <ul className="space-y-2">
            {chats.map((chat) => (
              <li
                key={chat.chat_id}
                className="p-4 rounded-lg border hover:bg-gray-50 transition cursor-pointer"
                onClick={() => handleChatClick(chat.chat_id)}
              >
                <span className="font-medium">{chat.title}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}