from typing import Tuple


class AudioProcessor:
    def transcribe(self, file_path: str, filename: str) -> Tuple[str, str]:
        import whisper
        from app.config import settings

        model = whisper.load_model(settings.whisper_model)
        result = model.transcribe(file_path)
        transcript = result["text"].strip()

        title = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
        return title, transcript
