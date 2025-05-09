export async function deleteAllChats() {
	const token = localStorage.getItem("token");
	const res = await fetch("http://localhost:8080/chats", {
	  method: "DELETE",
	  headers: { Authorization: `Bearer ${token}` },
	});
	if (!res.ok) throw new Error("не удалось удалить все чаты");
  }