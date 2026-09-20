from pathlib import Path

from utils.json_utils import read_json, write_json


def test_write_and_read_json(tmp_path):
    target = tmp_path / "sample.json"
    payload = {"name": "demo", "values": [1, 2, 3]}

    write_json(target, payload)
    loaded = read_json(target)

    assert loaded == payload
