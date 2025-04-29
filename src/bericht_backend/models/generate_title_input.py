from pydantic import BaseModel


class GenerateTitleInput(BaseModel):
    """Input model for generating a title."""

    text: str
