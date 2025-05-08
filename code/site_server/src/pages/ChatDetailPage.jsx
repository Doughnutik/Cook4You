// src/pages/ChatDetailPage.jsx
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { isTokenValid } from "../utils/auth";

export default function ChatDetailPage() {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const [chat, setChat] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isTokenValid()) {
      localStorage.removeItem("token");
      navigate(`/`);
      return;
    }

    const token = localStorage.getItem("token");

    fetch(`http://localhost:8080/chat/${chatId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("не удалось загрузить чат");
        return res.json();
      })
      .then((data) => {
        setChat(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [chatId]);

  if (loading) return <p>Загрузка...</p>;
  if (!chat) return <p>Чат не найден</p>;

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-2xl mx-auto bg-white shadow-md rounded-2xl p-6">
        <h1 className="text-2xl font-bold mb-4">{chat.title}</h1>
        <div className="space-y-2">
          {chat.messages.length === 0 ? (
            <p className="text-gray-600">В чате нет сообщений</p>
          ) : (
            chat.messages.slice(1).map((msg, i) => (
              <div key={i} className="border-b pb-2">
                <div className="font-semibold">{msg.role}</div>
                <div>{msg.content}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}