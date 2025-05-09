export async function fetchChats() {
	const token = localStorage.getItem("token");
	const res = await fetch("http://localhost:8080/chats", {
	  headers: { Authorization: `Bearer ${token}` },
	});
	if (!res.ok) throw new Error("не удалось загрузить чаты");
	return await res.json();
  }