import json
import time
from fpdf import FPDF
import speech_recognition
import pyttsx3
import asyncio
import edge_tts
from deep_translator import GoogleTranslator
import IPython.display as ipd
import pygame

Lang = ["english","hindi","french","spanish"]

languages = {
    "1": {"code": "en", "name": "English", "voice": "en-US-JennyNeural"},
    "2": {"code": "hi", "name": "Hindi", "voice": "hi-IN-SwaraNeural"},
    "3": {"code": "fr", "name": "French", "voice": "fr-FR-DeniseNeural"},
    "4": {"code": "es", "name": "Spanish", "voice": "es-ES-ElviraNeural"}}

def translate1(lang, text):
    text1 = GoogleTranslator(source=lang,target="en").translate(text)
    return text1

def translate2(lang, text):
    text1 = GoogleTranslator(source="en",target=lang).translate(text)
    return text1

print("Avaliable Languages:- ")
for i in Lang:
    print(i.capitalize())

while True:
    print("\nChatbot: Enter your preferred language.")
    language = input("You: ").lower()
    if language in Lang:
        break
    else:
        print("Chatbot: Not a valid language. Please select again.")
    
if language == "english":
    language = "en"
    language_voice = "en-US"
    language_output = "en-US-JennyNeural"
elif language == "hindi":
    language = "hi"
    language_voice = "hi-IN"
    language_output = "hi-IN-SwaraNeural"
elif language == "french":
    language = "fr"
    language_voice = "fr-FR"
    language_output = "fr-FR-DeniseNeural"
elif language == "spanish":
    language = "es"
    language_voice = "es-ES"
    language_output = "es-ES-ElviraNeural"

f = open("/home/prabal/Downloads/FOdleeeer/foldeeer/gravityFalls/symptoms_1.json",'r')
information = json.load(f)
f.close()

def extract_symptoms():
    symp = []
    for i in information:
        symp.append(i["code"].lower())
    return symp

symp = extract_symptoms()

def inp():
    user = input("You: ")
    user = translate1(language,user)
    return user

file = "/home/prabal/Downloads/FOdleeeer/foldeeer/gravityFalls/Output/Audio/audio_output.mp3"

async def play(s):
    file = f"/home/prabal/Downloads/FOdleeeer/foldeeer/gravityFalls/Output/Audio/{int(time.time())}.mp3"
    await edge_tts.Communicate(s,language_output).save(file)
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

async def ter(s):
    if s.startswith("Chatbot:"):
        k = s[8:]
    else:
        k = s
    k = translate2(language,k)
    await play(k)
    for i in range(len(s)-1):
        print(s[i],end='')
        time.sleep(0.02)
    print(s[len(s)-1])

async def ter1(s):
    if s.startswith("Chatbot:"):
        k = s[8:]
    else:
        k=s
    k = translate2(language,k)
    await play(k)
    for i in s:
        print(i,end='')
        time.sleep(0.03)



def vinp():
    text1 = ""
    point = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as s:
        print("Please speak now.....🗣️")
        a = 0
        b = 0
        while True:
            audio = point.listen(s)
            try:
                text1 = point.recognize_google(audio, language=language_voice)
                print("Chatbot: Audio captured.")
                a = 1
                break
            except:
                print("There is an error recogonizing the speech. Can you please repeat?....")
                b+=1
                if b==3:
                    text1 = inp()
                    break
            if a==1:break
        text1 = translate1(language,text1)
        return text1.lower()





async def frequen(symptoms,finish):
    L = ["How often do you experience ","(Rarely, Occasionally, Frequently, All the time)"]
    L1 = []
    for j in range(len(symptoms)):
        await ter("Chatbot: "+L[0]+symptoms[j]+" "+L[1])
        l = 0
        while True:
            if l<1:
                freq = inp()
            else:
                freq = inp()
            fr = freq.split()
            d = 0
            for i in fr:
                if i in finish:
                    await ter("Chatbot: Thank you. Have a great day!")
                    d = 1
                    break
            if d==1:
                return [1]
            for i in range(len(fr)):
                fr[i] = fr[i].lower()
            f = ["rarely","occasionally","frequently","all the time"]
            frequency = ""
            for i in f:
                if i in freq:
                    frequency = i
                    L1.append(frequency)
                    break
            if frequency == "":
                await ter("Chatbot: Sorry, I am not able to understand the frequency of your symptoms. Please choose form "+L[1])
                l+=1
                continue
            else:
                break
    return L1

