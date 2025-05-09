export async function deleteChat(chatId) {
	const token = localStorage.getItem("token");
	const res = await fetch(`http://localhost:8080/chat/${chatId}`, {
	  method: "DELETE",
	  headers: { Authorization: `Bearer ${token}` },
	});
	if (!res.ok) throw new Error("не удалось удалить чат");
  }