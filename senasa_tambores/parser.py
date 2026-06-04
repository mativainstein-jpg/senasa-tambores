from __future__ import annotations

import re
from datetime import datetime

from .models import TamborResult


OWNERSHIP_MESSAGE = "El tambor no le pertenece"
OUTPUT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
BRACKET_STATE_RE = re.compile(r"\[([^\]]+)\]")


def now_text() -> str:
    return datetime.now().strftime(OUTPUT_DATE_FORMAT)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def find_relevant_message(text: str) -> str:
    lines = [normalize_text(line) for line in (text or "").splitlines()]
    lines = [line for line in lines if line]

    for line in lines:
        if OWNERSHIP_MESSAGE.lower() in line.lower():
            return line

    if lines:
        return normalize_text(" | ".join(lines[:8]))

    return ""


def parse_query_text(numero_tambor: str, detected_text: str) -> TamborResult:
    message = find_relevant_message(detected_text)

    if OWNERSHIP_MESSAGE.lower() in message.lower():
        state_match = BRACKET_STATE_RE.search(message)
        return TamborResult(
            numero_tambor=numero_tambor,
            resultado="NO_PERTENECE",
            estado=state_match.group(1).strip() if state_match else "",
            mensaje=message,
            fecha_hora=now_text(),
        )

    return TamborResult(
        numero_tambor=numero_tambor,
        resultado="NO_RECONOCIDO",
        estado="",
        mensaje=message or "No se detecto un mensaje reconocible en pantalla.",
        fecha_hora=now_text(),
    )


def build_error_result(numero_tambor: str, message: str) -> TamborResult:
    return TamborResult(
        numero_tambor=numero_tambor,
        resultado="ERROR",
        estado="",
        mensaje=normalize_text(message),
        fecha_hora=now_text(),
    )
