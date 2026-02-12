# pyre-ignore-all-errors
from flask import Flask, render_template, request, jsonify, session
import string
import math
from collections import Counter
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

app = Flask(__name__)
app.secret_key = 'your-secret-key-for-session-management-2026'  # Required for sessions

# --- SESSION-BASED CONVERSATION CONTEXT ---
# This will store conversation history per user session
conversation_contexts = {}

# --- 1. SYNONYM DICTIONARY (THE BRAIN) ---
NORMALIZATION_MAP = {
    # FEES & MONEY
    "fees": "fee", "fee": "fee",
    "tuition": "fee", "dues": "fee",
    "cost": "fee", "costs": "fee",
    "price": "fee", "pricing": "fee",
    "payment": "fee", "pay": "fee",
    "amount": "fee", "expense": "fee",
    "lakh": "fee", "lakhs": "fee", "rs": "fee", "rupees": "fee",

    # TIMINGS & SCHEDULE
    "timings": "time", "time": "time",
    "schedule": "time", "scheduled": "time",
    "hours": "time", "hour": "time",
    "open": "time", "opening": "time", "closes": "time",
    "working": "time", "days": "time", "shift": "time",

    # CONTACT
    "contacts": "contact", "contact": "contact",
    "phone": "contact", "mobile": "contact", "cell": "contact",
    "number": "contact", "call": "contact", "helpline": "contact",
    "email": "contact", "mail": "contact", "support": "contact",

    # LOCATION
    "location": "address", "address": "address",
    "where": "address", "located": "address",
    "place": "address", "map": "address", "directions": "address",
    "city": "address", "bangalore": "address", "campus": "address",

    # COURSES
    "courses": "course", "course": "course",
    "programs": "course", "program": "course",
    "degrees": "course", "degree": "course",
    "branch": "course", "branches": "course", "stream": "course",
    "cse": "course", "btech": "course", "mtech": "course",

    # EXAMS
    "examinations": "exam", "exams": "exam", "exam": "exam",
    "tests": "exam", "test": "exam", "jee": "exam", "cet": "exam", 
    "gate": "exam", "cutoff": "exam", "cutoffs": "exam", "rank": "exam",

    # RESULTS
    "results": "result", "result": "result",
    "score": "result", "scores": "result",
    "grade": "result", "grades": "result",
    "gpa": "result", "cgpa": "result", "marks": "result", "portal": "result",

    # PLACEMENTS
    "placements": "placement", "placement": "placement",
    "jobs": "placement", "job": "placement",
    "careers": "placement", "career": "placement",
    "salary": "placement", "package": "placement", 
    "recruit": "placement", "hiring": "placement", 
    "amazon": "placement", "google": "placement",

    # FACILITIES
    "hostels": "hostel", "hostel": "hostel",
    "room": "hostel", "rooms": "hostel", "stay": "hostel", "accommodation": "hostel",
    "mess": "hostel", 
    "canteen": "canteen", "cafeteria": "canteen", "food": "canteen", "lunch": "canteen",
    "transport": "transport", "bus": "transport", "buses": "transport",
    "commute": "transport", "travel": "transport", "route": "transport",
    
    # ADMISSION
    "admission": "admission", "admissions": "admission",
    "apply": "admission", "application": "admission",
    "register": "admission", "join": "admission", "seat": "admission"
}

# --- 1.5 SPELLING CORRECTION DICTIONARY ---
SPELLING_CORRECTIONS = {
    # Common misspellings of institute terms
    "feees": "fees", "fes": "fees", "fess": "fees", "feesd": "fees",
    "addmission": "admission", "admision": "admission", "admissoin": "admission",
    "plcement": "placement", "placment": "placement", "placements": "placements",
    "hostl": "hostel", "hostle": "hostel", "hostell": "hostel",
    "timmings": "timings", "timing": "timings", "timimg": "timings",
    "cources": "courses", "cours": "course", "corse": "course", "corses": "courses",
    "contct": "contact", "cantact": "contact", "contat": "contact",
    "addres": "address", "adress": "address", "adres": "address",
    "exm": "exam", "exams": "exams", "examz": "exams",
    "reslt": "result", "rsult": "result", "resultt": "result",
    "schlrship": "scholarship", "scholrship": "scholarship",
    "infra": "infrastructure", "infrastructer": "infrastructure",
    "libary": "library", "libraray": "library", "librery": "library",
    "transportt": "transport", "trasport": "transport",
    "cantene": "canteen", "cantin": "canteen", "cantean": "canteen",
    "sallary": "salary", "salery": "salary", "salry": "salary",
    "pakage": "package", "packge": "package", "packag": "package",
    "registr": "register", "regsiter": "register",
    "facilites": "facilities", "facilitys": "facilities",
    "accomodation": "accommodation", "acomodation": "accommodation",
    "tuision": "tuition", "tution": "tuition", "tuiton": "tuition"
}

