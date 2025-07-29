import os
from pathlib import Path
from typing import Iterable, Sequence, Optional
import datetime
import exiftool
from tqdm import tqdm

FOLDER = Path("/Users/simonhardt/Desktop/MGD_Bilder")
# TODO Refactor ALLOWED_EXT -- it should be a filter
ALLOWED_EXT = ["jpg", "jpeg", "JPG"]

FIXED_IMAGE_TAG = "motogymkhana"

# DEFAULT VALUES FOR USER INPUTS
DEFAULT_LOCATION = "ConeCity"
CAPTION_ABSTRACT = ("MotoGymkhana Training des Moto Gymkhana Deutschland e.V., Motorrad-Training, Sicherheitstraining, "
                    "Motorrad, Huetchenspiel und mehr.")
KEYWORDS = ["Motogymkhana", "2025", "Vereinstraining", "Sicherheitstraining", "Motorrad",
            "Motorrad-Training"]
COPYRIGHT = "MotoGymkhana Deutschland e.V."


def prepare_web_folder():
    """Takes care that the web_size folder exists"""
    web_folder_path = os.path.join(FOLDER, "web_size")
    if not os.path.isdir(web_folder_path):
        os.makedirs(web_folder_path)

    return web_folder_path


def get_prefix():
    """Allows the user to enter a date"""
    date = input("Enter the date your pictures were taken (YYYY-MM-DD): ")
    location = input("Enter the location where (Default: ConeCity): ")
    if not date:
        date = datetime.date.today().isoformat()

    if not location:
        location = DEFAULT_LOCATION

    return f"{date}_{location}_{FIXED_IMAGE_TAG}"


def discover_files(folder: Path) -> list[Path]:
    """Returns a list of all files within a folder(path)"""
    files = [entry for entry in Path(folder).iterdir()
             if entry.is_file() and not entry.name.startswith(".")
             ]

    return files


def filter_by_ext(files: Iterable[Path], allowed_ext: Sequence[str] | None) -> list[Path]:
    """Returns a filtered list of files"""
    filtered_files = [file for file in files if allowed_ext is None or
                      file.suffix.lower().lstrip(".") in allowed_ext]

    return filtered_files


def get_valid_files(folder: Path, allowed_ext: Optional[Sequence[str]] = ("jpg", "jpeg")) -> list[dict[str, str]]:
    valid_files = []
    for file in filter_by_ext(discover_files(folder), allowed_ext):
        item = {
            "name": file.stem,
            "ext": file.suffix.lower().lstrip("."),
            "full_path": str(file)
        }
        valid_files.append(item)
    print(valid_files)
    return valid_files


def write_iptc_metadata(mapping_list, overwrite_original=True):
    """
    Writes IPTC metadata to a JPG file.
    - file_path: Path to the image
    - title: Media title (IPTC: ObjectName)
    - description: Description (IPTC: Caption/Abstract)
    - keywords: List of keywords (IPTC: Keywords)
 """
    for file in tqdm(mapping_list, desc="Writing IPTC metadata", unit="image", colour="cyan"):
        if file.get("processed") and file.get("method") == "compress":
            with exiftool.ExifTool() as et:
                tags = {
                    "IPTC:ObjectName": file.get("name").rsplit(".", 1)[0],
                    "IPTC:Caption-Abstract": CAPTION_ABSTRACT,
                    "IPTC:Keywords": KEYWORDS,
                    "IPTC:By-line": COPYRIGHT,
                }

                commands = []
                if overwrite_original:
                    commands.insert(0, "-overwrite_original")
                for key, value in tags.items():
                    if isinstance(value, list):
                        for v in value:
                            commands.append(f"-{key}={v}")
                    else:
                        commands.append(f"-{key}={value}")
                commands.append(file.get("new_full_path"))
                # print(commands)
                et.execute(*commands)
