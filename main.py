
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import urllib.request
import urllib.parse
import json

app = Flask(__name__, static_folder=".", static_url_path="/")
CORS(app)

GOOGLE_SEARCH_API_KEY = os.environ.get('GOOGLE_SEARCH_API_KEY', '')
GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID', '')

FAKE_HOSPITALS = [
    {
        "name": "City General Hospital",
        "address": "123 Main Street, Downtown",
        "phone": "+1-555-0100",
        "distance": "0.5 km"
    },
    {
        "name": "St. Mary's Medical Center",
        "address": "456 Oak Avenue, Midtown",
        "phone": "+1-555-0200",
        "distance": "1.2 km"
    },
    {
        "name": "Emergency Care Hospital",
        "address": "789 Pine Road, Eastside",
        "phone": "+1-555-0300",
        "distance": "2.1 km"
    }
]

LANGUAGE_PROMPTS = {
    'en': {
        'prefix': 'Health information about:',
        'disclaimer': '\n\n⚠ Disclaimer: This is general information only. Please consult a healthcare professional for medical advice.'
    },
    'hi': {
        'prefix': 'स्वास्थ्य जानकारी:',
        'disclaimer': '\n\n⚠ अस्वीकरण: यह केवल सामान्य जानकारी है। चिकित्सा सलाह के लिए कृपया स्वास्थ्य पेशेवर से परामर्श करें।'
    }
}

