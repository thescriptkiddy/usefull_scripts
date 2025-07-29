from tqdm import tqdm
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Any, Tuple, Optional, Dict
from src.compress import compress_image
from src.rename_files import rename_files
from src.utils import prepare_web_folder, write_iptc_metadata


# NOT IN USE RIGHT NOW. It is here for learning purposes only.
@dataclass
class Pipeline:
    source: Path
    output_dir: Path
    rename: Callable[[], List[Dict[str, Any]]] = rename_files
    compress: Callable[[Dict[str, Any]], Tuple[bool, Optional[str], str]] = compress_image
    write_metadata: Callable[[str], None] = write_iptc_metadata

    def run(self):
        for item in self.rename():
            ok, err, path = self.compress(item)
            if not ok:
                continue  # or log err
            self.write_metadata(path)


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
