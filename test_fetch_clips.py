from fetch_clips import pick_best_video


def test_prefers_portrait():
    data = {
        "videos": [
            {"video_files": [
                {"file_type": "video/mp4", "width": 1920, "height": 1080, "link": "https://landscape.mp4"},
                {"file_type": "video/mp4", "width": 1080, "height": 1920, "link": "https://portrait.mp4"},
            ]}
        ]
    }
    assert pick_best_video(data) == "https://portrait.mp4"


def test_falls_back_to_largest_landscape():
    data = {
        "videos": [
            {"video_files": [
                {"file_type": "video/mp4", "width": 640, "height": 360, "link": "https://small.mp4"},
                {"file_type": "video/mp4", "width": 1920, "height": 1080, "link": "https://big.mp4"},
            ]}
        ]
    }
    assert pick_best_video(data) == "https://big.mp4"


def test_returns_none_for_no_videos():
    assert pick_best_video({"videos": []}) is None


def test_prefers_closest_to_target_over_huge_file():
    data = {
        "videos": [
            {"video_files": [
                {"file_type": "video/mp4", "width": 2160, "height": 3840, "link": "https://huge_4k.mp4"},
                {"file_type": "video/mp4", "width": 1080, "height": 1920, "link": "https://exact_target.mp4"},
            ]}
        ]
    }
    assert pick_best_video(data) == "https://exact_target.mp4"


if __name__ == "__main__":
    test_prefers_portrait()
    test_falls_back_to_largest_landscape()
    test_returns_none_for_no_videos()
    test_prefers_closest_to_target_over_huge_file()
    print("Todos los tests pasaron.")
