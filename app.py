import streamlit as st
import json
import os
from groq import Groq
from dotenv import load_dotenv
import hashlib
from pytrends.request import TrendReq
import pandas as pd
import requests
import io
from PIL import Image
from streamlit_mic_recorder import speech_to_text

# Load environment variables
load_dotenv()

# --- Configuration & Setup ---
st.set_page_config(
    page_title="StyleSense AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = "data.json"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Custom CSS for Premium UI ---
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Poppins:wght@300;400;500;600&display=swap');

    :root {
        --primary-color: #6c5ce7;
        --secondary-color: #a29bfe;
        --accent-color: #fd79a8;
        --background-gradient: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        --glass-bg: rgba(255, 255, 255, 0.65);
        --glass-border: rgba(255, 255, 255, 0.4);
        --text-dark: #2d3436;
        --text-light: #636e72;
        --shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        --card-hover-shadow: 0 15px 35px rgba(31, 38, 135, 0.15);
    }

    /* Global App Styling */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(255, 246, 236) 0%, rgb(248, 240, 255) 90%);
        font-family: 'Poppins', sans-serif;
        color: var(--text-dark);
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif;
        color: var(--text-dark);
        font-weight: 700;
    }
    
    p, div, label, input, textarea {
        font-family: 'Poppins', sans-serif;
        color: var(--text-dark);
    }

    /* Glassmorphism Card Effect */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow);
        padding: 30px;
        margin-bottom: 25px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--card-hover-shadow);
        border-color: rgba(255, 255, 255, 0.8);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #fd79a8, #6c5ce7);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 12px 35px;
        font-weight: 600;
        font-size: 16px;
        letter-spacing: 0.5px;
        box-shadow: 0 5px 15px rgba(108, 92, 231, 0.2);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        text-transform: uppercase;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(108, 92, 231, 0.4);
        background: linear-gradient(90deg, #6c5ce7, #fd79a8);
        color: white;
    }
    
    .stButton > button:active {
        transform: scale(0.98);
    }

    /* Inputs */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 15px;
        border: 2px solid rgba(255, 255, 255, 0.5);
        background-color: rgba(255, 255, 255, 0.5);
        padding: 10px 15px;
        transition: all 0.3s ease;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
        color: #2d3436;
    }

    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus-within {
        border-color: var(--primary-color);
        background-color: rgba(255, 255, 255, 0.9);
        box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
        outline: none;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 3rem;
    }

    /* Hero Text */
    .hero-text {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        background: linear-gradient(90deg, #6C5CE7, #fd79a8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .subtitle {
        text-align: center;
        color: var(--text-light);
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Feature Icon */
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #fff, #f0f0f0);
        width: 100px;
        height: 100px;
        line-height: 100px;
        text-align: center;
        border-radius: 50%;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        display: inline-block;
        transition: transform 0.3s ease;
    }
    
    .glass-card:hover .feature-icon {
        transform: rotate(10deg) scale(1.1);
    }
    
    /* Hero Section Background */
    .hero-bg {
        background-image: url("https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        border-radius: 0 0 50px 50px;
        padding: 100px 20px;
        margin: -60px -20px 50px -20px; /* Negative margin to stretch full width */
        position: relative;
        text-align: center;
        color: white;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }
    
    .hero-overlay {
        background: linear-gradient(180deg, rgba(108, 92, 231, 0.4) 0%, rgba(253, 121, 168, 0.2) 100%);
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 0 0 50px 50px;
        z-index: 1;
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(108, 92, 231, 0.3);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(108, 92, 231, 0.5);
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
    }
    </style>

""", unsafe_allow_html=True)

# --- Data Management Functions ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "history": []}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"users": {}, "history": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

# --- AI Generation Function ---
def generate_style_content(topic, platform, language, style_context, mood, weather, user_profile):
    if not GROQ_API_KEY:
        return "⚠️ Error: Groq API Key not found. Please check your .env file."
    
    client = Groq(api_key=GROQ_API_KEY)
    
    model = "llama-3.3-70b-versatile"
    
    prompt = f"""
    You are StyleSense, an expert AI Fashion Stylist and Content Creator.
    
    Goal: Generate engaging, trendy, and platform-specific fashion content based on the user's request and profile.
    
    Request Details:
    - Topic: {topic}
    - Platform: {platform}
    - Language: {language}
    - Mood: {mood}
    - Weather: {weather}
    - Style Vibes: {style_context}
    
    User Profile:
    - Body Type: {user_profile.get('body_type', 'Not specified')}
    - Skin Tone: {user_profile.get('skin_tone', 'Not specified')}
    - Gender Preference: {user_profile.get('gender', 'Not specified')}
    
    Guidelines:
    - Tone: Stylish, confident, inclusive, and helpful.
    - {platform} specific optimizations (e.g., hashtags for Instagram, concise constraints for Twitter).
    - If the platform is Instagram, suggest a caption, a visual description of the outfit/photo, and relevant hashtags.
    - If the platform is Twitter, keep it punchy and thread-like if needed.
    - If the platform is WhatsApp, make it personal and shareable.
    - Suggest outfits that flatter the specific body type and skin tone mentioned.
    - Consider the weather and mood in the recommendation.
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error generating content: {str(e)}"
    
def get_sustainability_score(item_description):
    if not GROQ_API_KEY:
        return "⚠️ API Key missing"
    
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""
    Analyze the sustainability of this fashion item: "{item_description}".
    
    Return ONLY a JSON object with:
    - "score": (1-10 integer, 10 being most eco-friendly)
    - "reason": (Short 1 sentence explanation)
    - "tips": (Short 1 sentence tip to make it more sustainable)
    
    Do not add markdown formatting. Just the JSON string.
    """
    
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"score": 5, "reason": "Could not analyze", "tips": "Check materials manualy."}

def get_trend_data(keywords):
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(keywords, cat=0, timeframe='today 12-m', geo='', gprop='')
        data = pytrends.interest_over_time()
        return data
    except Exception as e:
        return None

def analyze_trends(trend_data_str):
    if not GROQ_API_KEY: return "Error: No API Key"
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"Analyze this fashion trend data trend: '{trend_data_str}'. Predict if it's rising or falling and give one strategy to wear it."
    
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return completion.choices[0].message.content

import base64

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def analyze_image_with_vision(image_base64):
    if not GROQ_API_KEY:
        return None
    
    client = Groq(api_key=GROQ_API_KEY)
    
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
                                "url": f"data:image/jpeg;base64,{image_base64}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"VISION API ERROR: {str(e)}")
        return {"error": str(e)}

def generate_image(prompt):
    # Free Hugging Face Inference API (using public model)
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    headers = {"Authorization": f"Bearer hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"} # Placeholder or specific key needed
    # Using a public space or fallback if no key provided by user.
    # For demo, let's use a very basic prompt structure
    
    # Since we don't have a user HF token, we'll try without auth (often works for public models on EF)
    # or better, use a placeholder image if it fails.
    try:
        response = requests.post(API_URL, json={"inputs": prompt})
        if response.status_code == 200:
            return response.content
        else:
            return None
    except:
        return None

# --- Session State Initialization ---
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'Home'
# Default Profile
if 'profile' not in st.session_state:
    st.session_state['profile'] = {"body_type": "Hourglass", "skin_tone": "Warm", "gender": "Female"}

# --- Navigation ---
def navigate_to(page):
    st.session_state['page'] = page
    st.rerun()

# --- Pages ---

def home_page():
    # Hero Section
    st.markdown("""
        <div class="hero-bg">
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <h1 style="color: white; font-size: 4rem; margin-bottom: 0;">StyleSense AI</h1>
                <p style="font-size: 1.5rem; opacity: 0.95; font-weight: 300; letter-spacing: 1px;">Elevate Your Wardrobe with Artificial Intelligence</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    st.markdown("<h2 style='text-align: center; margin-bottom: 40px;'>Explore Features</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <div class="feature-icon">🤖</div>
            <h3>AI Stylist</h3>
            <p>Get personalized outfit advice based on your body type, mood, and occasion.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="glass-card">
            <div class="feature-icon">✨</div>
            <h3>Trend Forecasting</h3>
            <p>Stay ahead of the curve with real-time fashion trend analysis and predictions.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="glass-card">
            <div class="feature-icon">👗</div>
            <h3>Digital Wardrobe</h3>
            <p>Digitize your closet and get mix-and-match suggestions from what you own.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Authentication / Welcome Area
    if st.session_state['user']:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h2>Welcome back, {st.session_state['user']}!</h2>
            <p>Ready to style your next look?</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_c1, col_c2, col_c3 = st.columns([1,2,1])
        with col_c2:
            if st.button("✨ Go to Studio", use_container_width=True):
                navigate_to("Studio")
    else:
        st.markdown("<h3 style='text-align: center;'>Get Started</h3>", unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            if st.button("Log In", use_container_width=True):
                navigate_to("Login")
            if st.button("Sign Up", use_container_width=True):
                navigate_to("Signup")

def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="glass-card">
            <h2 style="text-align: center;">Welcome Back</h2>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            data = load_data()
            users = data.get("users", {})
            
            if username in users and verify_password(users[username]["password"], password):
                st.session_state['user'] = username
                st.success("Logged in successfully!")
                navigate_to("Home")
            else:
                st.error("Invalid username or password")
                
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Back to Home", use_container_width=True):
            navigate_to("Home")

def signup_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="glass-card">
            <h2 style="text-align: center;">Join StyleSense</h2>
        </div>
        """, unsafe_allow_html=True)
        
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        st.markdown("### Create Your Style Profile")
        body_type = st.selectbox("Body Type", ["Hourglass", "Pear", "Apple", "Rectangle", "Inverted Triangle", "Athletic"])
        skin_tone = st.selectbox("Skin Tone / Undertone", ["Warm", "Cool", "Neutral", "Olive", "Deep"])
        gender = st.selectbox("Preferred Styling", ["Female", "Male", "Unisex"])
        
        if st.button("Create Account", use_container_width=True):
            if new_password != confirm_password:
                st.error("Passwords do not match")
                return
                
            data = load_data()
            if new_username in data["users"]:
                st.error("Username already exists")
                return
                
            data["users"][new_username] = {
                "password": hash_password(new_password),
                "profile": {
                    "body_type": body_type,
                    "skin_tone": skin_tone,
                    "gender": gender
                }
            }
            # Auto-login context for session
            st.session_state['profile'] = data["users"][new_username]["profile"]
            
            save_data(data)
            st.success("Account created! Please log in.")
            navigate_to("Login")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Back to Home", use_container_width=True):
            navigate_to("Home")

def studio_page():
    st.markdown("<h1 class='hero-text'>Content Studio</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Create magic with AI.</p>", unsafe_allow_html=True)
    
    # Inputs
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 1. Vision")
        
        # Voice Input
        st.write("🎤 Voice Input:")
        voice_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='studio_mic')
        
        default_topic = ""
        if voice_text:
            default_topic = voice_text
        
        topic = st.text_area("What's on your mind?", value=default_topic,
                            placeholder="e.g., Summer beach party outfit, Interview attire for tech job...")
        
        style_context = st.multiselect("Select Vibes/Context", 
                                      ["Casual", "Professional", "Vintage", "Streetwear", 
                                       "Minimalist", "Boho", "Glam", "Sustainable", "Edgy"],
                                      default=["Casual"])
        
        mood = st.select_slider("Select Mood", options=["Lazy", "Casual", "Confident", "Festive", "Professional", "Bold"])
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 2. Details")
        platform = st.selectbox("Select Platform", ["Instagram", "Twitter", "WhatsApp", "Blog Post", "LinkedIn"])
        language = st.selectbox("Language", ["English", "Spanish", "French", "Hindi", "Mandarin", "Arabic"])
        weather = st.selectbox("Weather Context", ["Sunny & Hot", "Mild / Spring", "Rainy", "Cold / Snowy", "Windy", "Indoor / AC"])
    
        occasion = st.selectbox("Occasion", ["Casual", "Date Night", "Wedding Guest", "Job Interview", "Party", "Travel", "Gym/Athleisure", "Office"])
        st.markdown('</div>', unsafe_allow_html=True)
        
    if st.button("✨ Generate Magic"):
        if not topic:
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Consulting the fashion oracle..."):
                # Get user profile if logged in
                user_profile = st.session_state.get('profile', {})
                
                # Combine topic with occasion for better context
                full_topic = f"{topic} for {occasion}"
                
                result = generate_style_content(full_topic, platform, language, ", ".join(style_context), mood, weather, user_profile)
                
                # Calculate Sustainability Score if topic implies an item
                sus_score = get_sustainability_score(topic)
                
                # Display Result
                st.subheader("Your Content")
                st.markdown("---")
                
                # Sustainability Badge
                score = sus_score.get('score', 5)
                color = "#00b894" if score > 7 else "#fdcb6e" if score > 4 else "#d63031"
                st.markdown(f"""
                <div class="glass-card" style="border-left: 8px solid {color};">
                    <h4>🌿 Eco-Score: {score}/10</h4>
                    <p><strong>Analysis:</strong> {sus_score.get('reason')}</p>
                    <p><em>Tip: {sus_score.get('tips')}</em></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f'<div class="glass-card"><h3>✨ A.I. Suggestion</h3>{result}</div>', unsafe_allow_html=True) 
                
                # Image Generation Option
                if st.button("🎨 Visualize This Outfit"):
                    with st.spinner("Generating AI Image (this may take 30s)..."):
                        img_prompt = f"Professional fashion photography of {full_topic}, {mood}, {weather}, {', '.join(style_context)}"
                        image_bytes = generate_image(img_prompt)
                        if image_bytes:
                            st.image(image_bytes, caption="AI Generated Visualization", use_container_width=True)
                        else:
                            st.warning("Could not generate image. API busy or unauthorized.")
                
                # Save to History
                data = load_data()
                if "history" not in data:
                    data["history"] = []
                    
                data["history"].append({
                    "user": st.session_state['user'],
                    "topic": full_topic,
                    "platform": platform,
                    "language": language,
                    "content": result,
                    "timestamp": "Just now" 
                })
                save_data(data)

def generate_static_advice(request_type, user_profile):
    if not GROQ_API_KEY:
        return "⚠️ Please set API Key."
    
    client = Groq(api_key=GROQ_API_KEY)
    model = "llama-3.3-70b-versatile"
    
    if request_type == "dos_donts":
        prompt = f"""
        Generate a concise list of 5 Fashion DOs and 5 Fashion DON'Ts specifically for:
        Body Type: {user_profile.get('body_type')}
        Skin Tone: {user_profile.get('skin_tone')}
        Gender: {user_profile.get('gender')}
        
        Format as clear markdown bullet points. 
        Focus on cuts, colors, and styling tricks.
        """
    elif request_type == "trends":
        prompt = f"""
        What are the top 3 current fashion trends suitable for:
        Gender: {user_profile.get('gender')}
        
        Briefly explain each and why it works.
        """
        
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def style_guide_page():
    st.markdown("<h1 class='hero-text'>Style Guide</h1>", unsafe_allow_html=True)
    
    user_profile = st.session_state.get('profile', {})
    if not user_profile:
        st.info("Please update your profile in the Sign Up page to get personalized advice.")
        return

    tab1, tab2 = st.tabs(["✅ Do's & ❌ Don'ts", "📈 Trend Watch"])
    
    with tab1:
        st.markdown(f'<div class="glass-card"><h3>Styling Rules for {user_profile.get("body_type")} Body & {user_profile.get("skin_tone")} Tone</h3>', unsafe_allow_html=True)
        if st.button("Generate My Rules", use_container_width=True):
            with st.spinner("Analyzing your profile..."):
                advice = generate_static_advice("dos_donts", user_profile)
                st.markdown(advice)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="glass-card"><h3>Current Trends for You</h3>', unsafe_allow_html=True)
        
        # Real Trend Input
        trend_kw = st.text_input("Analyze a Trend Keyword", "Oversized Blazer")
        
        if st.button("Analyze Trend Live", use_container_width=True):
            with st.spinner(f"Fetching data for {trend_kw}..."):
                trend_data = get_trend_data([trend_kw])
                if trend_data is not None and not trend_data.empty:
                    st.line_chart(trend_data[trend_kw], color="#6C5CE7")
                    
                    # AI Analysis
                    analysis = analyze_trends(f"Trend: {trend_kw}, Last 5 values: {trend_data[trend_kw].tail().tolist()}")
                    st.success("Analysis Complete")
                    st.markdown(f"**AI Insight:** {analysis}")
                else:
                    st.warning("Could not fetch data. Try a different keyword.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def chat_page():
    st.markdown("<h1 class='hero-text'>Chat with StyleSense</h1>", unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Voice Input for Chat
    c1, c2 = st.columns([1, 8])
    with c1:
        voice_chat_text = speech_to_text(language='en', start_prompt="🎤", stop_prompt="🛑", just_once=True, key='chat_mic')
    
    prompt = st.chat_input("Ask for style advice...")
    
    final_prompt = None
    if prompt:
        final_prompt = prompt
    elif voice_chat_text:
        final_prompt = voice_chat_text

    # React to user input
    if final_prompt:
        # Display user message in chat message container
        st.chat_message("user").markdown(final_prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": final_prompt})

        # Generate response
        try:
            client = Groq(api_key=GROQ_API_KEY)
            
            # Construct system prompt with context
            user_profile = st.session_state.get('profile', {})
            system_prompt = f"""You are StyleSense, an expert personal fashion stylist.
            User Profile: {user_profile}
            Context: The user is asking for real-time style advice. Be helpful, trendy, and concise.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
            ] + st.session_state.messages
            
            chat_completion = client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                temperature=0.7,
            )
            response = chat_completion.choices[0].message.content
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

def history_page():
    st.markdown("<h1 class='hero-text'>Style History</h1>", unsafe_allow_html=True)
    
    data = load_data()
    # Safely get history for user
    all_history = data.get("history", [])
    user_history = [h for h in all_history if h.get("user") == st.session_state['user']]
    
    if not user_history:
        st.info("No style history yet. Go to the Studio to generate some looks!")
    else:
        for item in reversed(user_history):
            with st.expander(f"📅 {item.get('topic', 'Unknown Topic')} - {item.get('platform', 'Platform')}"):
                st.markdown(f"""
                <div class="glass-card">
                    <p style="color: #666; font-size: 0.9em;">Language: {item.get('language')} | Time: {item.get('timestamp')}</p>
                    <hr>
                    {item.get('content')}
                </div>
                """, unsafe_allow_html=True)

def wardrobe_page():
    st.markdown("<h1 class='hero-text'>Digital Wardrobe</h1>", unsafe_allow_html=True)
    
    data = load_data()
    user_data = data["users"].get(st.session_state['user'], {})
    
    if "wardrobe" not in user_data:
        user_data["wardrobe"] = []
        data["users"][st.session_state['user']] = user_data
        save_data(data)
    
    wardrobe = user_data["wardrobe"]
    
    # --- Add Item Section ---
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.expander("➕ Add New Item to Closet", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input("Item Description", placeholder="e.g. Blue Denim Jacket")
        with col2:
            category = st.selectbox("Category", ["Top", "Bottom", "Dress", "Shoes", "Outerwear", "Accessory"])
            
        if st.button("Add to Wardrobe", use_container_width=True):
            if item_name:
                new_item = {"item": item_name, "category": category}
                wardrobe.append(new_item)
                user_data["wardrobe"] = wardrobe
                data["users"][st.session_state['user']] = user_data
                save_data(data)
                st.success(f"Added {item_name}!")
                st.rerun()
            else:
                st.warning("Please describe the item.")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Analytics Section ---
    if wardrobe:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Wardrobe Analysis")
        
        # Calculate stats
        total_items = len(wardrobe)
        categories = ["Top", "Bottom", "Dress", "Outerwear", "Shoes", "Accessory"]
        cat_counts = {cat: 0 for cat in categories}
        for item in wardrobe:
            if item['category'] in cat_counts:
                cat_counts[item['category']] += 1
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Total Items", total_items, "+1 this week")
            st.caption("Most popular: " + max(cat_counts, key=cat_counts.get))
            
        with c2:
            st.bar_chart(cat_counts, height=200, color="#6C5CE7")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # --- View Wardrobe ---
    if not wardrobe:
        st.info("Your wardrobe is empty. Add some items above!")
    else:
        st.markdown("### Your Collection")
        categories = ["Top", "Bottom", "Dress", "Outerwear", "Shoes", "Accessory"]
        
        # Create rows of 3 columns
        cols = st.columns(3)
        for idx, cat in enumerate(categories):
            col_idx = idx % 3
            with cols[col_idx]:
                st.markdown(f"""
                <div class="glass-card" style="padding: 15px;">
                    <h4 style="margin:0;">{cat}</h4>
                    <hr style="margin: 10px 0;">
                """, unsafe_allow_html=True)
                
                items = [i['item'] for i in wardrobe if i['category'] == cat]
                if items:
                    for i in items:
                        st.markdown(f"- {i}")
                else:
                    st.caption("No items")
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    
    # --- Mix & Match AI ---
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### ✨ Mix & Match Stylist")
    occasion_mix = st.selectbox("Outfit Occasion", ["Weekend Casual", "Work/Office", "Date Night", "Party"])
    
    if st.button("Create Outfit from My Wardrobe", use_container_width=True):
        if not wardrobe:
            st.error("Add items to your wardrobe first!")
        else:
            with st.spinner("Rummaging through your closet..."):
                wardrobe_text = ", ".join([f"{i['item']} ({i['category']})" for i in wardrobe])
                user_profile = st.session_state.get('profile', {})
                
                prompt = f"Act as a personal stylist. User Profile: {user_profile} Occasion: {occasion_mix} Available Wardrobe: {wardrobe_text} Task: Create a complete outfit using ONLY the items from the available wardrobe if possible. If a key piece is missing, suggest what to buy to complete the look. Explain why this outfit works for the occasion."
                
                if GROQ_API_KEY:
                    try:
                        client = Groq(api_key=GROQ_API_KEY)
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.3-70b-versatile",
                            temperature=0.7,
                        )
                        result = chat_completion.choices[0].message.content
                        st.markdown(f"<div style='background:rgba(255,255,255,0.5); padding:15px; border-radius:10px;'>{result}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"AI Error: {e}")
                else:
                    st.error("API Key missing.")
    st.markdown('</div>', unsafe_allow_html=True)

def smart_mirror_page():
    st.markdown("<h1 class='hero-text'>Smart Mirror AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Upload a photo to get personalized fashion analysis.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="glass-card"><h3>📸 Your Look</h3>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            st.image(uploaded_file, caption="Analyzed Image", use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="glass-card"><h3>🧠 AI Analysis</h3>', unsafe_allow_html=True)
        
        if uploaded_file:
            if st.button("✨ Analyze My Style", use_container_width=True):
                with st.spinner("Scanning features & consulting stylists..."):
                    # Encode and Analyze
                    base64_img = encode_image(uploaded_file)
                    analysis = analyze_image_with_vision(base64_img)
                    
                    if analysis and "error" not in analysis:
                        st.session_state['mirror_result'] = analysis
                    else:
                        error_msg = analysis.get("error", "Unknown error") if analysis else "No response from AI"
                        st.error(f"Could not analyze image: {error_msg}")
                        st.info("Check console for technical details.")
        
        # Display Results
        if 'mirror_result' in st.session_state:
            res = st.session_state['mirror_result']
            
            # --- Style Score Animation ---
            score = res.get('style_score', 0)
            st.markdown(f"#### 🏆 Style Score: {score}/100")
            st.progress(score)
            
            if score > 85:
                st.balloons()
                st.markdown("🌟 **Fashion Icon Status!**")
            elif score > 60:
                st.markdown("✨ **Looking Sharp!**")
            else:
                st.markdown("💡 **Room for Styling!**")
            
            st.divider()

            # --- Deep Analysis ---
            feat_col1, feat_col2 = st.columns(2)
            with feat_col1:
                st.markdown("**🎭 Mood/Vibe**")
                st.info(res.get('mood_analysis', 'N/A'))
            
            with feat_col2:
                st.markdown("**🎨 Colors & Patterns**")
                st.info(res.get('color_pattern_analysis', 'N/A'))
            
            st.divider()
            
            st.markdown("#### 👤 Features Detected")
            features = res.get('features', {})
            st.write(f"**Skin Tone:** {features.get('Estimated Skin Tone')}")
            st.write(f"**Body Shape:** {features.get('Body Shape/Type')}")
            st.write(f"**Vibe:** {features.get('Facial Features/Vibe')}")
            
            st.divider()
            
            st.markdown("#### 👗 What to Wear")
            for idea in res.get('outfit_ideas', []):
                st.success(f"• {idea}")
                
            st.divider()
            
            st.markdown("#### 💡 Why it Suits You")
            st.warning(res.get('why_it_suits'))
            
        else:
            st.info("Upload a photo and click analyze to see the magic!")
            
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Sidebar
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #6C5CE7;'>StyleSense AI</h2>", unsafe_allow_html=True)
        
        if st.session_state['user']:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: white; border-radius: 10px; margin-bottom: 20px;">
                <div style="font-size: 40px;">👤</div>
                <strong>{st.session_state['user']}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state['user'] = None
                navigate_to("Home")
            
            st.markdown("---")
            if st.button("🏠 Home", use_container_width=True):
                navigate_to("Home")
            if st.button("🪞 Smart Mirror", use_container_width=True):
                navigate_to("SmartMirror")
            if st.button("🎨 Studio", use_container_width=True):
                navigate_to("Studio")
            if st.button("💬 Chat", use_container_width=True):
                navigate_to("Chat")
            if st.button("👗 Wardrobe", use_container_width=True):
                navigate_to("Wardrobe")
            if st.button("📜 History", use_container_width=True):
                navigate_to("History")
            if st.button("📘 Guide", use_container_width=True):
                navigate_to("Guide")
        else:
            st.info("Please Log In to access features.")

    # Page Routing
    if st.session_state['page'] == "Home":
        home_page()
    elif st.session_state['page'] == "Login":
        login_page()
    elif st.session_state['page'] == "Signup":
        signup_page()
    elif st.session_state['page'] == "SmartMirror":
        if st.session_state['user']:
            smart_mirror_page()
        else:
            navigate_to("Login")
    elif st.session_state['page'] == "Studio":
        if st.session_state['user']:
            studio_page()
        else:
            navigate_to("Login")
    elif st.session_state['page'] == "Chat":
        if st.session_state['user']:
            chat_page()
        else:
            navigate_to("Login")
    elif st.session_state['page'] == "Wardrobe":
        if st.session_state['user']:
            wardrobe_page()
        else:
            navigate_to("Login")
    elif st.session_state['page'] == "History":
        if st.session_state['user']:
            history_page()
        else:
            navigate_to("Login")
    elif st.session_state['page'] == "Guide":
        if st.session_state['user']:
            style_guide_page()
        else:
            navigate_to("Login")
            
    # Footer
    st.markdown("""
        <div class="footer">
            <p>Made with ❤️ by Team Zenvy | © 2026 Fashion Tech</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
