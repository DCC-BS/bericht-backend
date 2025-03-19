import logging
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, UploadFile, WebSocket, WebSocketDisconnect

from bericht_backend.models.transcription_response import TranscriptionResponse
from bericht_backend.services.whisper_services import speech_to_text

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            # await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")


@app.post("/stt")
async def stt(audio_file: UploadFile) -> TranscriptionResponse:
    """
    Endpoint to submit a transcription task.
    """

    if audio_file.content_type is None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Content type of the audio file is None")

    if audio_file.filename is None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Filename of the audio file is None")

    # Read the uploaded file content
    audio_data = await audio_file.read()

    # Submit the transcription task
    transcription = await speech_to_text(audio_data)
    return transcription


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("bericht_backend:app", host="127.0.0.1", port=8000, reload=True)
