from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path


NASA_PCOE_URL = (
    "https://www.nasa.gov/intelligent-systems-division/"
    "discovery-and-systems-health/pcoe/pcoe-data-set-repository/"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Download a C-MAPSS archive from a user-supplied URL. "
            "Use the official NASA PCoE page to get the current file link."
        )
    )
    parser.add_argument("--url", required=True, help=f"Current NASA archive URL from {NASA_PCOE_URL}")
    parser.add_argument("--out", default="data/raw/cmaps.zip")
    args = parser.parse_args()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(args.url, out_path)
    print(f"Downloaded {args.url} -> {out_path}")


if __name__ == "__main__":
    main()

