from g4f.client import AsyncClient

class Model:
    def __init__(self, content: str):
        self.client = AsyncClient()
        self.history = [
            {
                "role": "system",
                "content": f"{content}"
            }
        ]
    
    def add_message(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content
        })
        
    async def print_stream_response(self, stream_response) -> str:
        result = []
        async for chunk in stream_response:
            if chunk.choices and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="")
                result.append(chunk.choices[0].delta.content)
        print()
        return ''.join(result)
    
    async def response(self, user_message: str) -> None:
        # Add user message to history
        self.add_message("user", user_message)
        
        # Get response from AI
        stream = self.client.chat.completions.stream(
            model="gpt-4o-mini",
            messages=self.history
        )
        
        response = await self.print_stream_response(stream)
        self.add_message("assistant", response)