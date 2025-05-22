import base64
import io
import os

from PIL import Image

from lumos_small_lc import prompts
from lumos_small_lc.base import llm_with_vision
from lumos_small_lc.output_parser import remove_think_parse


def describe_image(image_base64, meta_data=None) -> str:
    messages = [{
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": prompts.IMAGE_TO_TEXT_SIMPLE,
            },
        ],
    }, {
        "role": "user",
        "content": [
            {
                "type": "image",
                "source_type": "base64",
                "data": image_base64,
                "mime_type": "image/jpeg",
            },
        ],
    }]
    if meta_data:
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"metadata about this image: {meta_data}",
                }
            ]
        })
    return (llm_with_vision | remove_think_parse).invoke(messages)


def local_image_to_base64(image_path):
    """
    Loads an image from the given path and converts it to a Base64 string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The Base64 encoded string of the image, including the data URI prefix,
             or None if the image cannot be loaded.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at '{image_path}'")
        return None

    try:
        # Open the image using Pillow
        with Image.open(image_path) as img:
            # Determine the image format to include in the data URI
            # img.format will be something like 'JPEG', 'PNG', 'GIF'
            image_format = img.format.lower()
            if image_format == 'jpeg':  # Ensure correct MIME type for JPEG
                mime_type = 'image/jpeg'
            elif image_format == 'png':
                mime_type = 'image/png'
            elif image_format == 'gif':
                mime_type = 'image/gif'
            elif image_format == 'bmp':
                mime_type = 'image/bmp'
            elif image_format == 'webp':
                mime_type = 'image/webp'
            else:
                print(f"Warning: Unsupported image format '{img.format}'. Attempting to save as PNG.")
                # Fallback to PNG if format is unknown or unsupported for direct MIME type
                image_format = 'png'
                mime_type = 'image/png'

            # Create an in-memory binary stream
            buffered = io.BytesIO()

            # Save the image into the buffer in the determined format
            img.save(buffered, format=image_format)

            # Get the bytes from the buffer
            img_bytes = buffered.getvalue()

            # Encode the bytes to Base64
            encoded_string = base64.b64encode(img_bytes).decode('utf-8')

            # Construct the data URI
            return encoded_string

    except Exception as e:
        print(f"An error occurred while processing the image: {e}")
        return None


if __name__ == '__main__':
    from lumos_small_lc import samples

    print(describe_image(samples.PIKCLE_IMAGE))
    # print(describe_image(samples.CAT_IMAGE_BASE64))
