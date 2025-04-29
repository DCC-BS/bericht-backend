from pydantic import BaseModel


class GenerateTitleResponse(BaseModel):
    """
    Model for the response of the generate title endpoint.
    """

    title: str
    """
    The generated title.
    """
