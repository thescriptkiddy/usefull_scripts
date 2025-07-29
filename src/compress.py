import os
from PIL import Image
from src.utils import prepare_web_folder


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
