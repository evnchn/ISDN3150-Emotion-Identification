from openai import AzureOpenAI

functions = [
    {
        'name': 'output_final_emotion',
        'description': 'Output the final emotion of the user.',
        'parameters': {
            'type': 'object',
            'properties': {
                'emotions': {
                    'type': 'array',
                    'description': (
                        'The emotion(s) of the user. Required field.'
                        ' Follow order of appearance in the text.'
                    ),
                    'items': {
                        'type': 'object',
                        'properties': {
                            'emotion': {
                                'type': 'string',
                                'description': 'The emotion detected. Mandatory.',
                                'enum': [
                                    'happiness',
                                    'sadness',
                                    'anger',
                                    'surprise',
                                    'disgust',
                                    'fear',
                                    'indifference',
                                ],
                            },
                            'keywords': {
                                'type': 'array',
                                'description': (
                                    'The keywords that led to the emotion detected.'
                                    ' Mandatory. Case sensitive.'
                                ),
                                'items': {'type': 'string'},
                            },
                            'reasoning': {
                                'type': 'string',
                                'description': 'The reasoning for inferring this emotion from the text. Mandatory.',
                            },
                            'confidence': {
                                'type': 'number',
                                'description': 'The confidence of your prediction. Can be 0,25,50,75,100. Mandatory.',
                            },
                        },
                    },
                },
            },
        },
    },
]


def get_emotions(text_in, api_key=''):
    if not api_key:
        raise ValueError('API key is required.')
    client = AzureOpenAI(
        azure_endpoint='https://hkust.azure-api.net',  # HKUST Azure end point
        api_key=api_key,
        api_version='2024-02-01',
    )
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {
                'role': 'system',
                'content': (
                    'You are a skilled mental health expert.'
                    ' Your task is to decode the emotions from the text.'
                    ' Function parameters are mandatory.'
                    ' Indicate contrasting emotions in compound sentences.'
                ),
            },
            {'role': 'user', 'content': text_in},
        ],
        temperature=0.5,  # lower = more deterministic, higher = more creative
        max_tokens=300,
        tools=[{'type': 'function', 'function': functions[0]}],
        tool_choice={'type': 'function', 'function': {'name': 'output_final_emotion'}},
    )
    return response
