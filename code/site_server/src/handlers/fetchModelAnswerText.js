export async function fetchModelAnswerText(chatId, token) {
  const url = `http://localhost:8080/chat/${chatId}/model-answer-text`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Ошибка при получении ответа модели: ${response.status}`);
  }

  return await response.json();
}