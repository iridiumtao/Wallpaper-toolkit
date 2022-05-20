import image_processor
import logging
from pathlib import Path
from PIL import Image

logging.basicConfig(level=logging.INFO)


def image_process(path):
    """
    An example function to manipulate image process functions

    My own flow:
    run_waifu_2x -> crop_image -> image_blur -> image_mix -> image_edgy_blur
    """

    # To test is scaled file exists.
    # if so, skip it
    scaled_path = Path(path).with_stem(Path(path).stem + "_scaled")

    scaled_path__ = Path(scaled_path)
    if not scaled_path__.is_file():
        waifu2x_path = "{YOUR OWN DIRECTORY}"

        scaled_path = image_processor.run_waifu_2x(image_path=path, waifu2x_path=waifu2x_path)
    else:
        logging.info("waifu skipped")

    # maybe something wrong with waifu_2x
    if not scaled_path.is_file():
        logging.error("Scale failed")
        return

    cropped_image = image_processor.crop_image(scaled_path, save=True)
    blurred_image = image_processor.blur_image(image=cropped_image, blur_radius=24)
    foreground = Image.open(scaled_path)
    #foreground = image_processor.blur_image_edge(image=foreground)
    mix = image_processor.mix_image(name=foreground.filename, foreground=foreground, background=blurred_image, save=True)
    image_processor.blur_image_edge(path, mix, save=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    img_path = "{YOUR IMAGE DIRECTORY}"
    image_process(img_path)


