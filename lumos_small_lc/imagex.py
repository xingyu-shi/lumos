from lumos_small_lc import prompts
from lumos_small_lc.base import llm_with_vision
from lumos_small_lc.output_parser import remove_think_parse


def describe_image(image_base64) -> str:
    return (llm_with_vision | remove_think_parse).invoke([{
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": prompts.IMAGE_TO_TEXT,
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
    }])


if __name__ == '__main__':
    from lumos_small_lc import samples

    print(describe_image(samples.CAT_IMAGE_BASE64))
