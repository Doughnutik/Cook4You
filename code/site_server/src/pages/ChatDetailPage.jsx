import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { isTokenValid } from "../utils/auth";
import {
  fetchChat,
  sendMessage,
  fetchModelAnswerText,
  fetchModelAnswerImage,
} from "../handlers";
import { useAutoScroll } from "../hooks/useAutoScroll";

export default function ChatDetailPage() {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const [chat, setChat] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newMessage, setNewMessage] = useState("");
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const loadChat = async () => {
      if (!isTokenValid()) {
        localStorage.removeItem("token");
        navigate(`/`);
        return;
      }

      const token = localStorage.getItem("token");

      try {
        const data = await fetchChat(chatId, token);
        setChat(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadChat();
  }, [chatId]);

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    if (!isTokenValid()) {
      localStorage.removeItem("token");
      navigate(`/`);
      return;
    }

    setSending(true);
    const token = localStorage.getItem("token");

    try {
      const updatedChat = await sendMessage(chatId, newMessage.trim(), token);
      setChat(updatedChat);
      setNewMessage("");

      const modelAnswer = await fetchModelAnswerText(chatId, token);

      setChat((prev) => ({
        ...prev,
        messages: [...prev.messages, modelAnswer],
      }));
    } catch (error) {
      console.error(error);
    } finally {
      setSending(false);
    }
  };

  const handleShowDish = async () => {
    if (!isTokenValid()) {
      localStorage.removeItem("token");
      navigate(`/`);
      return;
    }

    const token = localStorage.getItem("token");

    try {
      const imageUrl = await fetchModelAnswerImage(chatId, token);
      const updatedChat = {
        ...chat,
        messages: [
          ...chat.messages,
        ],
      };
      setChat(updatedChat);
    } catch (error) {
      console.error("Ошибка при получении изображения:", error);
    }
  };

  useAutoScroll(messagesEndRef, chat?.messages);

  if (loading) return <p>Загрузка...</p>;
  if (!chat) return <p>Чат не найден</p>;

  return (
    <div className="min-h-screen bg-gray-100 p-6 flex flex-col items-center">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-md p-6 flex flex-col flex-grow h-full">
        <div className="overflow-y-auto flex-1 space-y-3 mb-4">
          {chat.messages.slice(1).map((msg, i) => (
            <div key={i} className="max-w-xl w-full border-b pb-2 break-words">
              <div className="font-bold uppercase">{msg.role}</div>
              {msg.type === "image" ? (
                <img
                  src={msg.content}
                  alt="Сгенерированное блюдо"
                  className="rounded-xl mt-2 object-contain"
                  style={{
                    width: `${window.innerWidth}px`,
                    height: `${window.innerHeight}px`,
                  }}
                />
              ) : (
                <div className="whitespace-pre-wrap break-all w-full overflow-hidden text-gray-800">
                  {msg.content}
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="flex space-x-2 mt-auto">
          <textarea
            className="w-full max-w-xl border rounded-xl px-4 py-2 resize-none"
            placeholder="Введите сообщение..."
            rows={2}
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyDown={async (e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                await handleSendMessage();
              }
            }}
          />
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded-xl"
            onClick={handleSendMessage}
            disabled={sending}
          >
            Отправить
          </button>
        </div>
        <button
          className="mt-4 bg-green-500 text-white px-4 py-2 rounded-xl"
          onClick={handleShowDish}
        >
          Показать блюдо
        </button>
      </div>
    </div>
  );
}