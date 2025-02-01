import json
import httpx
from http.server import BaseHTTPRequestHandler

api_key = "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"

def get_emotion(text):
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
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 150
        }

        with httpx.Client() as client:
            response = client.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            emotion_result = json.loads(result['choices'][0]['message']['content'].strip())
            
            required_emotions = ["happy", "sadness", "angry", "fear", "disgust", "neutral"]
            for emotion in required_emotions:
                if emotion not in emotion_result:
                    emotion_result[emotion] = 0
                else:
                    emotion_result[emotion] = int(emotion_result[emotion])
                    
            return emotion_result
    except Exception as e:
        return str(e)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        text = data.get('text', '')
        if not text:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'No text provided'}).encode())
            return

        try:
            emotion_result = get_emotion(text)
            if isinstance(emotion_result, str):
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': emotion_result}).encode())
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'result': emotion_result}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
