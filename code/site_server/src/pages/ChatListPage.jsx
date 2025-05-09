import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { isTokenValid } from "../utils/auth";
import {
  CreateChatForm,
  fetchChats,
  deleteChat,
  deleteAllChats,
} from "../handlers";

export default function ChatListPage() {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      if (!isTokenValid()) {
        localStorage.removeItem("token");
        navigate(`/`);
        return;
      }

      try {
        const data = await fetchChats();
        setChats(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleChatClick = (chatId) => {
    navigate(`/chat/${chatId}`);
  };

  const handleDeleteChat = async (chatId) => {
    if (!isTokenValid()) {
      localStorage.removeItem("token");
      navigate(`/`);
      return;
    }

    try {
      await deleteChat(chatId);
      setChats((prev) => prev.filter((chat) => chat.chat_id !== chatId));
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteAllChats = async () => {
    if (!isTokenValid()) {
      localStorage.removeItem("token");
      navigate(`/`);
      return;
    }

    try {
      await deleteAllChats();
      setChats([]);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-2xl mx-auto bg-white shadow-md rounded-2xl p-6">
        <h1 className="text-2xl font-bold mb-4">Ваши чаты</h1>

        <CreateChatForm
          onChatCreated={(newChat) => {
            setChats((prev) => [newChat, ...prev]);
          }}
        />

        {loading ? (
          <p>Загрузка...</p>
        ) : chats.length === 0 ? (
          <p className="text-gray-600">Чатов пока нет.</p>
        ) : (
          <>
            <ul className="space-y-2 mb-4">
              {chats.map((chat) => (
                <li
                  key={chat.chat_id}
                  className="p-4 rounded-lg border hover:bg-gray-50 transition cursor-pointer flex justify-between items-center"
                >
                  <span
                    className="font-medium"
                    onClick={() => handleChatClick(chat.chat_id)}
                  >
                    {chat.title}
                  </span>
                  <button
                    className="text-red-600 text-sm ml-4"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteChat(chat.chat_id);
                    }}
                  >
                    Удалить
                  </button>
                </li>
              ))}
            </ul>

            <button
              className="bg-red-600 text-white px-4 py-2 rounded-xl text-sm"
              onClick={handleDeleteAllChats}
            >
              Удалить все чаты
            </button>
          </>
        )}
      </div>
    </div>
  );
}