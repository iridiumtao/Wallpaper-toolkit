import subprocess

from PIL import Image, ImageFilter
import math
import logging
from pathlib import Path


def blur_image_edge(path: str = None,
                    image: Image = None,
                    color=(255, 255, 255),
                    save: bool = False):
    """
    Source <https://gist.github.com/namieluss/2a57539df54158e0c1575903a988bbb2>

    :param color: What color to use for the edge.  Default is white.
       If given, this should be a single integer or floating point value
       for single-band modes, and a tuple for multi-band modes (one value
       per band).  When creating RGB images, you can also use color
       strings as supported by the ImageColor module.  If the color is
       None, the image is not initialised.
    """

    # blur radius and diameter
    radius, diameter = 20, 40

    if image is None:
        # open an image
        img = Image.open(path)
    else:
        img = image

    # Paste image on white background
    background_size = (img.size[0] + diameter, img.size[1] + diameter)
    background = Image.new('RGB', background_size, color)
    background.paste(img, (radius, radius))

    # create new images with white and black
    mask_size = (img.size[0] + diameter, img.size[1] + diameter)
    mask = Image.new('L', mask_size, 255)

    black_size = (img.size[0] - diameter, img.size[1] - diameter)
    black = Image.new('L', black_size, 0)

    # create blur mask
    mask.paste(black, (diameter, diameter))

    # Blur image and paste blurred edge according to mask
    blur = background.filter(ImageFilter.GaussianBlur(radius / 2))
    background.paste(blur, mask=mask)

    if isinstance(image.filename, str):
        name = image.filename
    else:
        name = path

    if save:
        background.save(Path(name).with_stem(Path(name).stem + "_edgy_blurred"), quality=100)

    background.filename = Path(name).with_stem(Path(name).stem + "_edgy_blurred")
    logging.info(background.filename)
    return background


def blur_image(path: str = None, image: Image = None, blur_radius: int = 16, save: bool = False):
    """Blur the image"""

    if image is None:
        original_image = Image.open(path)
    else:
        original_image = image
    blurred_image = original_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    if image.filename is not None:
        name = image.filename
    else:
        name = path

    if save:
        blurred_image.save(Path(name).with_stem(Path(name).stem + "_blurred"), quality=100)

    blurred_image.filename = Path(name).with_stem(Path(name).stem + "_blurred")
    logging.info(blurred_image.filename)
    return blurred_image


def crop_image(path: str = None, image: Image = None, save: bool = False):
    """crop image into 16:9 ratio"""

    logging.info("cropping image")

    if image is None:
        # open an image
        image = Image.open(path)
    else:
        image = image

    if image.filename is not None:
        name = image.filename
    else:
        name = path

    width, height = image.size
    ratio = width / height

    # ratio from 1.76 to 1.78 are acceptable
    if math.isclose(ratio, 1.77, rel_tol=1e-3):
        return image

    if ratio > 1.77:
        wk = height * 1.77
        offset = (width - wk) / 2
        print("ratio > 1.77")
        # (left, upper, right, lower)
        image = image.crop((int(offset), 0, width - int(offset), height))
    else:
        hk = width / 1.77
        print("ratio <= 1.77")
        image = image.crop((0, int((height - hk) / 2), width, height - int((height - hk) / 2)))

    if save:
        image.save(Path(name).with_stem(Path(name).stem + "_cropped"), quality=100)

    image.filename = Path(name).with_stem(Path(name).stem + "_cropped")
    logging.info(image.filename)
    return image


def mix_image(name: str, foreground: Image, background: Image, save: bool = False):
    """
    Mixing image with background image and foreground image.
    Background image has to be bigger than the foreground
    """
    ratio = foreground.width / foreground.height
    if ratio > 1.77:
        h = foreground.height // (foreground.width / background.width)
        foreground = foreground.resize((background.width, int(h)))
        offset = (background.height - foreground.height) // 2
        background.paste(foreground, (0, offset))
    else:
        w = foreground.width // (foreground.height / background.height)
        foreground = foreground.resize((int(w), background.height))
        offset = (background.width - foreground.width) // 2
        background.paste(foreground, (offset, 0))
    logging.info(f"image_mix: offset = {offset}")
    if save:
        background.save(Path(name).with_name(Path(name).stem + "_mixed.png"), quality=100)
    background.filename = Path(name).with_name(Path(name).stem + "_mixed.png")
    logging.info(background.filename)
    return background


def run_waifu_2x(image_path, waifu2x_path, scale_size: int = None):
    """
    Run waifu_2x with waifu2x-ncnn-vulkan.
    link <https://github.com/nihui/waifu2x-ncnn-vulkan>

    :param waifu2x_path:  Path to your waifu_2x
    :param image_path:
    :param scale_size: upscale ratio for waifu_2x
    (1/2/4/8/16/32, default: do a calculation to make image larger than 4K(3840x2160))
    :type scale_size: int
    :return: Path for the output image
    :rtype: str
    """
    print(str(Path(__file__).parent) + "/" + image_path)

    if scale_size is None:
        scale_size = calculate_scale_level(image_path)

    abs_path = str(Path(__file__).parent) + "/" + image_path
    subprocess.call([waifu2x_path,
                     "-i",
                     abs_path,
                     "-o",
                     Path(abs_path).with_stem(Path(abs_path).stem + "_scaled"),
                     "-s",
                     str(scale_size),
                     "-g",
                     "0"])
    return Path(image_path).with_stem(Path(image_path).stem + "_scaled")


def calculate_scale_level(path):
    image = Image.open(path)
    width, height = image.size
    scale_width = 3840 / width
    scale_height = 2160 / height
    scale_raw = max(scale_height, scale_width)
    scale_size = int(math.pow(2, math.ceil(math.log(scale_raw, 2))))
    logging.info(f"scale level {scale_size}")
    return scale_size