# --- 2. INTENT CLASSIFICATION SYSTEM ---
# Define 7 intents with training data (keywords and example phrases)
INTENT_DEFINITIONS = {
    "admissions": {
        "keywords": ["admission", "apply", "application", "register", "join", "seat", "eligibility", 
                     "criteria", "qualify", "requirement", "enroll", "intake", "cutoff", "rank"],
        "examples": [
            "how to apply for admission",
            "what is the admission process",
            "when does registration start",
            "am i eligible for btech",
            "admission criteria for mtech"
        ],
        "weight": 1.2  # Higher weight for important intents
    },
    "exams": {
        "keywords": ["exam", "test", "jee", "gate", "kcet", "comedk", "entrance", "score", 
                     "cutoff", "rank", "result", "marks", "grade", "gpa", "cgpa"],
        "examples": [
            "which exams are accepted",
            "jee cutoff for cse",
            "gate score required",
            "how to check results"
        ],
        "weight": 1.0
    },
    "fees": {
        "keywords": ["fee", "tuition", "cost", "price", "payment", "pay", "amount", 
                     "expense", "lakh", "rupee", "rs", "scholarship", "loan", "waiver"],
        "examples": [
            "what are the fees",
            "how much is tuition",
            "btech fee structure",
            "any scholarships available"
        ],
        "weight": 1.3  # High priority
    },
    "placements": {
        "keywords": ["placement", "job", "career", "salary", "package", "recruit", 
                     "hiring", "company", "google", "amazon", "microsoft", "intern"],
        "examples": [
            "what about placements",
            "average package for cse",
            "which companies recruit",
            "highest salary offered"
        ],
        "weight": 1.1
    },
    "facilities": {
        "keywords": ["hostel", "transport", "bus", "canteen", "library", "wifi", 
                     "lab", "gym", "sports", "infrastructure", "facility", "accommodation"],
        "examples": [
            "tell me about hostel",
            "is there bus facility",
            "what infrastructure do you have",
            "library and wifi available"
        ],
        "weight": 0.9
    },
    "academics": {
        "keywords": ["course", "program", "degree", "branch", "cse", "btech", "mtech", 
                     "curriculum", "syllabus", "faculty", "professor", "teacher", "class"],
        "examples": [
            "what courses are offered",
            "cse curriculum details",
            "faculty qualifications",
            "btech branches available"
        ],
        "weight": 1.0
    },
    "general": {
        "keywords": ["time", "timing", "schedule", "contact", "phone", "email", 
                     "address", "location", "where", "campus", "event", "fest"],
        "examples": [
            "what are the timings",
            "contact details",
            "where is the campus",
            "college address"
        ],
        "weight": 0.8
    }
}

