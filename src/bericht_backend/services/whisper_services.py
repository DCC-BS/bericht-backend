import json
import uuid
from typing import Any

import aiohttp
from fastapi import APIRouter

from bericht_backend.models.response_format import ResponseFormat
from bericht_backend.models.transcription_response import TranscriptionResponse

from ..config import settings

router = APIRouter()

# BentoML API endpoint
BENTOML_API_URL = f"{settings.whisper_api}/audio/transcriptions"


async def speech_to_text(audio_data: bytes) -> TranscriptionResponse:
    """
    Transcribes the given audio data to text.

    Args:
        audio_data: The binary audio data to transcribe
        file_format: The format of the audio data

    """
    url = f"{settings.whisper_api}/audio/transcriptions"

    # Prepare form data
    form_data = aiohttp.FormData()
    form_data.add_field("file", audio_data, filename="audio.wav")

    progress_id = uuid.uuid4().hex
    form_data.add_field("progress_id", progress_id)

    form_data.add_field("response_format", ResponseFormat.JSON)  # Use the enum value

    # Send the request
    async with aiohttp.ClientSession() as session, session.post(url, data=form_data) as response:
        response.raise_for_status()
        transcription = TranscriptionResponse(**await response.json())
        return transcription
