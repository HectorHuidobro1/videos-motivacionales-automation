import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rotation import get_next_topic, save_state


def test_first_run_picks_index_zero():
    with tempfile.TemporaryDirectory() as d:
        topics_path = Path(d) / "topics.json"
        state_path = Path(d) / "state.json"
        topics_path.write_text(json.dumps(["A", "B", "C"]), encoding="utf-8")
        index, topic = get_next_topic(topics_path, state_path)
        assert index == 0
        assert topic == "A"


def test_advances_to_next_index():
    with tempfile.TemporaryDirectory() as d:
        topics_path = Path(d) / "topics.json"
        state_path = Path(d) / "state.json"
        topics_path.write_text(json.dumps(["A", "B", "C"]), encoding="utf-8")
        save_state(state_path, 0)
        index, topic = get_next_topic(topics_path, state_path)
        assert index == 1
        assert topic == "B"


def test_wraps_around_at_end_of_list():
    with tempfile.TemporaryDirectory() as d:
        topics_path = Path(d) / "topics.json"
        state_path = Path(d) / "state.json"
        topics_path.write_text(json.dumps(["A", "B", "C"]), encoding="utf-8")
        save_state(state_path, 2)
        index, topic = get_next_topic(topics_path, state_path)
        assert index == 0
        assert topic == "A"


def test_missing_state_file_behaves_like_first_run():
    with tempfile.TemporaryDirectory() as d:
        topics_path = Path(d) / "topics.json"
        state_path = Path(d) / "state_does_not_exist.json"
        topics_path.write_text(json.dumps(["A", "B"]), encoding="utf-8")
        index, topic = get_next_topic(topics_path, state_path)
        assert index == 0
        assert topic == "A"


if __name__ == "__main__":
    test_first_run_picks_index_zero()
    test_advances_to_next_index()
    test_wraps_around_at_end_of_list()
    test_missing_state_file_behaves_like_first_run()
    print("Todos los tests pasaron.")
