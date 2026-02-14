import os
import json
import base64
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def analyze_image_with_vision(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    prompt = """
    You are a professional fashion stylist and image consultant. Analyze this image deeply.
    
    1. Identify the person's features:
       - Estimated Skin Tone (e.g., Warm, Cool, Olive, Fair, Deep)
       - Body Shape/Type (if visible)
       - Facial Features/Vibe
       
    2. Analyze the context/outfit (if present):
       - Current Style
       - Colors worn
       - Occasion fit
       
    3. PROVIDE STYLING ADVICE:
       - "What to Wear": Suggest 3 specific outfit ideas that would perfectly suit this person's features.
       - "Why it Suits": Explain WHY these colors, cuts, and styles work for their specific skin tone and body type.
       
    4. ADDITIONAL ANALYSIS:
       - "Style Score": Rate the outfit/look on a scale of 0-100 based on coordination, fit, and trendiness.
       - "Mood & Vibe": Describe the mood (e.g., "Confident & Edgy", "Relaxed Boho").
       - "Colors & Patterns": Analyze the color palette and any patterns used.
       
    Format the output as JSON with keys: 
    "features", 
    "outfit_ideas" (list of strings), 
    "why_it_suits" (string), 
    "style_score" (integer 0-100),
    "mood_analysis" (string),
    "color_pattern_analysis" (string).
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"VISION API ERROR: {str(e)}")
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Optional: OpenCV processing could go here
        # image = cv2.imread(filepath)
        # ...
        
        result = analyze_image_with_vision(filepath)
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
