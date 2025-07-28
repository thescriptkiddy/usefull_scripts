import os
from pathlib import Path
from typing import Iterable, Sequence, Optional
import uuid
import datetime
from pprint import pprint
import exiftool
from PIL import Image
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


def rename_files():
    prefix = get_prefix()
    valid_files = get_valid_files(FOLDER)
    renamed_files = []

    for file in valid_files:
        original_full_path = file.get("full_path")
        full_path = file.get("full_path")
        ext = file.get("ext")
        new_name = f"{prefix}_{uuid.uuid4()}.{ext}"
        new_full_path = os.path.join(FOLDER, new_name)
        os.rename(full_path, new_full_path)
        new_dict = {
            "name": new_name,
            "ext": ext,
            "full_path": new_full_path,
            "original_full_path": original_full_path
        }
        renamed_files.append(new_dict)
    return renamed_files


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


def compress_image(file):
    try:
        image = Image.open(file["full_path"])
        new_full_path = os.path.join(prepare_web_folder(), file["name"])
        # print(f"Saved compressed image: {new_full_path}")

        image.save(new_full_path,
                   quality=75,
                   optimize=True,
                   progressive=True
                   )
        return True, None, new_full_path

    except Exception as e:
        return False, str(e)


def optimize_for_web():
    """Prepares images for web upload (includes renaming and compression)"""
    mapping_list = []

    if not prepare_web_folder():
        print("Web folder could not be created")
        return
    renamed_files = rename_files()
    if not renamed_files:
        print("No files available")
        return

    compressed_count = 0
    failed_count = 0
    skipped_count = 0
    for file in tqdm(renamed_files, desc="Compressing images", unit="file", colour="green", leave=True):
        if file["ext"].lower() in ("jpg", "jpeg"):
            success, error, new_full_path = compress_image(file)
            if success:
                mapping_list_entry = {
                    "name": file["name"],
                    "ext": file["ext"],
                    "original_full_path": file["original_full_path"],
                    "new_full_path": new_full_path,
                    "processed": True,
                    "method": "compress",
                    "error": None
                }

                mapping_list.append(mapping_list_entry)
                compressed_count += 1

            else:
                mapping_list_entry = {
                    "name": file["name"],
                    "ext": file["ext"],
                    "original_full_path": file["original_full_path"],
                    "new_full_path": new_full_path,
                    "processed": False,
                    "method": "compress",
                    "error": error
                }
                mapping_list.append(mapping_list_entry)
                failed_count += 1
        else:
            mapping_list_entry = {
                "name": file["name"],
                "ext": file["ext"],
                "original_full_path": file["original_full_path"],
                "new_full_path": file["full_path"],
                "processed": False,
                "method": "skipped",
                "error": "Unsupported file type"
            }
            mapping_list.append(mapping_list_entry)
            skipped_count += 1

    write_iptc_metadata(mapping_list)

    # print(f"{compressed_count} Images compressed ✅ ",
    #       f"{failed_count} Files failed ❌",
    #       f"{skipped_count} Skipped files ⚠️",
    #       sep="\n"
    #       )


# Orchestrator
# optimize_for_web()
