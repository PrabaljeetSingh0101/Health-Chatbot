import os, json, time, asyncio, pygame, speech_recognition, edge_tts, hashlib, re, uuid, traceback
from dotenv import load_dotenv
import google.generativeai as genai
from fpdf import FPDF
from deep_translator import GoogleTranslator
from pymongo import MongoClient
from thefuzz import process

# Global Pygame init
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.mixer.init()

# 1. SETUP & CONFIGURATION
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
TEXT_MODE = os.getenv("TEXT_MODE", "0") == "1"

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3-pro-preview"

# Lowercase affirmation words for consistent logic check
languages = {
    "english": {"code": "en", "voice": "en-US", "output": "en-US-GuyNeural", "affirm": ["yes", "yeah", "correct", "yep"]},
    "hindi": {"code": "hi", "voice": "hi-IN", "output": "hi-IN-MadhurNeural", "affirm": ["haan", "ji", "sahi", "ha"]},
    "french": {"code": "fr", "voice": "fr-FR", "output": "fr-FR-HenriNeural", "affirm": ["oui", "d'accord", "correct"]},
    "spanish": {"code": "es", "voice": "es-ES", "output": "es-ES-AlvaroNeural", "affirm": ["sí", "si", "correcto"]}
}

def extract_json(output):
    """Robust JSON extraction from potentially noisy AI output."""
    json_str = output.strip()
    while True:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            if '{' in json_str or '[' in json_str:
                match = re.search(r'(\{.*?\}|\[.*?\])', json_str, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    continue
                else:
                    raise ValueError("No valid JSON block found")
            else:
                raise ValueError(f"Invalid JSON in output: {json_str}")

# 2. UTILITY FUNCTIONS
async def call_gemini_with_retry(prompt, is_json=True, retries=3):
    model = genai.GenerativeModel(MODEL_NAME)
    for i in range(retries):
        try:
            gen_config = {"response_mime_type": "application/json"} if is_json else {}
            response = await asyncio.to_thread(model.generate_content, prompt, generation_config=gen_config)
            output = response.text.strip()
            
            if is_json:
                try:
                    return extract_json(output)
                except (json.JSONDecodeError, ValueError) as je:
                    print(f"JSON Parse fail on attempt {i+1}: {je}. Retrying...")
                    continue
            return output
        except Exception as e:
            print(f"Gemini attempt {i+1} error: {e}")
            if i < retries - 1:
                await asyncio.sleep(1.5)
    return {"complete": True, "symptoms": [], "summary": "Extraction failed"} if is_json else "Unknown"

async def chatbot_speak(text, lang_code, voice_output):
    if TEXT_MODE:
        print(f"Chatbot: {text}")
        return
    translated = GoogleTranslator(source="en", target=lang_code).translate(text) if lang_code != "en" else text
    print(f"Chatbot: {text}")
    path = "./Output/Audio/"
    os.makedirs(path, exist_ok=True)
    temp_file = f"{path}temp_{uuid.uuid4().hex[:8]}.mp3"
    try:
        communicator = edge_tts.Communicate(translated, voice_output)
        await communicator.save(temp_file)
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        start = time.time()
        while pygame.mixer.music.get_busy() and time.time() - start < 30:
            await asyncio.sleep(0.1)
        pygame.mixer.music.stop()
        if os.path.exists(temp_file): os.remove(temp_file)
    except Exception as e:
        print(f"Audio error: {e}")

async def get_confirmed_voice_input(lang_voice, lang_code, voice_output, prompt_text, simple=False):
    prompt = f"{prompt_text}: " if prompt_text else "> "
    if TEXT_MODE:
        return await asyncio.to_thread(input, prompt)
    recognizer = speech_recognition.Recognizer()
    retries = 0
    while retries < 3:
        if prompt_text: await chatbot_speak(prompt_text, lang_code, voice_output)
        with speech_recognition.Microphone() as source:
            print("Listening... 🗣️")
            recognizer.adjust_for_ambient_noise(source, duration=0.7)
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=12)
                captured = recognizer.recognize_google(audio, language=lang_voice)
                if simple: return captured
                
                await chatbot_speak(f"I heard: {captured}. Is that correct?", lang_code, voice_output)
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                confirm_audio = recognizer.listen(source, timeout=8)
                confirm_text = recognizer.recognize_google(confirm_audio, language=lang_voice).lower()
                
                if any(w in confirm_text for w in languages[lang_code]["affirm"]):
                    return GoogleTranslator(source=lang_code, target="en").translate(captured)
            except Exception as e:
                print(f"Recognition error: {e}")
        retries += 1
    fallback_prompt = f"{prompt_text}: " if prompt_text else "Type response: "
    return await asyncio.to_thread(input, fallback_prompt)

