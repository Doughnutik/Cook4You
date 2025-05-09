export async function createChat(title) {
	const token = localStorage.getItem("token");
	const res = await fetch("http://localhost:8080/chat", {
	  method: "POST",
	  headers: {
		"Content-Type": "application/json",
		Authorization: `Bearer ${token}`,
	  },
	  body: JSON.stringify({ title }),
	});
	if (!res.ok) throw new Error("не удалось создать чат");
	return await res.json();
  }