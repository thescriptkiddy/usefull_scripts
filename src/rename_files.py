import os
import uuid
from src.utils import get_prefix, get_valid_files, FOLDER


def rename_files():
    """Renames files based on a prefix"""
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
