import asyncio
from code.model.model import Conversation

async def main():
    content = "Ты будешь в роли эксперта по готовке. Пользователь будет задавать вопросы касательно приготовления блюд (рецепт блюда, как его готовить, насколько сложно и сколько займёт времени, различные нюансы и уточнения), ты будешь на эти вопросы отвечать"
    conversation = Conversation(content)
    while True:
        user_input = input("User: \n")
        if user_input.lower() == 'exit':
            print("\nGoodbye!")
            break

        await conversation.response(user_input)

if __name__ == "__main__":
    asyncio.run(main())
