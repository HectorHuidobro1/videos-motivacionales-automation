import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from youtube_upload import build_snippet


def test_build_snippet_includes_title_description_tags():
    metadata = {
        "topic": "El miedo como músculo",
        "guion": "texto del guion...",
        "title": "El miedo es un músculo",
        "title_alternatives": ["Otra opción de título"],
        "description": "Descripción de prueba con hashtags.",
        "tags": ["motivacion", "mentalidad fuerte"],
    }
    result = build_snippet(metadata)
    assert result["snippet"]["title"] == "El miedo es un músculo"
    assert result["snippet"]["description"] == "Descripción de prueba con hashtags."
    assert result["snippet"]["tags"] == ["motivacion", "mentalidad fuerte"]
    assert result["snippet"]["categoryId"] == "22"
    assert result["status"]["privacyStatus"] == "public"


if __name__ == "__main__":
    test_build_snippet_includes_title_description_tags()
    print("Todos los tests pasaron.")
