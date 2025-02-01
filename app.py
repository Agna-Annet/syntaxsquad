from flask import Flask, render_template, request, jsonify
import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set the API key
api_key = "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"

def get_emotion(text):
    # Formulate the prompt to request emotion analysis from the model
    prompt = f"""Analyze the emotional content of this text: '{text}'
    Return ONLY a JSON object with the following emotions as keys and their percentages (0-100) as values:
    {{
        "happy": percentage,
        "sadness": percentage,
        "angry": percentage,
        "fear": percentage,
        "disgust": percentage,
        "neutral": percentage
    }}
    The percentages should add up to 100. Return only the JSON object, no other text."""

    try:
        # API endpoint and headers
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Request payload
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 150
        }

        # Make the API request
        with httpx.Client() as client:
            response = client.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # Parse the response content as JSON
            emotion_result = json.loads(result['choices'][0]['message']['content'].strip())
            
            # Ensure all emotions are present and values are integers
            required_emotions = ["happy", "sadness", "angry", "fear", "disgust", "neutral"]
            for emotion in required_emotions:
                if emotion not in emotion_result:
                    emotion_result[emotion] = 0
                else:
                    emotion_result[emotion] = int(emotion_result[emotion])
                    
            return emotion_result
    except Exception as e:
        print(f"Error: {str(e)}")
        return str(e)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.json.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        emotion_result = get_emotion(text)
        if isinstance(emotion_result, str):  # If it's an error message
            return jsonify({'error': emotion_result}), 500
        return jsonify({'result': emotion_result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
