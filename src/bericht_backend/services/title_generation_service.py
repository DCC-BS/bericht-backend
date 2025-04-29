

from bericht_backend.services.open_ai_facade import OpenAIFacade


class TitleGenerationService:
    """
    Service for generating titles based on a given text.
    """

    def __init__(self, openAiFacade: OpenAIFacade):
        """
        Initialize the TitleGenerationService with an OpenAIFacade instance.

        Args:
            openAiFacade (OpenAIFacade): An instance of OpenAIFacade for interacting with the OpenAI API.
        """
        self.openAiFacade = openAiFacade

    def generate_title(self, text: str) -> str:
        """
        Generate a title for the given text.

        Args:
            text (str): The text to generate a title for.

        Returns:
            str: The generated title.
        """
        return self.openAiFacade.get_chat_completion(
            instructions="""
            You are a title generation AI.
            - Generate a title and only the title for the given text.
            - Ensure the title is in the same language as the text.
            - The title should be concise and relevant to the content of the text.
            """,
            prompt=f"Text: {text}\nTitle:",
        )