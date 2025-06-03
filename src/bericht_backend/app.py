from datetime import datetime
from http import HTTPStatus
from typing import Annotated

import truststore
from fastapi import FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from llm_facade.llm_facade import LLMFacade
from llm_facade.qwen3 import QwenVllm

from bericht_backend.config import Configuration
from bericht_backend.models.generate_title_input import GenerateTitleInput
from bericht_backend.models.generate_title_response import GenerateTitleResponse
from bericht_backend.models.log_response import LogEntry, LogResponse
from bericht_backend.models.transcription_response import TranscriptionResponse
from bericht_backend.services.mail_services import send_email
from bericht_backend.services.title_generation_service import TitleGenerationService
from bericht_backend.services.whisper_services import speech_to_text
from bericht_backend.utils.logger import InMemoryLogHandler, get_logger, init_logger

truststore.inject_into_ssl()

init_logger()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(docs_url=None)

config = Configuration.from_env()

print(config)

llm = QwenVllm(config=config, logger=logger)
llm_facade = LLMFacade(llm)

title_generation_service = TitleGenerationService(llm_facade)


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


@app.post("/title")
async def generate_title(request_body: GenerateTitleInput) -> GenerateTitleResponse:
    title = title_generation_service.generate_title(request_body.text)
    return GenerateTitleResponse(title=title)


@app.post("/send")
async def send_mail(
    to_email: Annotated[str, Form()],
    subject: Annotated[str, Form()],
    email_body: Annotated[str, Form()],
    file: UploadFile,
):
    """
    Endpoint to send an email.
    """

    word_attachment = await file.read()

    succcess = send_email(
        to_email=to_email,
        subject=subject,
        body=email_body,
        word_attachment=word_attachment,
        word_filename=file.file.name,
    )

    if not succcess:
        logger.error("Failed to send mail", to_email=to_email, subject=subject)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to send email")

    return {"message": "Email sent successfully"}


@app.get("/logs", response_model=LogResponse)
async def get_logs(
    level: str | None = None,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
    limit: int = 100,
    request_id: str | None = None,
) -> LogResponse:
    """
    Endpoint to retrieve logs with optional filtering.

    Args:
        level: Filter logs by log level (e.g., INFO, WARNING, ERROR)
        from_time: Filter logs from this time (inclusive)
        to_time: Filter logs until this time (inclusive)
        limit: Maximum number of logs to return
        request_id: Filter logs by specific request ID

    Returns:
        A LogResponse containing the filtered logs
    """
    logger.info(
        "Retrieving logs", level=level, from_time=from_time, to_time=to_time, limit=limit, request_id=request_id
    )

    # Get memory handler instance
    memory_handler = InMemoryLogHandler.get_instance()

    # Retrieve filtered logs
    log_entries = memory_handler.get_logs(
        level=level, from_time=from_time, to_time=to_time, limit=limit, request_id=request_id
    )

    # Convert to LogEntry objects for the response
    logs = [
        LogEntry(
            level=entry.get("level", "UNKNOWN"),
            timestamp=entry.get("timestamp", ""),
            message=entry.get("event", str(entry.get("message", ""))),
            module=entry.get("module", None),
            function=entry.get("function", None),
            line_number=entry.get("lineno", None),
            request_id=entry.get("request_id", None),
            extra={
                k: v
                for k, v in entry.items()
                if k not in ["level", "timestamp", "event", "message", "module", "function", "lineno", "request_id"]
            },
        )
        for entry in log_entries
    ]

    return LogResponse(logs=logs, count=len(logs), from_timestamp=from_time, to_timestamp=to_time, level_filter=level)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html>
  <head>
    <link rel="stylesheet" type="text/css" href="/static/swaggerui/swagger-ui.css" />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="/static/swaggerui/swagger-ui-bundle.js"></script>
    <script src="/static/swaggerui/swagger-ui-standalone-preset.js"></script>
    <script>
      const ui = SwaggerUIBundle({
        url: '/openapi.json',
        dom_id: '#swagger-ui',
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
      })
    </script>
  </body>
</html>
        """
    )


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("bericht_backend:app", host="127.0.0.1", port=8000, reload=True)
