from g4f.client import AsyncClient
from g4f.Provider import RetryProvider, Blackbox, PollinationsAI

class Model:
    def __init__(self, chat_model: str, image_model: str, 
                 image_generation_prompt: str, logger):
        self.client = AsyncClient(provider=RetryProvider([Blackbox, PollinationsAI], shuffle=True))
        self.image_generation_prompt = image_generation_prompt
        self.chat_model = chat_model
        self.image_model = image_model
        self.logger = logger
        self.logger.info("Создан новый Async клиент модели\n"
                    f"Чат модель: {chat_model}\n"
                    f"Модель изображений: {image_model}\n\n")
    
    async def response(self, history: list[dict]) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=history
            )
            
            if response.choices:
                return response.choices[0].message.content
            
            self.logger.error(f"response: пришёл пустой ответ от провайдера")
            return ""
        except Exception as e:
            self.logger.error(f"response: {e}")
            return ""
        
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
    
    async def make_prompt_for_image_model(self, history: list[dict]) -> str:
        history.append({
            "role": "user",
            "content": self.image_generation_prompt
        })
        
        prompt = ""
        try:
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=history
            )
            if response.choices:
                prompt = response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"make_prompt_for_image_model: {e}")
        finally:
            return prompt
        
    async def image(self, history: list[dict]) -> str:
        prompt = await self.make_prompt_for_image_model(history)
        self.logger.info(f"\nprompt для изображения: {prompt}\n")
        if len(prompt) == 0:
            self.logger.error(f"image: пустой prompt для генерации изображения от провайдера")
            return ""
        url = await self.create_image(prompt=prompt)
        if len(url) == 0:
            self.logger.error(f"image: пустой url изображения от провайдера")
        return url