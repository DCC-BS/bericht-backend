from openai import OpenAI

from bericht_backend.config import settings


class OpenAIFacade:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_api,
        )

    def get_chat_completion(self, instructions: str, prompt: str, instruction_user: str = "system") -> str:
        completion = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {
                    "role": instruction_user,
                    "content": instructions,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return completion.choices[0].message.content
