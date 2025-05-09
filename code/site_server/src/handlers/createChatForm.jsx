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
    if (e.key === "Enter") {
      e.preventDefault();
      handleCreate();
    }
  };
  return (
    <div className="flex gap-2 mb-4">
      <input
        type="text"
        placeholder="Название чата"
        className="border px-4 py-2 rounded-xl flex-1"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={creating}
      />
      <button
        className="bg-green-600 text-white px-4 py-2 rounded-xl"
        onClick={handleCreate}
        disabled={creating}
      >
        Создать
      </button>
    </div>
  );
}