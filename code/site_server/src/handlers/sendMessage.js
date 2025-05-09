export async function sendMessage(chatId, message, token) {
	const res = await fetch(`http://localhost:8080/chat/${chatId}/add-message`, {
	  method: "POST",
	  headers: {
		"Content-Type": "application/json",
		Authorization: `Bearer ${token}`,
	  },
	  body: JSON.stringify({ content: message }),
	});
  
	if (!res.ok) {
	  throw new Error("ошибка при отправке сообщения");
	}
  
	return res.json();
  }