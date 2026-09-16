"""Download and unzip one month of Divvy trip data.

Source: public S3 bucket at https://divvy-tripdata.s3.amazonaws.com
(no authentication required). v1 scope: one hardcoded month; the
month list will later come from comparing the bucket against the
load manifest in Postgres.
"""

from pathlib import Path
import zipfile

import requests

BASE_URL = "https://divvy-tripdata.s3.amazonaws.com"
DATA_DIR = Path("data")


def download_month(yyyymm: str) -> Path:
    """Download one monthly zip into data/ and return its path."""
    filename = f"{yyyymm}-divvy-tripdata.zip"
    url = f"{BASE_URL}/{filename}"
    zip_path = DATA_DIR / filename
    DATA_DIR.mkdir(exist_ok=True)

    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

    return zip_path


def unzip(zip_path: Path) -> list[Path]:
    """Extract the CSV(s) from a monthly zip, skipping macOS junk entries."""
    with zipfile.ZipFile(zip_path) as archive:
        members = [
            name
            for name in archive.namelist()
            if name.endswith(".csv") and not name.startswith("__MACOSX")
        ]
        archive.extractall(DATA_DIR, members=members)
    return [DATA_DIR / name for name in members]


if __name__ == "__main__":
    zip_path = download_month("202608")
    print(f"downloaded {zip_path} ({zip_path.stat().st_size / 1_000_000:.1f} MB)")
    for csv_path in unzip(zip_path):
        print(f"extracted {csv_path}")
