from g4f.client import AsyncClient
from g4f.Provider import RetryProvider, Blackbox, PollinationsAI
from logging import Logger

RESPONSE_ERROR = "Ошибка получение ответа модели"
IMAGE_ERROR = "Ошибка генерации изображения"

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
        self.logger.info("Создан новый Async клиент\n"
                    f"Чат модель: {chat_model}\n"
                    f"Модель изображений: {image_model}\n"
                    f"Начальный промпт: {initial_prompt}\n")
    
    def add_message(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content
        })
        
    async def print_stream_response(self, stream_response) -> str:
        result = []
        try:
            async for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="")
                    result.append(chunk.choices[0].delta.content)
            if len(result) > 0:
                print()
        except Exception as e:
            self.logger.error(f"print_steam_response: {e}")
            result = []
        finally:
            return ''.join(result)
    
    async def response(self, user_message: str) -> None:
        self.add_message("user", user_message)
        try:
            stream = self.client.chat.completions.stream(
                model=self.chat_model,
                messages=self.history
            )
            response = await self.print_stream_response(stream)
            if len(response) > 0:
                self.add_message("assistant", response)
            else:
                print(RESPONSE_ERROR)
        except Exception as e:
            self.logger.error(f"response: {e}")
            print(RESPONSE_ERROR)
            self.history.pop()
        
    async def create_image(self, prompt: str) -> str:
        image_url = ""
        try:
            response = await self.client.images.generate(
                prompt=prompt,
                model=self.image_model,
                response_format="url"
            )
            if response.data:
                image_url = response.data[0].url
        except Exception as e:
            self.logger.error(f"create_image: {e}")
        finally:
            return image_url
    
    async def make_prompt_for_image_model(self) -> str:
        self.add_message("user", "Исходя из моих запросов, сформулируй на английском языке полное описание блюда, которое я хочу сейчас приготовить, учитывая тот рецепт, который ты мне написал. Я его отправлю генератору изображений. Очень важно, чтобы описание соответствовало твоему рецепту влоть до мелочей, иначе изображение не будет описывать ожидаемое блюдо! Не нужно никаких лишний слов и комментариев, только промпт для генератора изображений")
        
        prompt = ""
        try:
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=self.history
            )
            if response.choices:
                prompt = response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"make_prompt_for_image_model: {e}")
        finally:
            self.history.pop()
            return prompt
        
    async def image(self) -> str:
        prompt = await self.make_prompt_for_image_model()
        self.logger.info(f"Prompt для изображения: {prompt}")
        if len(prompt) == 0:
            print(IMAGE_ERROR)
            return ""
        url = await self.create_image(prompt=prompt)
        if len(url) == 0:
            print(IMAGE_ERROR)
        return url