DEMO_HEALTH_INFO = {
    'fever': {
        'en': '''🌡 Fever Information:

Symptoms:
- Body temperature above 100.4°F (38°C)
- Sweating and chills
- Headache
- Muscle aches
- Weakness

Common Causes:
- Viral infections (flu, cold)
- Bacterial infections
- Heat exhaustion
- Certain medications

Treatment:
- Rest and drink plenty of fluids
- Take fever-reducing medication (acetaminophen, ibuprofen)
- Cool compress on forehead
- Wear light clothing

When to see a doctor:
- Fever above 103°F (39.4°C)
- Fever lasting more than 3 days
- Severe headache or rash
- Difficulty breathing''',
        'hi': '''🌡 बुखार की जानकारी:

लक्षण:
- शरीर का तापमान 100.4°F (38°C) से ऊपर
- पसीना और ठंड लगना
- सिरदर्द
- मांसपेशियों में दर्द
- कमजोरी

सामान्य कारण:
- वायरल संक्रमण (फ्लू, सर्दी)
- बैक्टीरियल संक्रमण
- गर्मी लगना
- कुछ दवाएं

उपचार:
- आराम करें और खूब तरल पदार्थ पिएं
- बुखार कम करने की दवा लें (पैरासिटामोल, इबुप्रोफेन)
- माथे पर ठंडी पट्टी
- हल्के कपड़े पहनें

डॉक्टर को कब दिखाएं:
- 103°F (39.4°C) से अधिक बुखार
- 3 दिन से अधिक समय तक बुखार
- गंभीर सिरदर्द या चकत्ते
- सांस लेने में कठिनाई'''
    },
    'headache': {
        'en': '''🤕 Headache Information:

Common Types:
- Tension headache (most common)
- Migraine
- Cluster headache
- Sinus headache

Symptoms:
- Pain in head, scalp, or neck
- Pressure or tightness
- Sensitivity to light/sound (migraine)

Treatment:
- Rest in a quiet, dark room
- Apply cold or warm compress
- Take pain relievers (ibuprofen, aspirin)
- Stay hydrated
- Avoid triggers (stress, certain foods)

When to see a doctor:
- Sudden, severe headache
- Headache with fever, stiff neck
- Vision changes
- Difficulty speaking''',
        'hi': '''🤕 सिरदर्द की जानकारी:

सामान्य प्रकार:
- तनाव सिरदर्द (सबसे आम)
- माइग्रेन
- क्लस्टर सिरदर्द
- साइनस सिरदर्द

लक्षण:
- सिर, खोपड़ी या गर्दन में दर्द
- दबाव या जकड़न
- प्रकाश/ध्वनि के प्रति संवेदनशीलता (माइग्रेन)

उपचार:
- शांत, अंधेरे कमरे में आराम करें
- ठंडी या गर्म पट्टी लगाएं
- दर्द निवारक लें (इबुप्रोफेन, एस्पिरिन)
- हाइड्रेटेड रहें
- ट्रिगर्स से बचें (तनाव, कुछ खाद्य पदार्थ)

डॉक्टर को कब दिखाएं:
- अचानक, गंभीर सिरदर्द
- बुखार, गर्दन में अकड़न के साथ सिरदर्द
- दृष्टि में बदलाव
- बोलने में कठिनाई'''
    },
    'cough': {
        'en': '''😷 Cough Information:

Types:
- Dry cough
- Wet/productive cough
- Chronic cough (lasting >8 weeks)

Common Causes:
- Common cold or flu
- Allergies
- Asthma
- Acid reflux

Treatment:
- Stay hydrated
- Use honey (for adults)
- Cough drops or lozenges
- Humidifier to add moisture to air
- Avoid irritants (smoke, dust)

When to see a doctor:
- Cough lasting more than 3 weeks
- Coughing up blood
- Difficulty breathing
- High fever''',
        'hi': '''😷 खांसी की जानकारी:

प्रकार:
- सूखी खांसी
- गीली/उत्पादक खांसी
- पुरानी खांसी (8 सप्ताह से अधिक)

सामान्य कारण:
- सामान्य सर्दी या फ्लू
- एलर्जी
- अस्थमा
- एसिड रिफ्लक्स

उपचार:
- हाइड्रेटेड रहें
- शहद का उपयोग करें (वयस्कों के लिए)
- खांसी की गोलियां
- हवा में नमी जोड़ने के लिए ह्यूमिडिफायर
- परेशान करने वाली चीजों से बचें (धुआं, धूल)

डॉक्टर को कब दिखाएं:
- 3 सप्ताह से अधिक खांसी
- खून के साथ खांसी
- सांस लेने में कठिनाई
- तेज बुखार'''
    },
    'cold': {
        'en': '''🤧 Cold/Flu Information:

Symptoms:
- Runny or stuffy nose
- Sore throat
- Sneezing
- Mild fever
- Body aches

Treatment:
- Rest plenty
- Drink warm fluids
- Gargle with salt water
- Use steam inhalation
- Take over-the-counter cold medicine

Prevention:
- Wash hands frequently
- Avoid close contact with sick people
- Cover mouth when coughing

When to see a doctor:
- Symptoms lasting more than 10 days
- High fever (above 103°F)
- Severe sore throat
- Difficulty breathing''',
        'hi': '''🤧 सर्दी/फ्लू की जानकारी:

लक्षण:
- बहती या बंद नाक
- गले में खराश
- छींक आना
- हल्का बुखार
- शरीर में दर्द

उपचार:
- भरपूर आराम करें
- गर्म तरल पदार्थ पिएं
- नमक के पानी से गरारे करें
- भाप लें
- काउंटर पर मिलने वाली सर्दी की दवा लें

रोकथाम:
- बार-बार हाथ धोएं
- बीमार लोगों के करीब संपर्क से बचें
- खांसते समय मुंह ढकें

डॉक्टर को कब दिखाएं:
- 10 दिन से अधिक लक्षण
- तेज बुखार (103°F से ऊपर)
- गंभीर गले में खराश
- सांस लेने में कठिनाई'''
    },
    'stomach': {
        'en': '''🤢 Stomach Pain Information:

Common Causes:
- Indigestion
- Gas or bloating
- Food poisoning
- Gastritis
- Peptic ulcer

Symptoms:
- Abdominal pain or cramping
- Nausea
- Bloating
- Loss of appetite

Treatment:
- Avoid spicy and fatty foods
- Eat small, frequent meals
- Drink plenty of water
- Use antacids for heartburn
- Apply warm compress to abdomen

When to see a doctor:
- Severe or persistent pain
- Blood in stool or vomit
- Sudden, severe abdominal pain
- Pain with fever''',
        'hi': '''🤢 पेट दर्द की जानकारी:

सामान्य कारण:
- अपच
- गैस या सूजन
- फूड पॉइजनिंग
- गैस्ट्राइटिस
- पेप्टिक अल्सर

लक्षण:
- पेट में दर्द या ऐंठन
- मतली
- सूजन
- भूख न लगना

उपचार:
- मसालेदार और वसायुक्त भोजन से बचें
- छोटे, बार-बार भोजन करें
- खूब पानी पिएं
- सीने की जलन के लिए एंटासिड का उपयोग करें
- पेट पर गर्म सेक करें

डॉक्टर को कब दिखाएं:
- गंभीर या लगातार दर्द
- मल या उल्टी में खून
- अचानक, गंभीर पेट दर्द
- बुखार के साथ दर्द'''
    },
    'diarrhea': {
        'en': '''💩 Diarrhea Information:

Causes:
- Viral or bacterial infection
- Food intolerance
- Contaminated food or water
- Medications

Treatment:
- Drink plenty of fluids (ORS, water)
- Eat bland foods (rice, banana, toast)
- Avoid dairy, caffeine, alcohol
- Take probiotics
- Rest

Prevention:
- Wash hands before eating
- Drink clean water
- Avoid street food

When to see a doctor:
- Diarrhea lasting more than 2 days
- Severe dehydration
- Blood in stool
- High fever''',
        'hi': '''💩 दस्त की जानकारी:

कारण:
- वायरल या बैक्टीरियल संक्रमण
- भोजन असहिष्णुता
- दूषित भोजन या पानी
- दवाएं

उपचार:
- खूब तरल पदार्थ पिएं (ORS, पानी)
- सादा भोजन खाएं (चावल, केला, टोस्ट)
- डेयरी, कैफीन, शराब से बचें
- प्रोबायोटिक्स लें
- आराम करें

रोकथाम:
- खाने से पहले हाथ धोएं
- साफ पानी पिएं
- स्ट्रीट फूड से बचें

डॉक्टर को कब दिखाएं:
- 2 दिन से अधिक दस्त
- गंभीर निर्जलीकरण
- मल में खून
- तेज बुखार'''
    },
    'diabetes': {
        'en': '''🩺 Diabetes Information:

Types:
- Type 1 Diabetes
- Type 2 Diabetes
- Gestational Diabetes

Symptoms:
- Increased thirst and urination
- Unexplained weight loss
- Fatigue
- Blurred vision
- Slow-healing wounds

Management:
- Monitor blood sugar regularly
- Take prescribed medications
- Follow diabetic diet
- Regular exercise
- Maintain healthy weight

Prevention (Type 2):
- Eat healthy diet
- Exercise regularly
- Maintain healthy weight
- Limit sugar intake''',
        'hi': '''🩺 मधुमेह की जानकारी:

प्रकार:
- टाइप 1 मधुमेह
- टाइप 2 मधुमेह
- गर्भावस्था मधुमेह

लक्षण:
- अधिक प्यास और पेशाब
- अस्पष्ट वजन घटना
- थकान
- धुंधली दृष्टि
- धीरे-धीरे ठीक होने वाले घाव

प्रबंधन:
- नियमित रूप से ब्लड शुगर मॉनिटर करें
- निर्धारित दवाएं लें
- मधुमेह आहार का पालन करें
- नियमित व्यायाम
- स्वस्थ वजन बनाए रखें

रोकथाम (टाइप 2):
- स्वस्थ आहार लें
- नियमित व्यायाम करें
- स्वस्थ वजन बनाए रखें
- चीनी का सेवन सीमित करें'''
    },
    'blood pressure': {
        'en': '''❤ High Blood Pressure Information:

Symptoms:
- Often no symptoms (silent killer)
- Headaches
- Shortness of breath
- Nosebleeds
- Chest pain

Risk Factors:
- Family history
- Obesity
- High salt diet
- Lack of exercise
- Stress

Management:
- Take prescribed medications
- Reduce salt intake
- Exercise regularly
- Maintain healthy weight
- Limit alcohol
- Manage stress
- Quit smoking''',
        'hi': '''❤ उच्च रक्तचाप की जानकारी:

लक्षण:
- अक्सर कोई लक्षण नहीं (साइलेंट किलर)
- सिरदर्द
- सांस की तकलीफ
- नकसीर
- सीने में दर्द

जोखिम कारक:
- पारिवारिक इतिहास
- मोटापा
- उच्च नमक आहार
- व्यायाम की कमी
- तनाव

प्रबंधन:
- निर्धारित दवाएं लें
- नमक का सेवन कम करें
- नियमित व्यायाम करें
- स्वस्थ वजन बनाए रखें
- शराब सीमित करें
- तनाव प्रबंधित करें
- धूम्रपान छोड़ें'''
    },
    'asthma': {
        'en': '''🫁 Asthma Information:

Symptoms:
- Shortness of breath
- Wheezing
- Chest tightness
- Coughing (especially at night)

Common Triggers:
- Allergens (dust, pollen, pet dander)
- Air pollution
- Cold air
- Exercise
- Stress

Management:
- Use prescribed inhalers
- Avoid triggers
- Take controller medications
- Have rescue inhaler always
- Monitor symptoms

When to see a doctor:
- Frequent asthma attacks
- Symptoms not controlled
- Emergency: severe breathing difficulty''',
        'hi': '''🫁 अस्थमा की जानकारी:

लक्षण:
- सांस की तकलीफ
- घरघराहट
- सीने में जकड़न
- खांसी (खासकर रात में)

सामान्य ट्रिगर:
- एलर्जेन (धूल, पराग, पालतू जानवर)
- वायु प्रदूषण
- ठंडी हवा
- व्यायाम
- तनाव

प्रबंधन:
- निर्धारित इनहेलर का उपयोग करें
- ट्रिगर्स से बचें
- कंट्रोलर दवाएं लें
- रेस्क्यू इनहेलर हमेशा रखें
- लक्षणों की निगरानी करें

डॉक्टर को कब दिखाएं:
- बार-बार अस्थमा के दौरे
- लक्षण नियंत्रित नहीं
- आपातकाल: गंभीर सांस लेने में कठिनाई'''
    },
    'back pain': {
        'en': '''🦴 Back Pain Information:

Common Causes:
- Muscle strain
- Poor posture
- Herniated disc
- Arthritis
- Lack of exercise

Treatment:
- Rest (but avoid prolonged bed rest)
- Apply hot/cold packs
- Gentle stretching exercises
- Pain relievers (ibuprofen)
- Improve posture
- Strengthen core muscles

Prevention:
- Exercise regularly
- Maintain good posture
- Lift heavy objects properly
- Maintain healthy weight

When to see a doctor:
- Severe pain lasting weeks
- Pain radiating to legs
- Numbness or weakness
- Loss of bladder control''',
        'hi': '''🦴 पीठ दर्द की जानकारी:

सामान्य कारण:
- मांसपेशियों में खिंचाव
- खराब मुद्रा
- हर्नियेटेड डिस्क
- गठिया
- व्यायाम की कमी

उपचार:
- आराम (लेकिन लंबे समय तक बिस्तर पर आराम से बचें)
- गर्म/ठंडे पैक लगाएं
- धीरे से स्ट्रेचिंग व्यायाम
- दर्द निवारक (इबुप्रोफेन)
- मुद्रा में सुधार करें
- कोर मांसपेशियों को मजबूत करें

रोकथाम:
- नियमित व्यायाम करें
- अच्छी मुद्रा बनाए रखें
- भारी वस्तुओं को सही तरीके से उठाएं
- स्वस्थ वजन बनाए रखें

डॉक्टर को कब दिखाएं:
- हफ्तों तक गंभीर दर्द
- पैरों में दर्द फैलना
- सुन्नता या कमजोरी
- मूत्राशय नियंत्रण का नुकसान'''
    },
    'allergy': {
        'en': '''🤧 Allergy Information:

Common Types:
- Food allergies
- Seasonal allergies (hay fever)
- Dust/mold allergies
- Pet allergies
- Insect sting allergies

Symptoms:
- Sneezing, runny nose
- Itchy eyes
- Skin rash or hives
- Swelling
- Difficulty breathing (severe)

Treatment:
- Avoid known allergens
- Antihistamines
- Nasal sprays
- Eye drops
- For severe: carry epinephrine auto-injector

Prevention:
- Identify triggers
- Keep environment clean
- Use air purifiers
- Check food labels''',
        'hi': '''🤧 एलर्जी की जानकारी:

सामान्य प्रकार:
- भोजन एलर्जी
- मौसमी एलर्जी (हे फीवर)
- धूल/मोल्ड एलर्जी
- पालतू जानवर एलर्जी
- कीट के डंक से एलर्जी

लक्षण:
- छींक आना, बहती नाक
- आंखों में खुजली
- त्वचा पर चकत्ते या पित्ती
- सूजन
- सांस लेने में कठिनाई (गंभीर)

उपचार:
- ज्ञात एलर्जेन से बचें
- एंटीहिस्टामाइन
- नाक स्प्रे
- आई ड्रॉप्स
- गंभीर के लिए: एपिनेफ्रिन ऑटो-इंजेक्टर रखें

रोकथाम:
- ट्रिगर्स की पहचान करें
- पर्यावरण को साफ रखें
- एयर प्यूरीफायर का उपयोग करें
- भोजन लेबल जांचें'''
    }
}

