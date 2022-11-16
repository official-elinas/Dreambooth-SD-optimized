'''
---- Credit to jonny#1231 ----
---- Modifications by Elinas#5898 ----
Before running this script on your machine, enter the following command
pip install pillow numpy
'''

import os
import argparse

from PIL import Image, ImageOps, UnidentifiedImageError
import numpy as np
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-in', '--input_dir', type=str, required=True, help='Input directory to all of your images')
parser.add_argument('-out', '--output_dir', type=str, required=True, help='Output directory to save your images')
args = parser.parse_args()

source_image = args.input_dir
destination_image = args.output_dir

processed_dir = os.path.join(source_image, destination_image)
if not os.path.exists(processed_dir):
   os.makedirs(destination_image)

for i in os.listdir(source_image):
    if i == ".DS_Store":
        continue
    img_src = os.path.join(source_image, i)
    dst_src = os.path.join(destination_image, i)
    if os.path.isfile(img_src):
        try:
            image = Image.open(f"{img_src}")
        except UnidentifiedImageError:
            print('Not an image passing...')
            continue
        image = ImageOps.contain(image, (768, 768))

        min_size = (1024, 768) if image.width > image.height else (768, 1024)
        
        for j in range(2):
            position = np.random.uniform(size=2)
            image = ImageOps.pad(image, min_size, color='black', centering=(position[0], position[1]))
            min_size = (1024,1024)
        image.save(f"{dst_src}")