async def severe(symptoms,finish):
    scale = ["1","2","3","4","5","6","7","8","9","10"]
    L1 = []
    for j in range(len(symptoms)):
        await ter("Chatbot: On a scale of 1-10, how severe is your "+symptoms[j]+"?")
        l = 0
        while True:
            if l<1:
                s = inp()
            else:
                s = inp()
            sr = s.split()
            d = 0
            for i in sr:
                if i in finish:
                    await ter("Chatbot: Thank you. Have a great day!")
                    d = 1
                    break
            if d==1:
                return [1]
            A = False
            for k in sr:
                if k in scale:
                    L1.append(k)
                    A = True
                    break
            if A == False:
                await ter("Chatbot: Sorry, I cannot able to interpret the severity of the symptom. Please enter in scale of (1-10).")
                l+=1
                continue
            if A == True:
                break
    return L1

async def duration(symptoms,finish):
    L1=[]
    for j in range(len(symptoms)):
        await ter("Chatbot: From how long are you experiencing "+symptoms[j]+"?")
        l = 0
        while True:
            if l<1:
                dur = inp().split()
            else:
                dur = inp().split()
            f=0
            for i in dur:
                if i in finish:
                    await ter("Chatbot: Thank you. Have a great day!")
                    f = 1
                    break
            if f==1:
                return [1]
            scale1 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50']
            A = False
            for i in range(len(dur)):
                if dur[i] in scale1:
                    duration = dur[i]+" "+dur[i+1]
                    L1.append(duration)
                    A = True
                    break
            if A == False:
                await ter("Chatbot: Sorry, I am not able to understand the duration. Can you please describe it again?")
                l+=1
            elif A == True:
                break
    return L1

def report(d, summary):
    file = "/home/prabal/Downloads/FOdleeeer/foldeeer/gravityFalls/Output/Summary/patient_report.pdf"
    pointer = FPDF()
    pointer.add_page()
    pointer.set_font("Courier", size=25)
    pointer.cell(200, 10, "PATIENT REPORT")
    pointer.ln(10)
    pointer.set_font("Courier", size=14)
    pointer.cell(200, 10, "Patient Details", border='B')
    pointer.ln(10)

    for k, v in d.items():
        pointer.cell(40, 10, k)
        pointer.cell(40, 10, v)
        pointer.ln(8)
    pointer.ln(12)  
    
    pointer.set_font("Courier", size=14)
    pointer.cell(200, 10, "Summary", border='B')
    pointer.ln(10)
    pointer.set_font("Arial", size=15)
    pointer.ln(6)
    pointer.cell(15,10,"S.No",border=1)
    pointer.cell(30, 10, "Symptoms",border=1)
    pointer.cell(30, 10, "Frequency",border=1)
    pointer.cell(30, 10, "Severity",border=1)
    pointer.cell(30, 10, "Duration",border=1)
    pointer.cell(50, 10, "Additional Notes",border=1)
    pointer.ln(10)
    k=0
    for a in summary:
        pointer.cell(15,10,str(k+1),border=1)
        pointer.cell(30, 10, a["symptom"], border=1)
        pointer.cell(30, 10, a["frequency"], border=1)
        pointer.cell(30, 10, a["severity"], border=1)
        pointer.cell(30, 10, a["duration"], border=1)
        pointer.cell(50, 10, a["additional"], border=1)
        pointer.ln(10)
        k+=1

    pointer.output(file)
    print("Patient report successfully saved.")

