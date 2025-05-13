export async function fetchModelAnswerImage(chatId, token) {
  const url = `http://localhost:8080/chat/${chatId}/model-answer-image`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Ошибка при получении изображения: ${response.status}`);
  }

  return await response.json();
}