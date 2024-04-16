import base64
import os
from pathlib import Path
import mutagen
from mutagen.oggopus import OggOpus
from mutagen.flac import Picture
from PIL import Image

OPTIONS = True

def crop_img_options(img_path):

    options_dir = f'{os.path.dirname(img_path)}\\audio cover options'
    Path(options_dir).mkdir(parents=True, exist_ok=True)

    img = Image.open(img_path)
    
    width, height = img.size
    crop_area = (width - height)
    crop_start = list(range(crop_area + 1))
    crop_start = crop_start[0::20] # every 20px
    for x in crop_start:
        cropped = img.crop((x, 0, height + x, height))
        img_path_cropped = f"{options_dir}\\cropped (offset {x}px).png"
        cropped.save(img_path_cropped)

def main(name):

    audio = mutagen.File(name)

    # date
    date = audio["DATE"]
    date = date[0]
    if '-' not in date:
        date = f'{date[:4]}-{date[4:6]}-{date[6:8]}'
    audio["DATE"] = date
    
    # album and album artist
    audio["ALBUM"] = audio["TITLE"]
    audio["ALBUMARTIST"] = audio["ARTIST"]

    # track number
    audio["TRACK"] = u'01'

    # URL
    audio["ORIGIN WEBSITE"] = audio["PURL"]
    audio.pop('PURL')

    # Delete description
    audio.pop('DESCRIPTION')
    audio.pop('SYNOPSIS')

    # Delete language
    audio.pop('LANGUAGE')

    # misc
    audio["QUALITY"] = u'Medium'
    audio["WWWAUDIOFILE"] = u'YouTube'

    audio["RELEASETYPE"] = u'Single' # Manually change to Playlist \ Album \ EP if you care

    # Picture (only for opus right now)
    if (type(audio) == OggOpus):
        # read image
        b64_data = audio.get("metadata_block_picture")
        data = base64.b64decode(b64_data[0])
        picture = Picture(data)
        img_path = f"{os.path.dirname(name)}/temp_image.png"
        with open(img_path, "wb") as h:
            h.write(picture.data)

        # crop image
        img = Image.open(img_path)

        width, height = img.size
        crop_area = (width-height)/2
        cropped = img.crop((crop_area, 0, height + crop_area, height))
        img_path_cropped = f"{os.path.dirname(img_path)}/temp_image_cropped.png"
        cropped.save(img_path_cropped)

        # add cover options
        if OPTIONS:
            crop_img_options(img_path)

        # embed image
        with open(img_path_cropped, "rb") as h:
            data = h.read()
        picture = Picture()
        picture.data = data
        picture.type = 3  # front cover
        picture.mime = u"image/png"

        audio["metadata_block_picture"] = base64.b64encode(picture.write()).decode('ascii')

        os.remove(img_path_cropped)
        os.remove(img_path)

    audio.save()
