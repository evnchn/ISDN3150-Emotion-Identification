from __future__ import annotations

import json
import os
import re
from typing import TypedDict

import openai
from dotenv import load_dotenv
from nicegui import ui

from kanjo import get_emotions

# Load the .env file
load_dotenv()


class EmotionResult(TypedDict):
    emotion: str
    keywords: list[str]
    reasoning: str
    confidence: int


color_dict: dict[str, str] = {
    'happiness': 'green',
    'sadness': 'blue',
    'anger': 'red',
    'surprise': 'yellow',
    'disgust': 'purple',
    'fear': 'orange',
    'indifference': 'gray',
}


def show_block(emotion: str, keywords: list[str], reasoning: str, confidence: int | str, raw_text: str) -> None:
    with ui.card().classes(f'border-l-4 border-{color_dict[emotion]}-500 w-full bg-gray-800 rounded-xl shadow-lg'):
        ui.label(emotion.title()).classes(f'text-2xl font-bold text-{color_dict[emotion]}-400')
        prepare_string = raw_text
        for keyword in keywords:
            prepare_string = re.sub(r'(?i)' + re.escape(keyword), lambda m: f'**{m.group(0)}**', prepare_string)
        ui.markdown(prepare_string).classes('text-lg text-gray-300')
        ui.label(f'Reasoning: {reasoning}').classes('text-sm text-gray-400 italic')
        ui.label(f'Confidence: {confidence}%').classes('text-sm font-semibold text-cyan-300')


@ui.page('/')
def main(secret: str | None = None):
    ui.dark_mode(True)
    ui.query('.nicegui-content').classes('p-0 gap-0')

    with ui.element('div').classes('w-full bg-gradient-to-r from-gray-900 via-gray-900 to-cyan-950 p-8 rounded-b-2xl mb-6'):
        ui.label('ISDN3150 Lab 1: Emotion Analysis').classes('text-3xl font-bold text-cyan-400 tracking-tight')
        ui.label('Powered by GPT-4o-mini').classes('text-sm text-gray-500 mt-1')

    with ui.column().classes('w-full max-w-4xl mx-auto px-8 gap-4'):
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
            ui.button('Analyze', on_click=process_text).classes('bg-cyan-600 hover:bg-cyan-500 text-white font-semibold px-6 py-2 rounded-lg transition-colors')
        raw_response = ui.label('Raw response').classes('text-sm text-gray-500')

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


# /admin is expected to be protected by Cloudflare Access
@ui.page('/admin')
def admin():
    return main(secret=os.getenv('OPENAI_API_KEY'))


ui.run()
