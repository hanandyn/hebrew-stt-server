"""
Hebrew STT Server - ivrit.ai Whisper via faster-whisper
OpenAI-compatible /v1/audio/transcriptions endpoint
"""
import io
import tempfile
import logging
from pathlib import Path

from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("hebrew-stt")

app = Flask(__name__)

_model = None

MODEL_ID = "ivrit-ai/whisper-large-v3-turbo-ct2"


def get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        log.info(f"Loading model: {MODEL_ID}")
        _model = WhisperModel(
            MODEL_ID,
            device="cpu",
            compute_type="int8",
            cpu_threads=4,
            num_workers=1,
        )
        log.info("Model loaded")
    return _model


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": MODEL_ID, "language": "he"})


@app.route("/v1/audio/transcriptions", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["file"]
    language = request.form.get("language", "he")
    response_format = request.form.get("response_format", "json")

    # Save to temp file (faster-whisper needs a path)
    suffix = Path(audio_file.filename).suffix if audio_file.filename else ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        audio_file.save(tmp)
        tmp_path = tmp.name

    try:
        model = get_model()
        segments, info = model.transcribe(
            tmp_path,
            language=language,
            beam_size=5,
            vad_filter=True,
        )

        text = " ".join(seg.text.strip() for seg in segments)

        log.info(
            f"Transcribed {info.duration:.1f}s audio → {len(text)} chars "
            f"(lang: {info.language}, prob: {info.language_probability:.2f})"
        )

        if response_format == "text":
            return text, 200, {"Content-Type": "text/plain; charset=utf-8"}

        return jsonify({"text": text})

    except Exception as e:
        log.exception("Transcription failed")
        return jsonify({"error": str(e)}), 500
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    log.info("Starting Hebrew STT server on port 8881")
    get_model()
    log.info("Ready.")
    app.run(host="0.0.0.0", port=8881)