async def assistant_chatbot():
    await ter("Chatbot: Hi There!")
    await ter("Chatbot: I am your medical assistant chatbot.")
    await ter("Chatbot: What is your name sir/mam?")
    name = inp()
    await ter("Chatbot: What is your age?")
    age = inp()
    await ter("Chatbot: What is your gender?")
    gender = inp()
    await ter("Chatbot: Please provide your contact number.")
    c_number = inp()
    await ter("Chatbot: Thanks")
    det = {"Name": name, "Age": age, "Gender": gender, "Contact": c_number}
    print(det)
    await ter("Chatbot: Please describe your symptoms.")
    q = 0
    while True:
        symptoms = []
        if q<1:
            user = inp().split()
        else:
            user = inp().split()
        str_user = " ".join(user)
        finish = ["end","quit","terminate"]
        for i in range(len(user)):
            user[i] = user[i].lower()
        c = 0
        for i in user:
            if i in finish:
                time.sleep(1)
                await ter("Chatbot: Thank you. Have a great day!")
                c = 1
                break
        if c == 1:
            break
        index = []
        for i in range(len(user)):
            if len(user[i]) < 4:
                index.append(i)
        index = index[::-1]
        for i in index:
            user.pop(i)
        for i in symp:
            if i in str_user:
                symptoms.append(i)
        if len(symptoms) == 0:
            await ter("Chatbot: Sorry, I am not able to understand your symptoms. Can you please describe it in more details?")
            q+=1
            continue
        else:break
    if c!=1:
        L_f = await frequen(symptoms,finish)
        d = 0
        for i in L_f:
            if i == 1:
                d=1
                break
        if d!=1:
            L_s = await severe(symptoms,finish)
            e = 0
            for i in L_s:
                if i == 1:
                    e=1
                    break
            if e!=1:
                L_d = await duration(symptoms,finish)
                p = 0
                for i in L_s:
                    if i == 1:
                        p=1
                        break
    if c==1 or d==1 or e==1 or p==1:
        pass
    else:
        summary = []
        for i in range(len(symptoms)):
            D={}
            D["symptom"] = symptoms[i]
            D["frequency"] = L_f[i]
            D["severity"] = L_s[i]
            D["duration"] = L_d[i]
            await ter("Chatbot: Do you want to provide any additional information for "+symptoms[i]+" or any medical history?")
            A_i = inp()
            D["additional"] = A_i
            summary.append(D)
        summ = ""
        freq = ""
        sever = ""
        durat = ""
        for i in range(len(symptoms)):
            summ += summary[i]["symptom"]
            freq += summary[i]["frequency"]
            sever += summary[i]["severity"]
            durat += summary[i]["duration"]
        rep = f"""
        Patient Summary for Doctor:
        ○ Name: {name}
        ○ Symptoms: {summ}
        ○ Frequency of Symptoms: {freq}
        ○ Severity of Symptoms: {sever}
        ○ Duration of Symptoms: {durat}
        """
        await ter(rep)
        await ter("Chatbot: Thank you. This information will be helpful for doctors to have a clear understanding of the disease.")
        D["name"] = name
        D["age"] = age
        D["gender"] = gender
        D["contact"] = c_number
        report(det,summary)
        return D

async def main():
    D = await assistant_chatbot()
    return D

D = asyncio.run(main())


import os
import base64
import pymongo
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption
import json


encryption_key = os.urandom(96)  
# print("Generated Encryption Key (Base64, for storage):", base64.b64encode(encryption_key).decode())


uri = "mongodb+srv://Admin:admin_password@chatbot-module-3.g7yk7.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["Chatbot-module-3"]
collection = db['patients']


key_vault_namespace = "encryption.__keyVault"
kms_providers = {"local": {"key": encryption_key}} 

client_encryption = ClientEncryption(
    kms_providers,
    key_vault_namespace,
    client,
    client.codec_options
)

encryption_key_id = client_encryption.create_data_key("local")
# print("Encryption Key ID:", encryption_key_id)

SYMPTOM_FILE_PATH = "/home/prabal/Downloads/symptoms_1.json"

with open(SYMPTOM_FILE_PATH, 'r') as f:
    information = json.load(f)

def extract_symptoms():
    return [i["code"].lower() for i in information]

symp = extract_symptoms()

def encrypt_data(value):
    return client_encryption.encrypt(
        value,
        "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
        encryption_key_id
    )

def decrypt_data(encrypted_value):
    return client_encryption.decrypt(encrypted_value)


patient_document = {
    "name": D["name"],
    "age": D["age"],  
    "gender": D["gender"],
    "contact": encrypt_data(D["contact"]),  
    "symptom": D["symptom"],
    "frequency" :  D["frequency"],
    "duration" : D["duration"],
    "severity" : D["severity"],
    "Additional_notes": D["additional"]
}

collection.insert_one(patient_document)

def fetch_patient_data():
    user_role = input("Enter your role (admin/doctor): ").strip().lower()

    patient = collection.find_one({}, sort=[("_id", -1)])
    
    if patient:  
        
        if user_role == "admin":
            print(f"Name: {patient['name']}")
            print(f"Age: {patient['age']}")
            print(f"Gender: {patient['gender']}")
            print(f"Contact: {decrypt_data(patient['contact'])}")
            print(f"Symptoms: {patient['symptom']}")
            print(f"Frequency: {patient['frequency']}")
            print(f"Duration: {patient['duration']}")
            print(f"Severity: {patient['severity']}")
            return 0
            
        
        elif user_role == "doctor":
            print(f"Name: {patient['name']}")
            print(f"Age : {patient['age']}")
            print(f"Gender: {patient['gender']}")
            print(f"Contact (Encrypted): {patient['contact']}")
            print(f"Symptoms : {patient['symptom']}")
            print(f"Frequency: {patient['frequency']}")
            print(f"Duration: {patient['duration']}")
            print(f"Severity: {patient['severity']}")
            return 0
        
        else:
            print("Unauthorized access")
    else:
        print("No patient records found in the database.")

fetch_patient_data()
