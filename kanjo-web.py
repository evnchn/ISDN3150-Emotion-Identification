from __future__ import annotations

import json
import os
import re

import openai
from dotenv import load_dotenv
from nicegui import ui

from kanjo import get_emotions

# Load the .env file
load_dotenv()

color_dict = {
    'happiness': 'green',
    'sadness': 'blue',
    'anger': 'red',
    'surprise': 'yellow',
    'disgust': 'purple',
    'fear': 'orange',
    'indifference': 'gray',
}


def show_block(emotion, keywords, reasoning, confidence, raw_text):
    with ui.card().classes(f'border-{color_dict[emotion]}-500 w-full bg-{color_dict[emotion]}-100'):
        ui.label(emotion.title()).classes('text-2xl')
        prepare_string = raw_text
        for keyword in keywords:
            prepare_string = re.sub(r'(?i)' + re.escape(keyword), lambda m: f'**{m.group(0)}**', prepare_string)
        ui.markdown(prepare_string).classes('text-lg make-strong-red')
        ui.label(f'Reasoning: {reasoning}')
        ui.label(f'Confidence: {confidence}%')


@ui.page('/')
def main(secret: str | None = None):
    ui.label('ISDN3150 Lab 1: Emotion Analysis').classes('text-2xl font-bold')

    input_apikey = ui.input(
        'API Key', value=secret, password=True,
        validation={'API key is required': lambda v: bool(v.strip())},
    ).classes('w-full')

    def process_text():
        if not input_apikey.value or not input_apikey.value.strip():
            raw_response.set_text('Please enter an API key')
            return
        if not text_input.value or not text_input.value.strip():
            raw_response.set_text('Please enter text to analyze')
            return
        text_for_analysis = text_input.value
        try:
            response = get_emotions(text_for_analysis, api_key=input_apikey.value)
        except ValueError as e:
            raw_response.set_text(f'Validation error: {e}')
            return
        except openai.APIError as e:
            raw_response.set_text(f'API error: {e}')
            return

        emotions_json_text = response.choices[0].message.tool_calls[0].function.arguments

        raw_response.set_text(emotions_json_text)

        try:
            emotions_json = json.loads(emotions_json_text)
        except json.JSONDecodeError:
            raw_response.set_text('Failed to parse API response')
            return

        emotions = emotions_json['emotions']

        show_emotions.refresh(emotions, text_for_analysis)

    with ui.row().classes('w-full items-center'):
        text_input = ui.input(
            'Enter text to analyze',
            validation={'Text is required': lambda v: bool(v.strip())},
        ).classes('text-lg flex flex-grow')
        ui.button('Analyze', on_click=process_text)
    raw_response = ui.label('Raw response')

    @ui.refreshable
    def show_emotions(emotions=None, text_for_analysis=None):
        if not emotions:
            return
        for emotion in emotions:
            if emotion.get('emotion') not in color_dict:
                continue
            show_block(
                emotion.get('emotion', 'indifference'),
                emotion.get('keywords', []),
                emotion.get('reasoning', ''),
                emotion.get('confidence', 'N/A'),
                text_for_analysis,
            )

    show_emotions()


@ui.page('/admin')
def admin():
    return main(secret=os.getenv('OPENAI_API_KEY'))


ui.run()
