"""CUBE TO XMP desktop entry point and packaged-resource self-check."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

from web_studio import ROOT, StudioBridge, main


def self_test():
    with TemporaryDirectory() as directory:
        bridge = StudioBridge(ROOT, Path(directory) / "library")
        state = bridge.state()
        assert state["ok"] and len(state["data"]["items"]) >= 6
        item_id = state["data"]["items"][0]["id"]
        selected = bridge.select(item_id)
        assert selected["ok"] and selected["data"]["document"]["target"] == "XMP"
    print("CUBE TO XMP resource self-test passed")

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        main()
