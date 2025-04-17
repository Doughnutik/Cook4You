import asyncio
from logger import logger
from client import client

async def main():
    logger.info("Сервер запущен")
    id = "-"
    while id == "-":
        email = input("Введите email: ")
        password = input("Введите пароль: ")
        id = await client.get_user_id(email, password)
        if len(id) == 0:
            id = await client.new_user(email, password)
        elif id == "-":
            print("Неверный пароль, попробуйте снова")
    
    chats = await client.get_user_chats(id)
    print()
    print(chats)
    print()
    
    chat_id = input("Введите chat_id: ")
    if chat_id == "-":
        title = input("Введите название нового чата: ")
        chat_id = await client.new_chat(id, title)
    while True:
        user_input = input("Ваш вопрос: ")
        if user_input == "exit":
            break
        elif user_input == "image":
            url = await client.ask_question(id, chat_id, '', "image")
            print(f"Ссылка на картинку: {url}")
        else:
            response = await client.ask_question(id, chat_id, user_input, "text")
            print(f"Ответ модели: {response}")

if __name__ == "__main__":
    asyncio.run(main())