from g4f.client import AsyncClient
from g4f.Provider import RetryProvider, Blackbox, PollinationsAI
from logging import Logger

class Model:
    def __init__(self, chat_model: str, image_model: str, initial_prompt: str, logger: Logger):
        self.client = AsyncClient(provider=RetryProvider([Blackbox, PollinationsAI], shuffle=True))
        self.history = [
            {
                "role": "system",
                "content": f"{initial_prompt}"
            }
        ]
        self.chat_model = chat_model
        self.image_model = image_model
        self.logger = logger
        self.logger.info("Создан новый Async клиент"
                    f"Чат модель: {chat_model}"
                    f"Модель изображений: {image_model}"
                    f"Начальный промпт: {initial_prompt}")
    
    def add_message(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content
        })
        
    async def print_stream_response(self, stream_response) -> str:
        try:
            result = []
            async for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="")
                    result.append(chunk.choices[0].delta.content)
            if len(result) == 0:
                print("Получен пустой ответ. Попробуйте снова")
            else:
                print()
            return ''.join(result)
        except Exception as e:
            self.logger.error(f"print_steam_response: {e}")
            print("Возникла ошибка, попробуйте снова задать вопрос")
            return ""
    
    async def response(self, user_message: str) -> None:
        try:
            stream = self.client.chat.completions.stream(
                model=self.chat_model,
                messages=self.history
            )
            response = await self.print_stream_response(stream)
            if len(response) > 0:
                self.add_message("assistant", response)
        except Exception as e:
            self.logger.error(f"response: {e}")
            print("Возникла ошибка, попробуйте снова задать вопрос")
        
    async def create_image(self, prompt: str) -> str:
        try:
            response = await self.client.images.generate(
                prompt=prompt,
                model=self.image_model,
                response_format="url"
            )
            if response.data:
                image_url = response.data[0].url
                return image_url
            return ""
        except Exception as e:
            self.logger.error(f"create_image: {e}")
            return ""
    
    async def make_prompt_for_image_model(self) -> str:
        try:
            self.add_message("user", "Исходя из моих запросов, сформулируй на английском языке полное описание блюда, которое я хочу сейчас приготовить, чтобы я его отправил генератору изображений в качестве промпта")
            
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=self.history
            )
            
            self.history.pop()
            
            if response.choices:
                prompt = response.choices[0].message.content
                return prompt
            return ""
        except Exception as e:
            self.logger.error(f"make_prompt_for_image_model: {e}")
            return ""
        
    async def image(self) -> str:
        prompt = await self.make_prompt_for_image_model()
        if len(prompt) == 0:
            return ""
        url = await self.create_image(prompt=prompt)
        return url