def get_demo_response(query, language):
    query_lower = query.lower()
    
    for keyword, info in DEMO_HEALTH_INFO.items():
        if keyword in query_lower:
            return info.get(language, info['en'])
    
    if language == 'hi':
        return f'''आपकी क्वेरी के बारे में: {query}

यह एक डेमो स्वास्थ्य सहायक है। निम्नलिखित रोगों के बारे में जानकारी उपलब्ध है:
- बुखार (fever)
- सिरदर्द (headache)  
- खांसी (cough)
- सर्दी/फ्लू (cold)
- पेट दर्द (stomach pain)
- दस्त (diarrhea)
- मधुमेह (diabetes)
- उच्च रक्तचाप (blood pressure)
- अस्थमा (asthma)
- पीठ दर्द (back pain)
- एलर्जी (allergy)

⚠ अस्वीकरण: यह केवल सामान्य जानकारी है। चिकित्सा सलाह के लिए कृपया स्वास्थ्य पेशेवर से परामर्श करें।'''
    else:
        return f'''About your query: {query}

This is a demo health assistant. Information available for common diseases:
- fever
- headache
- cough
- cold/flu
- stomach pain
- diarrhea
- diabetes
- blood pressure
- asthma
- back pain
- allergy

⚠ Disclaimer: This is general information only. Please consult a healthcare professional for medical advice.'''

