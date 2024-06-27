from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile


def process_image(image, new_format='PNG', size=(200, 200)):
    """Function for resizing and processing immages."""

    img = Image.open(image)

    img = img.resize(size, Image.Resampling.LANCZOS)

    filename = f"{os.path.splitext(image.name)[0]}.{new_format.lower()}"

    img_io = BytesIO()
    img.save(img_io, format=new_format)
    img_io.seek(0)

    return ContentFile(img_io.read(), name=filename)
