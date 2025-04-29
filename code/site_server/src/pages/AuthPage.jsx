import { useState } from "react";

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const toggleForm = () => setIsLogin(!isLogin);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      alert("введите email и пароль");
      return;
    }

    if (!isLogin && password !== repeatPassword) {
      alert("пароли не совпадают");
      return;
    }

    try {
      const url = isLogin
        ? "http://localhost:8080/login"
        : "http://localhost:8080/register";

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        alert("ошибка: " + data.detail);
      } else {
        alert(isLogin ? "вход выполнен" : "регистрация прошла успешно");
        // здесь можно сохранить токен и перейти на следующий экран
      }
    } catch (err) {
      alert("ошибка запроса: " + err.message);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-100 px-4">
      <div className="w-full max-w-[320px] p-6 bg-white rounded-2xl shadow-xl">
        <h2 className="text-2xl font-bold mb-4 text-center">
          {isLogin ? "Вход" : "Регистрация"}
        </h2>
        <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            className="p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Пароль"
            className="p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {!isLogin && (
            <input
              type="password"
              placeholder="Повторите пароль"
              className="p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={repeatPassword}
              onChange={(e) => setRepeatPassword(e.target.value)}
            />
          )}
          <button
            type="submit"
            className="bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition"
          >
            {isLogin ? "Войти" : "Зарегистрироваться"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600">
          {isLogin ? "Нет аккаунта?" : "Уже есть аккаунт?"}{" "}
          <button onClick={toggleForm} className="text-blue-500 hover:underline">
            {isLogin ? "Зарегистрируйтесь" : "Войдите"}
          </button>
        </p>
      </div>
    </div>
  );
}