# 3. PDF GENERATOR
def generate_pdf(bio, medical):
    os.makedirs("./Output/Summary/", exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(41, 128, 185)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 20, "CLINICAL INTAKE REPORT", ln=True, align="C")
    pdf.ln(25)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, " PATIENT PROFILE", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 11)
    for k, v in bio.items():
        if k != "hashed_name":
            pdf.cell(0, 8, f" {k.capitalize()}: {v}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, " MEDICAL EVALUATION", ln=True, fill=True)
    
    if not medical:
        pdf.cell(0, 10, " No medical data collected.", ln=True)
    else:
        for item in medical:
            urgency = item.get('urgency', 'low')
            if urgency == 'high':
                pdf.set_text_color(255, 0, 0)
            else:
                pdf.set_text_color(41, 128, 185)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 8, f" SYMPTOM: {item.get('symptom','N/A').upper()}", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 10)
            # Dynamic rendering of all AI-extracted keys
            for key, val in item.items():
                if key != 'symptom':
                    pdf.cell(0, 6, f" {key.capitalize()}: {val}", ln=True)
            pdf.ln(2)
            
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 10, f"Generated: {time.strftime('%Y-%m-%d %H:%M')}", align="C")
    pdf.output("./Output/Summary/report.pdf")

# 4. MAIN SYSTEM
async def run_system():
    print("--- Medical Intake Partner Dec 2025 ---")
    user_choice = await asyncio.to_thread(input, "Select Language (English, Hindi, French, Spanish): ")
    user_choice = user_choice.lower().strip()
    if user_choice in languages:
        lang_key = user_choice
    else:
        match = process.extractOne(user_choice, list(languages.keys()))
        lang_key = match[0] if match and match[1] > 75 else "english"
    cfg = languages[lang_key]
    
    # Disclaimer
    await chatbot_speak("Disclaimer: This is not medical advice. Consult a doctor. Proceed?", cfg["code"], cfg["output"])
    consent = await get_confirmed_voice_input(cfg["voice"], cfg["code"], cfg["output"], None, simple=True)
    if not any(w in consent.lower() for w in cfg["affirm"]):
        print("Session ended.")
        return
    
    # Bio Section with Improved Validation
    name = await get_confirmed_voice_input(cfg["voice"], cfg["code"], cfg["output"], "What is your name?")
    raw_age = await get_confirmed_voice_input(cfg["voice"], cfg["code"], cfg["output"], "What is your age?")
    age_match = re.search(r'\d+', raw_age)
    age = age_match.group() if age_match else "Unknown"
    
    gender_raw = await get_confirmed_voice_input(cfg["voice"], cfg["code"], cfg["output"], "What is your gender?")
    gender_std = await call_gemini_with_retry(f"Standardize to 'Male', 'Female', or 'Other': {gender_raw}", is_json=False)
    gender = gender_std if gender_std.lower() in ['male', 'female', 'other'] else "Other"

    # Dynamic Symptom Interview
    raw_input = await get_confirmed_voice_input(cfg["voice"], cfg["code"], cfg["output"], "Briefly, what symptoms are you experiencing?")
    
    symptom_list_data = await call_gemini_with_retry(f"Identify symptoms in: '{raw_input}'. Return ONLY a JSON list of strings or [] if none.", is_json=True)
    symptoms = symptom_list_data if isinstance(symptom_list_data, list) else [raw_input]
    
    medical_data = []
    for i, symp in enumerate(symptoms, 1):
        print(f"Triage ongoing: {symp} ({i}/{len(symptoms)})")
        await chatbot_speak(f"Processing symptom {i} of {len(symptoms)}.", cfg["code"], cfg["output"])
        history = f"Initial statement: {raw_input}. "
        while True:
            # Clinical "Justification" logic
            state = await call_gemini_with_retry(f"Acting as a triage doctor for {symp}. Context: {history[-2000:]}. Ask ONE justified question (red flags, severity) or set complete=true.", True)
            await asyncio.sleep(2)  # Rate limit
            if state.get("complete", True): break
            ans = await get_confirmed_voice_input(cfg["voice"], cfg["code"], cfg["output"], state.get("question"))
            history += f"Q: {state.get('question')} A: {ans}. "
        
        extract_prompt = f"Synthesize medical triage for {symp} from: {history}. Return ONLY JSON dict with keys: 'severity' (int 1-10), 'duration' (str), 'urgency' (low/med/high), 'summary' (2 sentences)."
        summary_data = await call_gemini_with_retry(extract_prompt, is_json=True)
        await asyncio.sleep(2)
        # Ensure data integrity for PDF
        if isinstance(summary_data, dict):
            summary_data['symptom'] = symp
            medical_data.append(summary_data)
        else:
            medical_data.append({"symptom": symp, "severity": "Unknown", "duration": "Unknown", "urgency": "low", "summary": "Data extraction failed for this symptom."})

    # Final Summary & Correction Loop
    while True:
        playback = f"Confirming for {name}, age {age}. "
        for m in medical_data:
            playback += f"Symptom: {m.get('symptom')}. Severity: {m.get('severity', 'N/A')}, Urgency: {m.get('urgency', 'low')}. Summary: {m.get('summary', '')[:50]}. "
        
        # Split long playback
        chunks = [playback[i:i+800] for i in range(0, len(playback), 800)]
        for chunk in chunks:
            await chatbot_speak(chunk, cfg["code"], cfg["output"])
            await asyncio.sleep(1)
        await chatbot_speak("Is this information correct?", cfg["code"], cfg["output"])
        
        correction_input = await get_confirmed_voice_input(cfg["voice"], cfg["code"], cfg["output"], None, simple=True)
        
        if any(w in correction_input.lower() for w in cfg["affirm"]): break
        
        await chatbot_speak("Please tell me the correction.", cfg["code"], cfg["output"])
        user_fix = await get_confirmed_voice_input(cfg["voice"], cfg["code"], cfg["output"], None, simple=True)
        update_prompt = f"Update this clinical data: {json.dumps(medical_data)} with this user correction: '{user_fix}'. Return updated JSON list of dicts."
        updated_data = await call_gemini_with_retry(update_prompt, is_json=True)
        await asyncio.sleep(2)
        if isinstance(updated_data, list): medical_data = updated_data

    # Save and Export
    bio = {"name": name, "age": age, "gender": gender, "hashed_name": hashlib.sha256(name.encode()).hexdigest()}
    generate_pdf(bio, medical_data)
    
    if MONGO_URI:
        try:
            db_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=30000, connectTimeoutMS=10000)
            db = db_client[os.getenv("DB_NAME", "HealthBot")]
            db['patients'].update_one(
                {"hashed_name": bio["hashed_name"]},
                {"$set": {**bio, "medical": medical_data, "time": time.time()}},
                upsert=True
            )
            print("Database entry created/updated.")
        except Exception as e:
            print(f"DB connectivity issue: {e}")
    
    print("\n[Clinical Report finalized in ./Output/Summary/report.pdf]")

if __name__ == "__main__":
    try:
        asyncio.run(run_system())
    except KeyboardInterrupt:
        print("\nSession ended by user.")
    except Exception as e:
        print(f"Critical System Failure: {e}")
        print(traceback.format_exc())
    finally:
        pygame.mixer.quit()
