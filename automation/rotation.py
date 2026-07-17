"""
rotation.py — Elige el proximo tema de la lista rotativa y persiste el
indice usado, para que la generacion diaria nunca repita tema hasta
completar la vuelta completa.
"""
import json
from pathlib import Path


def get_next_topic(topics_path: Path, state_path: Path) -> tuple[int, str]:
    topics = json.loads(topics_path.read_text(encoding="utf-8"))

    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        last_index = state.get("last_used_index", -1)
    else:
        last_index = -1

    next_index = (last_index + 1) % len(topics)
    return next_index, topics[next_index]


def save_state(state_path: Path, index: int) -> None:
    state_path.write_text(
        json.dumps({"last_used_index": index}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
