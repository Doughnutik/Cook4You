export async function fetchChat(chatId, token) {
	const res = await fetch(`http://localhost:8080/chat/${chatId}`, {
	  headers: { Authorization: `Bearer ${token}` },
	});
  
	if (!res.ok) {
	  throw new Error("не удалось загрузить чат");
	}
  
	return res.json();
  }