class IntentClassifier:
    """Simple Intent Classifier using TF-IDF and keyword matching"""
    
    def __init__(self, intent_definitions):
        self.intents = intent_definitions
        self.intent_vectors = {}
        self._build_intent_vectors()
    
    def _build_intent_vectors(self):
        """Build TF-IDF-like vectors for each intent based on keywords and examples"""
        for intent_name, intent_data in self.intents.items():
            # Combine keywords and examples
            all_text = " ".join(intent_data["keywords"]) + " " + " ".join(intent_data["examples"])
            
            # Preprocess the combined text
            tokens = preprocess_text(all_text)
            
            # Create a frequency vector
            token_freq = Counter(tokens)
            
            # Store the vector with weight
            self.intent_vectors[intent_name] = {
                'vector': token_freq,
                'weight': intent_data.get('weight', 1.0)
            }
    
    def classify(self, query):
        """
        Classify a query into one of the defined intents
        Returns: (intent_name, confidence_score)
        """
        # Preprocess the query
        query_tokens = preprocess_text(query)
        
        if not query_tokens:
            return ("general", 0.0)
        
        query_vector = Counter(query_tokens)
        
        # Calculate similarity with each intent
        intent_scores = {}
        for intent_name, intent_data in self.intent_vectors.items():
            # Calculate overlap score (Jaccard-like similarity + frequency)
            intent_vec = intent_data['vector']
            weight = intent_data['weight']
            
            # Common tokens
            common_tokens = set(query_vector.keys()) & set(intent_vec.keys())
            
            if not common_tokens:
                intent_scores[intent_name] = 0.0
                continue
            
            # Calculate weighted score
            score = sum(min(query_vector[token], intent_vec[token]) for token in common_tokens)
            score = score / len(query_tokens)  # Normalize by query length
            score = score * weight  # Apply intent weight
            
            intent_scores[intent_name] = score
        
        # Get the best intent
        if not intent_scores or max(intent_scores.values()) == 0:
            return ("general", 0.0)
        
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[best_intent]
        
        return (best_intent, confidence)
    
    def get_all_scores(self, query):
        """Get scores for all intents (useful for debugging)"""
        query_tokens = preprocess_text(query)
        query_vector = Counter(query_tokens)
        
        intent_scores = {}
        for intent_name, intent_data in self.intent_vectors.items():
            intent_vec = intent_data['vector']
            weight = intent_data['weight']
            
            common_tokens = set(query_vector.keys()) & set(intent_vec.keys())
            
            if not common_tokens:
                intent_scores[intent_name] = 0.0
                continue
            
            score = sum(min(query_vector[token], intent_vec[token]) for token in common_tokens)
            if query_tokens:
                score = score / len(query_tokens)
            score = score * weight
            
            intent_scores[intent_name] = round(score, 4)
        
        return intent_scores

# --- 3. STOPWORDS (NOISE REMOVAL) ---
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "in", "on", "at", "to", "for", 
    "of", "with", "by", "about", "how", "what", "when", "where", "who", "which", 
    "why", "can", "could", "would", "should", "do", "does", "did", "please", 
    "help", "me", "i", "you", "my", "your", "we", "us", "our", "it", "this", "that"
}

# --- 3. PREPROCESSING ENGINE ---
def preprocess_text(text):
    """
    Enhanced preprocessing that combines:
    1. Spelling correction
    2. Synonym mapping
    3. TF-IDF preprocessing
    """
    # Lowercase & Remove punctuation
    text = text.lower()
    text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    tokens = text.split()
    
    clean_tokens = []
    for token in tokens:
        if token not in STOP_WORDS and token != "":
            # Step 1: Apply spelling correction first
            corrected_token = SPELLING_CORRECTIONS.get(token, token)
            # Step 2: Apply synonym normalization
            normalized_token = NORMALIZATION_MAP.get(corrected_token, corrected_token)
            clean_tokens.append(normalized_token)
            
    return clean_tokens

# --- Initialize Intent Classifier (after preprocess_text is defined) ---
intent_classifier = IntentClassifier(INTENT_DEFINITIONS)

