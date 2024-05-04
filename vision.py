import base64
import json
import os
from typing import List
import uuid
from io import BytesIO

import anthropic 
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
vision_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model_version = "claude-3-opus-20240229"
correction_model_version = "claude-3-haiku-20240307"
image_media_type = "image/jpeg"
IMG_RES = 1080


# Function to encode the image
def encode_and_resize(image):
    W, H = image.size
    image = image.resize((IMG_RES, int(IMG_RES * H / W)))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    image.save(f"test/{uuid.uuid4()}.png", format="JPEG")
    encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return encoded_image


def get_actions(screenshot, objective, hint_markers, actions_history: List[str]):
    encoded_screenshot = encode_and_resize(screenshot)
    response = vision_client.messages.create(
        model=model_version,
        max_tokens=128,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"You need to choose which action to take to help a user do this task: {objective}. Your options are type, click, scroll_up, scroll_down and done. Type and click take strings where if you want to click on an object, return the string with the yellow character sequence you want to click on, and to type just a string with the message you want to type. For clicks, please only respond with the 1-2 letter sequence in the yellow box, and if there are multiple valid options choose the one you think a user would select. For typing, please return a click to click on the box along with a type with the message to write. When the page seems satisfactory, return done as a key with no value. If you the relevant content is not displayed on the screen, scroll further. You must respond in JSON only with no other fluff or bad things will happen. The JSON keys must ONLY be one of scroll_up, scroll_down, type, or click. Do not return the JSON inside a code block. If you want to click and type, return {{\"click\": \"letter\", \"type\": {{ \"content\" }}. Attached here is a list of the descriptions of the elements shown on the screen: {hint_markers}. Here are the past actions, {actions_history}, do not repeat them if no progress is being made.",
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_media_type,
                            "data": encoded_screenshot
                        },
                    },
                ],
            }
        ],
    )
    response_text =response.content[0].text 
    print(response_text)
    try:
        json_response = json.loads(response_text)
    except json.JSONDecodeError:
        print("Error: Invalid JSON response")
        cleaned_response = vision_client.messages.create(
            model=correction_model_version,
            max_tokens=1000,
            system="You are a helpful assistant to fix an invalid JSON response. You need to fix the invalid JSON response to be valid JSON. You must respond in JSON only with no other fluff or bad things will happen. Do not return the JSON inside a code block.",
            messages=[
                {"role": "user", "content": f"The invalid JSON response is: {response_text}"},
            ],
        )
        try:
            cleaned_json_response = json.loads(cleaned_response.content[0].text)
        except json.JSONDecodeError:
            print("Error: Invalid JSON response")
            return {}
        return cleaned_json_response

    return json_response


if __name__ == "__main__":
    image = Image.open("image.png")
    actions = get_actions(image, "upvote the pinterest post")