def search_disease_info(query, language='en'):
    lang_config = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS['en'])
    
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
        demo_response = get_demo_response(query, language)
        return demo_response
    
    try:
        search_query = f"{lang_config['prefix']} {query} symptoms treatment causes"
        
        url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_SEARCH_API_KEY}&cx={GOOGLE_SEARCH_ENGINE_ID}&q={urllib.parse.quote(search_query)}"
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        if 'items' in data and len(data['items']) > 0:
            results = []
            for i, item in enumerate(data['items'][:3]):
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                link = item.get('link', '')
                results.append(f"{i+1}. {title}\n{snippet}\nSource: {link}")
            
            response_text = '\n\n'.join(results)
            response_text += lang_config['disclaimer']
            return response_text
        else:
            return f"No information found for: {query}{lang_config['disclaimer']}"
            
    except Exception as e:
        demo_response = get_demo_response(query, language)
        return demo_response

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    language = data.get("language", "en")
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    response = search_disease_info(message, language)
    
    return jsonify({
        "reply": response,
        "language": language
    })

@app.route("/api/emergency", methods=["POST"])
def emergency():
    data = request.get_json() or {}
    language = data.get("language", "en")
    
    emergency_messages = {
        'en': '🚨 EMERGENCY - Nearest Hospitals:',
        'hi': '🚨 आपातकाल - निकटतम अस्पताल:'
    }
    
    message = emergency_messages.get(language, emergency_messages['en'])
    
    hospital_list = []
    for hospital in FAKE_HOSPITALS:
        hospital_info = f"\n\n📍 {hospital['name']}\n📞 {hospital['phone']}\n📍 {hospital['address']}\n📏 Distance: {hospital['distance']}"
        hospital_list.append(hospital_info)
    
    response = message + ''.join(hospital_list)
    
    call_911 = {
        'en': '\n\n⚠ For life-threatening emergencies, call 911 immediately!',
        'hi': '\n\n⚠ जीवन के लिए खतरनाक आपातकाल के लिए, तुरंत 911 पर कॉल करें!'
    }
    
    response += call_911.get(language, call_911['en'])
    
    return jsonify({
        "reply": response,
        "hospitals": FAKE_HOSPITALS
    })

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)