from flask import Flask, request, send_file
from utilities.utils import *
import os
import subprocess

app = Flask(__name__)

conversation = ""

@app.route('/generate_audio', methods=['POST'])
def generate_audio():

    global conversation

    data = request.json
    user_input = data.get('utterance', '')
    user_name = data.get('user_name', 'Nishant')

    if user_input:
        reply = generate_reply_1(user_utterance=user_input, user_name=user_name, conversation=conversation)
        conversation += f"{user_name} : {user_input} \n"
        conversation += f"Juan : {reply}\n"
        # Assuming you have a client instance for your TTS model
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="fable",
            input=reply,
        )

        # Provide the file path directly to stream_to_file
        output_file_path = "output.mp3"
        response.stream_to_file(output_file_path)

        # Stream the file back to the client
        return send_file(
            output_file_path,
            as_attachment=True,
            download_name="output.mp3",
            mimetype="audio/mpeg"
        )
    else:
        return {"error": "Invalid input"}, 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
