from llama_index.core.prompts import PromptTemplate
from llm_facade.llm_facade import LLMFacade


class TitleGenerationService:
    """
    Service for generating titles based on a given text.
    """

    def __init__(self, lmm_facade: LLMFacade):
        """
        Initialize the TitleGenerationService with an OpenAIFacade instance.

        Args:
            openAiFacade (OpenAIFacade): An instance of OpenAIFacade for interacting with the OpenAI API.
        """
        self.llm_facade: LLMFacade = lmm_facade

    def generate_title(self, text: str) -> str:
        """
        Generate a title for the given text.

        Args:
            text (str): The text to generate a title for.

        Returns:
            str: The generated title.
        """

        promt = PromptTemplate("""
            You are a title generation AI.
            - Generate a title and only the title for the given text.
            - Ensure the title is in the same language as the text.
            - The title should be concise and relevant to the content of the text.
            Text: {text}
            """)

        title = self.llm_facade.complete(
            prompt=promt.format(text=text),
        )

        title = title.replace("ß", "ss")  # Replace 'ß' with 'ss' for better readability
        title = title.strip()
        return title
