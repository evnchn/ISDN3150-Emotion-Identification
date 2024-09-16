from kanjo import get_emotions

from nicegui import ui

import json

import os

from dotenv import load_dotenv

# Load the .env file
load_dotenv()


"""["happiness" GREEN,
 "sadness" BLUE , 
"anger" RED ,
 "surprise" YELLOW, 
"disgust" PURPLE,
 "fear" BLACK, 
"indifference" GRAY]
"""

color_dict = {
    "happiness": "green",
    "sadness": "blue",
    "anger": "red",
    "surprise": "yellow",
    "disgust": "purple",
    "fear": "orange",
    "indifference": "gray"
}

import re

def show_block(emotion, keywords, reasoning, confidence, raw_text):
    with ui.card().classes(f"border-{color_dict[emotion]}-500 w-full bg-{color_dict[emotion]}-100"):
        ui.label(emotion.title()).classes("text-2xl")
        prepare_string = raw_text
        for keyword in keywords:
            prepare_string = re.sub(r'(?i)'+re.escape(keyword), lambda m: f"**{m.group(0)}**", prepare_string)
        ui.markdown(prepare_string).classes("text-lg make-strong-red")
        ui.label(f"Reasoning: {reasoning}")
        ui.label(f"Confidence: {confidence}%")

@ui.page("/")
def main(secret: str = None):
    ui.label("ISDN3150 Lab 1: Emotion Analysis").classes("text-2xl font-bold")

    input_apikey = ui.input("API Key", value=secret, password=True).classes("w-full")

    def process_text():
        text_for_analysis = text_input.value
        try:
            response = get_emotions(text_for_analysis, api_key=input_apikey.value)
        except Exception as e:
            print(e)
            raw_response.set_text(str(e))
            return
        print(response)

        emotions_json_text = response.choices[0].message.function_call.arguments
        print(emotions_json_text)

        raw_response.set_text(emotions_json_text)

        emotions_json = json.loads(emotions_json_text)
        print(emotions_json)

        emotions = emotions_json["emotions"]

        show_emotions.refresh(emotions, text_for_analysis)

    with ui.row().classes("w-full items-center"):
        text_input = ui.input("Enter text to analyze").classes(
            "text-lg flex flex-grow")
        button = ui.button("Analyze", on_click=process_text)
    raw_response = ui.label("Raw response")

    @ui.refreshable
    def show_emotions(emotions = None, text_for_analysis = None):
        if not emotions:
            return
        for emotion in emotions:
            if not emotion.get("emotion") in color_dict:
                continue
            show_block(emotion.get("emotion","indifference"), emotion.get("keywords",[]), emotion.get("reasoning",""), emotion.get("confidence", "N/A"), text_for_analysis)

    show_emotions()

@ui.page("/admin")
def admin():
    print(os.getenv("OPENAI_API_KEY"))
    return main(secret=os.getenv("OPENAI_API_KEY"))

ui.run()
