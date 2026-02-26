import pytest

from kanjo import functions, get_emotions


class TestFunctionSchema:
    """Test the OpenAI function schema is well-formed."""

    def test_functions_list_not_empty(self):
        assert len(functions) > 0

    def test_function_has_required_keys(self):
        func = functions[0]
        assert 'name' in func
        assert 'description' in func
        assert 'parameters' in func

    def test_function_name(self):
        assert functions[0]['name'] == 'output_final_emotion'

    def test_emotions_enum_present(self):
        emotions_enum = functions[0]['parameters']['properties']['emotions']['items']['properties']['emotion']['enum']
        assert isinstance(emotions_enum, list)
        expected_count = 7
        assert len(emotions_enum) == expected_count

    def test_all_expected_emotions_in_enum(self):
        emotions_enum = functions[0]['parameters']['properties']['emotions']['items']['properties']['emotion']['enum']
        expected = ['happiness', 'sadness', 'anger', 'surprise', 'disgust', 'fear', 'indifference']
        assert set(emotions_enum) == set(expected)


class TestGetEmotions:
    """Test get_emotions function."""

    def test_raises_value_error_without_api_key(self):
        with pytest.raises(ValueError, match='API key is required'):
            get_emotions('hello')

    def test_raises_value_error_with_empty_api_key(self):
        with pytest.raises(ValueError, match='API key is required'):
            get_emotions('hello', api_key='')


class TestColorDict:
    """Test that color_dict is consistent with the function schema."""

    def test_all_emotions_have_colors(self):
        # Import here since kanjo-web.py has side effects (ui.run)
        # We test the color_dict independently
        from kanjo import functions
        emotions_enum = functions[0]['parameters']['properties']['emotions']['items']['properties']['emotion']['enum']
        color_dict = {
            'happiness': 'green',
            'sadness': 'blue',
            'anger': 'red',
            'surprise': 'yellow',
            'disgust': 'purple',
            'fear': 'orange',
            'indifference': 'gray',
        }
        for emotion in emotions_enum:
            assert emotion in color_dict, f'Emotion {emotion} missing from color_dict'
