"""Speech-to-text with word-level timestamps (Hebrew + English).

Backends
  faster-whisper : local Whisper (CTranslate2). Hebrew uses ivrit-ai's fine-tuned model by default.
  sidecar        : read <video>.words.json or <video>.srt sitting next to the raw file.
  none           : no transcript — the pipeline falls back to audio-energy cutting, no captions.

Transcript format (transcript.json):
  {"language": "he", "words": [{"w": "שלום", "s": 0.52, "e": 0.91, "p": 0.98}, ...],
   "sentences": [{"s": 0.52, "e": 3.1, "text": "...", "i0": 0, "i1": 7}, ...]}
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from .media import run

log = logging.getLogger("factory")

HEBREW_RE = re.compile(r"[֐-׿]")
SENTENCE_END = re.compile(r"[.!?…]$|[.!?]\"?$")


def is_hebrew(text: str) -> bool:
    return bool(HEBREW_RE.search(text))


# ---------------------------------------------------------------------------
def build_sentences(words: list[dict], max_gap: float = 0.7, max_words: int = 30) -> list[dict]:
    """Group words into sentences using punctuation and pauses."""
    sents, start = [], 0
    for i, w in enumerate(words):
        last = i == len(words) - 1
        gap = (words[i + 1]["s"] - w["e"]) if not last else 0
        if last or SENTENCE_END.search(w["w"]) or gap > max_gap or (i - start + 1) >= max_words:
            chunk = words[start:i + 1]
            sents.append({"s": chunk[0]["s"], "e": chunk[-1]["e"], "i0": start, "i1": i + 1,
                          "text": " ".join(x["w"] for x in chunk)})
            start = i + 1
    return sents


def _norm_words(words: list[dict]) -> list[dict]:
    out = []
    for w in words:
        t = str(w.get("w", "")).strip()
        if not t:
            continue
        s, e = float(w["s"]), float(w["e"])
        if e <= s:
            e = s + 0.08
        out.append({"w": t, "s": round(s, 3), "e": round(e, 3), "p": round(float(w.get("p", 1.0)), 3)})
    out.sort(key=lambda x: x["s"])
    return out


def finalize(words: list[dict], language: str) -> dict:
    words = _norm_words(words)
    if language in (None, "", "auto"):
        language = "he" if any(is_hebrew(w["w"]) for w in words[:50]) else "en"
    return {"language": language, "words": words, "sentences": build_sentences(words)}


# ---------------------------------------------------------------------------
def _srt_time(t: str) -> float:
    h, m, rest = t.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


def words_from_srt(path: Path) -> list[dict]:
    """SRT has only cue-level timing: distribute cue time over words by character length."""
    text = Path(path).read_text(encoding="utf-8-sig")
    words = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [l for l in block.splitlines() if l.strip()]
        tl = next((l for l in lines if "-->" in l), None)
        if not tl:
            continue
        a, b = [x.strip().split(" ")[0] for x in tl.split("-->")]
        s, e = _srt_time(a), _srt_time(b)
        body = " ".join(lines[lines.index(tl) + 1:])
        body = re.sub(r"<[^>]+>|\{[^}]+\}", "", body)
        toks = body.split()
        if not toks:
            continue
        total = sum(len(t) + 1 for t in toks)
        cur = s
        for t in toks:
            d = (e - s) * (len(t) + 1) / total
            words.append({"w": t, "s": cur, "e": cur + d * 0.92})
            cur += d
    return words


def load_sidecar(raw: Path) -> dict | None:
    wj = raw.with_suffix(".words.json")
    srt = raw.with_suffix(".srt")
    if wj.exists():
        data = json.loads(wj.read_text(encoding="utf-8"))
        words = data["words"] if isinstance(data, dict) else data
        lang = data.get("language", "auto") if isinstance(data, dict) else "auto"
        log.info("Using sidecar transcript %s", wj.name)
        return finalize(words, lang)
    if srt.exists():
        log.info("Using sidecar subtitles %s (word timing interpolated)", srt.name)
        return finalize(words_from_srt(srt), "auto")
    return None


# ---------------------------------------------------------------------------
def _device(cfg: dict) -> tuple[str, str]:
    dev = cfg["device"]
    if dev == "auto":
        try:
            import ctranslate2
            dev = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
        except Exception:
            dev = "cpu"
    ct = cfg["compute_type"]
    if ct == "auto":
        ct = "float16" if dev == "cuda" else "int8"
    return dev, ct


def _load_model(name: str, tcfg: dict, models_dir: Path):
    from faster_whisper import WhisperModel
    dev, ct = _device(tcfg)
    local = models_dir / name.replace("/", "__")
    src = str(local) if local.exists() else name
    log.info("Loading Whisper model %s on %s/%s", src, dev, ct)
    return WhisperModel(src, device=dev, compute_type=ct, download_root=str(models_dir))


def transcribe_whisper(audio: Path, tcfg: dict, models_dir: Path) -> dict:
    lang = tcfg["language"]
    if lang == "auto":
        det = _load_model(tcfg["models"]["detect"], tcfg, models_dir)
        _, info = det.transcribe(str(audio), beam_size=1, language=None, without_timestamps=True)
        lang = info.language if info.language in ("he", "en") else ("he" if info.language == "iw" else "en")
        log.info("Detected language: %s (p=%.2f)", lang, info.language_probability)
        del det
    model = _load_model(tcfg["models"].get(lang, tcfg["models"]["en"]), tcfg, models_dir)
    segments, _ = model.transcribe(str(audio), language=lang, beam_size=tcfg["beam_size"],
                                   word_timestamps=True, vad_filter=tcfg["vad_filter"],
                                   condition_on_previous_text=False)
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"w": w.word.strip(), "s": w.start, "e": w.end, "p": w.probability})
    return finalize(words, lang)


def transcribe(raw: Path, audio: Path, cfg: dict, models_dir: Path) -> dict | None:
    tcfg = cfg["transcription"]
    if tcfg.get("use_sidecars", True):
        side = load_sidecar(raw)
        if side:
            return side
    backend = tcfg["backend"]
    if backend == "none" or backend == "sidecar":
        log.warning("No transcript available (backend=%s) — energy-based cutting, no captions.", backend)
        return None
    try:
        return transcribe_whisper(audio, tcfg, models_dir)
    except ImportError:
        log.error("faster-whisper is not installed — run scripts/install.sh. Continuing without transcript.")
    except Exception as exc:  # model download blocked, OOM, ...
        log.error("Transcription failed (%s). Continuing without transcript.", exc)
    return None


def extract_audio(src: Path, dst: Path) -> Path:
    run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-loglevel", "error", "-i", str(src),
         "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(dst)])
    return dst
