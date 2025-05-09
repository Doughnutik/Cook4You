import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { isTokenValid } from "../utils/auth";
import { createChat } from "../handlers/createChat";

export default function CreateChatForm({ onChatCreated }) {
  const [title, setTitle] = useState("");
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();

  const handleCreate = async () => {
    if (!title.trim()) return;
    if (!isTokenValid()) {
      localStorage.removeItem("token");
      navigate(`/`);
      return;
    }

    setCreating(true);
    try {
      const newChat = await createChat(title.trim());
      setTitle("");
      onChatCreated(newChat);
    } catch (err) {
      console.error(err);
    } finally {
      setCreating(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleCreate();
    }
  };

  return (
    <div className="flex flex-col gap-2 mb-4">
      <textarea
        placeholder="Название чата (Enter — создать, Shift+Enter — новая строка)"
        className="border px-4 py-2 rounded-xl resize-none whitespace-pre-wrap"
        rows={2}
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={creating}
      />
      <button
        className="bg-green-600 text-white px-4 py-2 rounded-xl self-start"
        onClick={handleCreate}
        disabled={creating}
      >
        Создать
      </button>
    </div>
  );
}