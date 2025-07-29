RESIZE = False
RESIZE_WIDTH = 800  # px
RESIZE_HEIGHT = 600  # px
MAX_FILESIZE = 2.0


def calculate_scale_factor():
    """Helper function for resize / compress PNG images"""
    pass


def resize_images_by_pixels(web_folder=prepare_web_folder()):
    """PNG pixel based compression (work in progress)"""
    if web_folder:
        entries = get_valid_files()
        for file in entries:
            full_path = file["full_path"]
            file_size_bytes = os.path.getsize(full_path)
            file_size_mb = file_size_bytes / 1024 / 1024
            print(f"Filename: {file} Filesize: {file_size_mb}")
            size_deviation = float(MAX_FILESIZE - file_size_mb)
            print(f"Deviation: {size_deviation}")
            img = Image.open(full_path)
            width, height = img.size
            print(f"Width: {width} Height: {height}")
    else:
        return False
