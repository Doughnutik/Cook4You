// src/utils/auth.js
export function isTokenValid() {
	const token = localStorage.getItem("token");
	if (!token) return false;
  
	try {
	  const payloadBase64 = token.split(".")[1];
	  const payloadJson = atob(payloadBase64);
	  const payload = JSON.parse(payloadJson);
  
	  const currentTime = Math.floor(Date.now() / 1000);
	  return payload.exp && currentTime < payload.exp;
	} catch (err) {
	  console.error("Ошибка при проверке токена:", err);
	  return false;
	}
  }