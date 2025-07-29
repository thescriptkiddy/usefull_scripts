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


# Orchestrator
optimize_for_web()
