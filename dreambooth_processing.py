# Credit to haru#1367

import os
import argparse
import glob
import tqdm
from PIL import Image, ImageOps

# args
parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', type=str, help='Input directory to all of your images')
parser.add_argument('--output_dir', type=str, help='Output directory to save your images')
parser.add_argument('--image_size_max', type=int, default=768, help='Maximum size of the image')
parser.add_argument('--image_size_min', type=int, default=512, help='Minimum size of the image')
parser.add_argument('--image_size_pixels', type=int, default=768*640, help='Maximum pixels in an image')
parser.add_argument('--dreambooth_label', type=str, default=None, required=False, help='Outputs captions to the output_dir that contains the label for each image')
args = parser.parse_args()

aspect_ratios = []

def resize_image(image: Image, max_size=(768,768), max_pixels=768*640, min_size_resize=512, max_size_resize=768) -> Image:
    global aspect_ratios
    image = ImageOps.contain(image, max_size, Image.Resampling.LANCZOS)
    # resize to integer multiple of 64
    w, h = image.size
    w, h = map(lambda x: x - x % 64, (w, h))

    res_dict = {}
    for i in range(max_size_resize+64, min_size_resize, -64):
        res_dict[i] = i - 64

    for _ in range(2):
        if w * h > max_pixels:
            w, h = res_dict[w], res_dict[h]
        else:
            break

    ratio = w / h
    src_ratio = image.width / image.height

    src_w = w if ratio > src_ratio else image.width * h // image.height
    src_h = h if ratio <= src_ratio else image.height * w // image.width

    resized = image.resize((src_w, src_h), resample=Image.Resampling.LANCZOS)
    res = Image.new("RGB", (w, h))
    res.paste(resized, box=(w // 2 - src_w // 2, h // 2 - src_h // 2))

    # use set for aspect ratios to avoid duplicates
    aspect_ratios.append((w, h))
    aspect_ratios = list(set(aspect_ratios))

    return res

# get all images
images = glob.glob(os.path.join(args.input_dir, '*'))
os.makedirs(args.output_dir, exist_ok=True)
for image in tqdm.tqdm(images):
    if image.endswith('.txt'):
        continue
    # open image
    img = Image.open(image)
    # resize image
    img = resize_image(img, max_size=(args.image_size_max, args.image_size_max), max_pixels=args.image_size_pixels, min_size_resize=args.image_size_min, max_size_resize=args.image_size_max)
    # save image
    img.save(os.path.join(args.output_dir, os.path.basename(image)))
    if args.dreambooth_label:
        # caption file path is the same as the image path but with a .txt extension
        caption_dir = os.path.join(args.output_dir, os.path.basename(image).split('.')[0] + '.txt')
        # write caption to file
        with open(caption_dir, 'w') as f:
            f.write(args.dreambooth_label)

print('Done! Here are the output aspect ratios (W, H):')
for aspect_ratio in aspect_ratios:
    print(aspect_ratio)
