import requests
import json

def test_continuous_input_api(api_url, audio_file_path, question, user_id, user_name, character):
    """
    Test the continuous input API by sending an audio file and associated data as query parameters.

    Args:
    api_url (str): The URL of the API endpoint.
    audio_file_path (str): Path to the audio file to be sent.
    question (str): The question to be sent with the request.
    user_id (str): The ID of the user.
    user_name (str): The name of the user.
    character (str): The character to be used for the response.

    Returns:
    dict: A dictionary containing the status code and response content.
    """
    # Prepare the query parameters
    params = {
        "question": question,
        "user_id": user_id,
        "user_name": user_name,
        "character": character
    }

    try:
        # Open and read the audio file as binary
        with open(audio_file_path, 'rb') as audio_file:
            # Prepare the files for the request
            files = {
                'audio_file': ('audio.wav', audio_file, 'audio/wav'),
            }
            
            # Send POST request with query parameters and file
            response = requests.post(api_url, params=params, files=files)

        # Check if the request was successful
        if response.status_code == 200:
            print("Request successful!")
            return {
                "status_code": response.status_code,
                "content": response.content
            }
        else:
            print(f"Request failed with status code: {response.status_code}")
            return {
                "status_code": response.status_code,
                "content": response.text
            }

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {
            "status_code": None,
            "content": str(e)
        }

# Example usage
if __name__ == "__main__":
    api_url = 'http://65.0.178.207:6000/generate_response_continuous_v2'
    audio_file_path = 'harvard_wav.wav'
    user_id = 'user_206e2dbdc24f4b699fbf271326b4e3af'
    user_name = 'nishant'
    question = 'What is the weather like today?'
    character = 'sophia'

    result = test_continuous_input_api(api_url, audio_file_path, question, user_id, user_name, character)
    
    print("Test Result:")
    print(f"Status Code: {result['status_code']}")
    if result['status_code'] == 200:
        print("Response received successfully.")
        # The response is likely binary data (audio), so we'll just print its length
        print(f"Response Content Length: {len(result['content'])} bytes")
    else:
        print(f"Error Content: {result['content']}")