# --- 4. TF-IDF IMPLEMENTATION ---
class TFIDFRetriever:
    def __init__(self):
        self.faqs = []
        self.documents = []  # Preprocessed FAQ questions
        self.idf = {}
        self.tf_idf_vectors = []
        
    def add_faq(self, question, answer, tag):
        """Add an FAQ to the knowledge base"""
        self.faqs.append({
            'question': question,
            'answer': answer,
            'tag': tag
        })
        # Preprocess and store the question
        preprocessed = preprocess_text(question)
        self.documents.append(preprocessed)
        
    def build_index(self):
        """Build TF-IDF index after all FAQs are added"""
        # Calculate document frequency for each term
        df = Counter()
        for doc in self.documents:
            unique_terms = set(doc)
            for term in unique_terms:
                df[term] += 1
        
        # Calculate IDF
        num_docs = len(self.documents)
        for term, freq in df.items():
            self.idf[term] = math.log(num_docs / freq)
        
        # Calculate TF-IDF vectors for each document
        for doc in self.documents:
            tf_idf_vector = self._calculate_tf_idf(doc)
            self.tf_idf_vectors.append(tf_idf_vector)
    
    def _calculate_tf_idf(self, tokens):
        """Calculate TF-IDF vector for a document"""
        tf_idf = {}
        tf = Counter(tokens)
        doc_length = len(tokens)
        
        for term, count in tf.items():
            # TF: term frequency normalized by document length
            term_freq = count / doc_length if doc_length > 0 else 0
            # TF-IDF
            tf_idf[term] = term_freq * self.idf.get(term, 0)
        
        return tf_idf
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two TF-IDF vectors"""
        # Get all unique terms
        all_terms = set(vec1.keys()) | set(vec2.keys())
        
        # Calculate dot product
        dot_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in all_terms)
        
        # Calculate magnitudes
        mag1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
        mag2 = math.sqrt(sum(val ** 2 for val in vec2.values()))
        
        # Avoid division by zero
        if mag1 == 0 or mag2 == 0:
            return 0
        
        return dot_product / (mag1 * mag2)
    
    def retrieve(self, query, threshold=0.1):
        """
        Retrieve the most relevant FAQ for a query
        Returns: (answer, similarity_score, tag) or None
        """
        # Preprocess query
        query_tokens = preprocess_text(query)
        
        if not query_tokens:
            return None
        
        # Calculate TF-IDF for query
        query_vector = self._calculate_tf_idf(query_tokens)
        
        # Calculate similarities with all documents
        similarities = []
        for idx, doc_vector in enumerate(self.tf_idf_vectors):
            similarity = self._cosine_similarity(query_vector, doc_vector)
            similarities.append((idx, similarity))
        
        # Get the best match
        best_match = max(similarities, key=lambda x: x[1])
        idx, score = best_match
        
        # Return answer if similarity is above threshold
        if score >= threshold:
            return (self.faqs[idx]['answer'], score, self.faqs[idx]['tag'])
        
        return None

# --- 5. KNOWLEDGE BASE WITH ENHANCED FAQ ENTRIES ---
# Initialize TF-IDF retriever
tfidf_retriever = TFIDFRetriever()

# Add FAQs with multiple question variations for better retrieval
FAQ_DATA = [
    {
        "question": "What are the fees tuition cost price payment for btech mtech",
        "answer": "💰 <b>[FEES STRUCTURE]</b><br>• B.Tech: ₹1.5 Lakhs/year<br>• M.Tech: ₹90,000/year<br><i>*Scholarships available for merit students.</i>",
        "tag": "fees"
    },
    {
        "question": "What are the timings schedule hours working days opening time",
        "answer": "🕒 <b>[CAMPUS HOURS]</b><br>• Classes: 9:00 AM - 5:00 PM (Mon-Fri)<br>• Admin Office: 9:30 AM - 4:30 PM (Mon-Sat)",
        "tag": "timings"
    },
    {
        "question": "What is the contact phone number email support helpline",
        "answer": "📞 <b>[CONTACT DETAILS]</b><br>• Admission Cell: +91 98765 43210<br>• Email: admissions@nics.edu.in",
        "tag": "contact"
    },
    {
        "question": "What is the address location where campus map directions city bangalore",
        "answer": "📍 <b>[LOCATION]</b><br>Tech Park Campus, Electronic City Phase 1,<br>Bangalore, Karnataka - 560100.",
        "tag": "address"
    },
    {
        "question": "What courses programs degrees branches offered cse btech mtech stream",
        "answer": "🎓 <b>[COURSES OFFERED]</b><br>1. Computer Science (CSE)<br>2. AI & Data Science<br>3. Cyber Security<br>Also offering M.Tech & Ph.D programs.",
        "tag": "courses"
    },
    {
        "question": "What entrance exams tests jee cet gate cutoff rank required",
        "answer": "📝 <b>[ENTRANCE EXAMS]</b><br>• B.Tech: JEE Mains / KCET / COMEDK rank.<br>• M.Tech: GATE score.<br><b>Last Year's CSE Cutoff:</b> JEE Rank 15,000",
        "tag": "exams"
    },
    {
        "question": "How to check results score grade gpa cgpa marks portal",
        "answer": "📊 <b>[RESULTS]</b><br>Check semester results on the <b>Student ERP Portal</b>.<br>Min 7.5 CGPA required for Placement Eligibility.",
        "tag": "results"
    },
    {
        "question": "What is the infrastructure library wifi lab facilities",
        "answer": "💻 <b>[INFRASTRUCTURE]</b><br>• 24/7 Digital Library (IEEE access)<br>• NVIDIA AI Research Lab<br>• 1 Gbps Wi-Fi Campus-wide.",
        "tag": "infrastructure"
    },
    {
        "question": "Tell me about hostel accommodation room stay mess",
        "answer": "🏠 <b>[HOSTEL]</b><br>• AC/Non-AC Twin Sharing.<br>• Fees: ₹85,000/year (Includes Veg/Non-Veg Mess).",
        "tag": "hostel"
    },
    {
        "question": "What is the admission process apply application register join seat",
        "answer": "📝 <b>[ADMISSION PROCESS]</b><br>Counseling starts in June.<br>Carry 10th/12th marksheets, JEE scorecard, and Aadhar card.",
        "tag": "admission"
    },
    {
        "question": "What transport bus commute travel route facilities available",
        "answer": "🚌 <b>[TRANSPORT]</b><br>AC Buses covering all major Bangalore routes.<br>Pass fee: ₹25,000/year.",
        "tag": "transport"
    },
    {
        "question": "Tell me about canteen cafeteria food lunch dining",
        "answer": "☕ <b>[CAFETERIA]</b><br>• Main Canteen (Veg Only)<br>• Coffee Day Kiosk<br>Open 8 AM - 8 PM.",
        "tag": "canteen"
    },
    {
        "question": "What are the placements jobs salary package recruit amazon google microsoft careers",
        "answer": "💼 <b>[PLACEMENTS 2024]</b><br>• Highest: ₹45 LPA (Amazon)<br>• Average: ₹8.5 LPA<br>• Top Recruiters: Google, Microsoft, TCS, Infosys.",
        "tag": "placement"
    }
]

# Build the TF-IDF index
for faq in FAQ_DATA:
    tfidf_retriever.add_faq(faq['question'], faq['answer'], faq['tag'])

tfidf_retriever.build_index()

# --- 6. GREETING DETECTION (SIMPLE PATTERN MATCHING) ---
GREETINGS = ["hello", "hi", "hey", "namaste", "greetings", "good morning", "good afternoon"]
FAREWELL = ["bye", "goodbye", "exit", "quit", "see you", "later"]

def is_greeting(text):
    text_lower = text.lower()
    return any(greeting in text_lower for greeting in GREETINGS)

def is_farewell(text):
    text_lower = text.lower()
    return any(word in text_lower for word in FAREWELL)

# --- 8. RULE-BASED PATTERN MATCHING (EDGE CASES) ---
def rule_based_matcher(text):
    """
    Advanced rule-based pattern matching for specific queries
    Returns: (answer, confidence) or None
    """
    text_lower = text.lower()
    
    # Pattern 1: Direct question about specific amount
    if re.search(r'\d+\s*(lakh|rupee|rs|₹)', text_lower):
        return ("I see you're asking about specific amounts. Our fees are: B.Tech ₹1.5L/year, M.Tech ₹90K/year.", 0.9)
    
    # Pattern 2: Comparison questions
    if any(word in text_lower for word in ["compare", "difference", "vs", "versus", "better"]):
        return ("For detailed comparisons between programs, please contact our admission cell at +91 98765 43210.", 0.85)
    
    # Pattern 3: Eligibility questions
    if any(word in text_lower for word in ["eligible", "qualify", "criteria", "requirement"]):
        return ("📋 <b>[ELIGIBILITY]</b><br>B.Tech requires JEE/KCET rank. M.Tech requires GATE score. Contact admissions for specific cutoffs.", 0.88)
    
    # Pattern 4: Scholarship/financial aid
    if any(word in text_lower for word in ["scholarship", "financial aid", "loan", "waiver"]):
        return ("💰 <b>[SCHOLARSHIPS]</b><br>Merit scholarships available! Students with >90% in 12th get 25% fee waiver. Education loans supported.", 0.9)
    
    # Pattern 5: Faculty/professor questions
    if any(word in text_lower for word in ["faculty", "professor", "teacher", "staff"]):
        return ("👨‍🏫 <b>[FACULTY]</b><br>All faculty are PhD holders from IITs/NITs. Student-teacher ratio is 1:15. Industry experts conduct guest lectures.", 0.88)
    
    # Pattern 6: Events/festivals
    if any(word in text_lower for word in ["event", "fest", "festival", "cultural", "techfest"]):
        return ("🎉 <b>[EVENTS]</b><br>Annual TechFest in February and Cultural Fest 'Spandan' in March. Multiple coding hackathons throughout the year.", 0.87)
    
    # Pattern 7: Sports/extracurricular
    if any(word in text_lower for word in ["sports", "gym", "cricket", "football", "basketball", "extracurricular"]):
        return ("⚽ <b>[SPORTS]</b><br>We have cricket/football grounds, basketball court, and a modern gym. Multiple sports clubs and teams available.", 0.86)
    
    return None

# --- 9. CONVERSATION CONTEXT MANAGEMENT ---
def get_or_create_session():
    """Get or create a session ID for conversation tracking"""
    if 'session_id' not in session:
        import uuid
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def update_context(session_id, query, response, tag=None):
    """Update conversation context for a session"""
    if session_id not in conversation_contexts:
        conversation_contexts[session_id] = {
            'history': [],
            'last_tag': None,
            'query_count': 0
        }
    
    context = conversation_contexts[session_id]
    context['history'].append({
        'query': query,
        'response': response,
        'tag': tag,
        'timestamp': datetime.now().isoformat()
    })
    context['last_tag'] = tag
    context['query_count'] += 1
    
    # Keep only last 10 interactions to save memory
    if len(context['history']) > 10:
        context['history'] = context['history'][-10:]

def get_context_response(session_id, query):
    """Generate contextual response based on conversation history"""
    if session_id not in conversation_contexts:
        return None
    
    context = conversation_contexts[session_id]
    
    # If user asks follow-up questions like "more details", "tell me more", etc.
    follow_up_phrases = ["more", "detail", "elaborate", "explain", "tell me more", "anything else"]
    if any(phrase in query.lower() for phrase in follow_up_phrases):
        if context['last_tag']:
            return f"For more details about <b>{context['last_tag']}</b>, please contact our admission cell at +91 98765 43210 or email admissions@nics.edu.in"
    
    return None

# --- 7. FLASK ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    data = request.get_json()
    raw_input = data.get('message', '')
    
    # Get or create session for context tracking
    session_id = get_or_create_session()
    
    # Priority 1: Check for greetings
    if is_greeting(raw_input):
        response = "<b>Namaste!</b> Welcome to NICS. I can help with B.Tech admissions, Fees, and Placements."
        update_context(session_id, raw_input, response, 'greeting')
        return jsonify({
            'response': response,
            'method': 'greeting',
            'confidence': 1.0,
            'intent': 'greeting'
        })
    
    # Priority 2: Check for farewell
    if is_farewell(raw_input):
        response = "Goodbye! All the best for your engineering journey. <b>Jai Hind! 🇮🇳</b>"
        update_context(session_id, raw_input, response, 'farewell')
        return jsonify({
            'response': response,
            'method': 'farewell',
            'confidence': 1.0,
            'intent': 'farewell'
        })
    
    # CLASSIFY INTENT FIRST (NEW!)
    detected_intent, intent_confidence = intent_classifier.classify(raw_input)
    
    # Priority 3: Check conversation context (follow-up questions)
    context_response = get_context_response(session_id, raw_input)
    if context_response:
        update_context(session_id, raw_input, context_response, 'context')
        return jsonify({
            'response': context_response,
            'method': 'context',
            'confidence': 0.95,
            'intent': detected_intent,
            'intent_confidence': round(intent_confidence, 3)
        })
    
    # Priority 4: Rule-based pattern matching for edge cases
    rule_result = rule_based_matcher(raw_input)
    if rule_result:
        answer, confidence = rule_result
        update_context(session_id, raw_input, answer, 'rule-based')
        return jsonify({
            'response': answer,
            'method': 'rule-based',
            'confidence': confidence,
            'intent': detected_intent,
            'intent_confidence': round(intent_confidence, 3)
        })
    
    # Priority 5: Use TF-IDF retrieval for FAQ matching (with preprocessing including spelling correction)
    result = tfidf_retriever.retrieve(raw_input, threshold=0.1)
    
    if result:
        answer, confidence, tag = result
        update_context(session_id, raw_input, answer, tag)
        return jsonify({
            'response': answer,
            'method': 'tfidf',
            'confidence': round(confidence, 3),
            'tag': tag,
            'intent': detected_intent,
            'intent_confidence': round(intent_confidence, 3)
        })
    else:
        # Fallback message with intent-based suggestion
        intent_suggestions = {
            'admissions': 'Try asking: "How do I apply?" or "What is the admission process?"',
            'exams': 'Try asking: "Which exams are accepted?" or "What is the JEE cutoff?"',
            'fees': 'Try asking: "What are the fees?" or "Any scholarships?"',
            'placements': 'Try asking: "Tell me about placements" or "Average package?"',
            'facilities': 'Try asking: "What facilities are there?" or "Tell me about hostel"',
            'academics': 'Try asking: "What courses are offered?" or "Tell me about faculty"',
            'general': 'Try asking about <b>Fees</b>, <b>Placements</b>, or <b>Admissions</b>.'
        }
        
        suggestion = intent_suggestions.get(detected_intent, intent_suggestions['general'])
        fallback = f"I didn't fully understand that. 🤔<br>It seems you're asking about <b>{detected_intent}</b>.<br>{suggestion}"
        
        update_context(session_id, raw_input, fallback, 'fallback')
        return jsonify({
            'response': fallback,
            'method': 'fallback',
            'confidence': 0.0,
            'intent': detected_intent,
            'intent_confidence': round(intent_confidence, 3)
        })

@app.route('/debug', methods=['POST'])
def debug_tfidf():
    """Debug endpoint to see TF-IDF scores for all FAQs"""
    data = request.get_json()
    query = data.get('message', '')
    
    query_tokens = preprocess_text(query)
    query_vector = tfidf_retriever._calculate_tf_idf(query_tokens)
    
    results = []
    for idx, doc_vector in enumerate(tfidf_retriever.tf_idf_vectors):
        similarity = tfidf_retriever._cosine_similarity(query_vector, doc_vector)
        results.append({
            'faq': tfidf_retriever.faqs[idx]['tag'],
            'similarity': round(similarity, 4)
        })
    
    # Sort by similarity
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    return jsonify({
        'query': query,
        'preprocessed': query_tokens,
        'results': results
    })

@app.route('/context', methods=['GET'])
def get_context():
    """Endpoint to view conversation context for current session"""
    session_id = get_or_create_session()
    
    if session_id in conversation_contexts:
        context = conversation_contexts[session_id]
        return jsonify({
            'session_id': session_id,
            'query_count': context['query_count'],
            'last_tag': context['last_tag'],
            'history': context['history']
        })
    else:
        return jsonify({
            'session_id': session_id,
            'query_count': 0,
            'message': 'No conversation history yet'
        })

@app.route('/classify_intent', methods=['POST'])
def classify_intent_debug():
    """Debug endpoint to see intent classification scores"""
    data = request.get_json()
    query = data.get('message', '')
    
    # Get the detected intent
    detected_intent, confidence = intent_classifier.classify(query)
    
    # Get all intent scores
    all_scores = intent_classifier.get_all_scores(query)
    
    # Preprocess query to show what tokens are used
    query_tokens = preprocess_text(query)
    
    return jsonify({
        'query': query,
        'preprocessed_tokens': query_tokens,
        'detected_intent': detected_intent,
        'confidence': round(confidence, 4),
        'all_intent_scores': all_scores,
        'intent_definitions': {
            intent: {
                'keywords': INTENT_DEFINITIONS[intent]['keywords'][:5],  # Show first 5 keywords
                'weight': INTENT_DEFINITIONS[intent]['weight']
            }
            for intent in INTENT_DEFINITIONS.keys()
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
