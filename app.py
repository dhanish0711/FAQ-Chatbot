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
    "register": "admission", "join": "admission", "seat": "admission",

    # SCHOLARSHIP
    "scholarship": "scholarship", "scholarships": "scholarship",
    "waiver": "scholarship", "concession": "scholarship",

    # LIBRARY
    "library": "library", "books": "library", "journals": "library",

    # CLUBS & ACTIVITIES
    "club": "club", "clubs": "club",
    "society": "club", "societies": "club",
    "nss": "club", "ncc": "club",

    # INTERNSHIP
    "internship": "internship", "internships": "internship",
    "intern": "internship", "stipend": "internship",

    # ATTENDANCE
    "attendance": "attendance", "absent": "attendance",
    "proxy": "attendance", "detention": "attendance",

    # HEALTH & MEDICAL
    "medical": "medical", "clinic": "medical",
    "doctor": "medical", "ambulance": "medical",

    # PARKING
    "parking": "parking", "vehicle": "parking", "bike": "parking",

    # BACKLOG
    "backlog": "backlog", "arrear": "backlog",
    "supplementary": "backlog", "atkt": "backlog", "revaluation": "backlog",

    # TIMETABLE
    "timetable": "timetable", "routine": "timetable", "period": "timetable"
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
    "tuision": "tuition", "tution": "tuition", "tuiton": "tuition",
    "scholership": "scholarship", "scholarshp": "scholarship", "scholrshp": "scholarship",
    "attandance": "attendance", "attendence": "attendance", "attendace": "attendance",
    "internshp": "internship", "intrship": "internship", "intership": "internship",
    "timetabel": "timetable", "timetble": "timetable",
    "backlg": "backlog", "bcklog": "backlog", "baklog": "backlog",
    "medcal": "medical", "medial": "medical",
    "parkng": "parking", "parkin": "parking",
    "vehical": "vehicle", "vehicl": "vehicle"
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

# --- 3.5 ENTITY EXTRACTION FOR DATES, COURSES & SEMESTERS ---
class EntityExtractor:
    """Extract structured entities from queries like dates, courses, and semesters"""
    
    def __init__(self):
        # Define course code patterns (use regex word-boundary matching)
        self.course_patterns = {
            'CS': [r'\bcs\b', r'\bcse\b', r'\bcomputer science\b', r'\bcompsci\b'],
            'IT': [r'\binformation technology\b', r'\binfo tech\b'],
            'ECE': [r'\bece\b', r'\belectronics\b', r'\belectronics communication\b'],
            'MECH': [r'\bmech\b', r'\bmechanical\b'],
            'CIVIL': [r'\bcivil\b'],
            'EEE': [r'\beee\b', r'\belectrical\b', r'\belectrical electronics\b'],
            'BTECH': [r'\bbtech\b', r'\bb\.tech\b', r'\bb tech\b'],
            'MTECH': [r'\bmtech\b', r'\bm\.tech\b', r'\bm tech\b']
        }
        
        # Month patterns
        self.months = {
            'january': 1, 'jan': 1,
            'february': 2, 'feb': 2,
            'march': 3, 'mar': 3,
            'april': 4, 'apr': 4,
            'may': 5,
            'june': 6, 'jun': 6,
            'july': 7, 'jul': 7,
            'august': 8, 'aug': 8,
            'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10,
            'november': 11, 'nov': 11,
            'december': 12, 'dec': 12
        }
    
    def extract_entities(self, text):
        """Extract all entities from text"""
        text_lower = text.lower()
        entities = {
            'courses': [],
            'semesters': [],
            'dates': [],
            'months': [],
            'years': []
        }
        
        # Extract courses using regex word boundaries
        for course_code, patterns in self.course_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if course_code not in entities['courses']:
                        entities['courses'].append(course_code)
                    break
        
        # Extract semesters using regex
        # Pattern: sem 5, semester 3, 5th sem, etc.
        sem_patterns = [
            r'sem(?:ester)?\s*(\d+)',
            r'(\d+)(?:st|nd|rd|th)?\s*sem(?:ester)?',
            r's(\d+)'
        ]
        
        for pattern in sem_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                sem_num = int(match)
                if 1 <= sem_num <= 8 and sem_num not in entities['semesters']:
                    entities['semesters'].append(sem_num)
        
        # Extract months
        for month_name, month_num in self.months.items():
            if month_name in text_lower:
                entities['months'].append({
                    'name': month_name.capitalize(),
                    'number': month_num
                })
        
        # Extract years (4-digit years between 2020-2030)
        year_pattern = r'\b(202[0-9]|203[0-0])\b'
        years = re.findall(year_pattern, text_lower)
        entities['years'] = [int(y) for y in years]
        
        # Extract dates (dd/mm/yyyy, dd-mm-yyyy, dd.mm.yyyy)
        date_patterns = [
            r'\b(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})\b',
            r'\b(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s+(\d{2,4})\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                entities['dates'].extend(matches)
        
        # Remove duplicates and sort
        entities['semesters'] = sorted(list(set(entities['semesters'])))
        entities['courses'] = list(set(entities['courses']))
        
        return entities
    
    def format_entity_context(self, entities):
        """Format extracted entities into a readable string"""
        context_parts = []
        
        if entities['courses']:
            context_parts.append(f"Courses: {', '.join(entities['courses'])}")
        
        if entities['semesters']:
            sem_str = ', '.join([f"Semester {s}" for s in entities['semesters']])
            context_parts.append(f"Semesters: {sem_str}")
        
        if entities['months']:
            month_names = [m['name'] for m in entities['months']]
            context_parts.append(f"Months: {', '.join(month_names)}")
        
        if entities['years']:
            context_parts.append(f"Years: {', '.join(map(str, entities['years']))}")
        
        return " | ".join(context_parts) if context_parts else ""

# Initialize Entity Extractor
entity_extractor = EntityExtractor()

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
        "answer": "💰 <b>[FEES STRUCTURE 2026-27]</b><br>• <b>B.Tech:</b> ₹1.5 Lakhs/year (₹75K per semester)<br>• <b>M.Tech:</b> ₹90,000/year (₹45K per semester)<br>• <b>Ph.D:</b> ₹60,000/year + stipend for GATE scholars<br>• <b>Hostel + Mess:</b> ₹85,000/year<br>• <b>Payment Modes:</b> UPI, NEFT, Credit/Debit Card, DD<br>• <b>EMI:</b> Semester-wise installment available<br>• <b>Deadline:</b> Within 15 days of admission<br><i>*Merit scholarships: 25% waiver for 12th marks > 90%</i>",
        "tag": "fees"
    },
    {
        "question": "What are the timings schedule hours working days opening time",
        "answer": "🕒 <b>[CAMPUS HOURS]</b><br>• Classes: 9:00 AM - 5:00 PM (Mon-Fri)<br>• Admin Office: 9:30 AM - 4:30 PM (Mon-Sat)",
        "tag": "timings"
    },
    {
        "question": "What is the contact phone number email support helpline",
        "answer": "📞 <b>[CONTACT DETAILS]</b><br>• <b>Admission Cell:</b> +91 98765 43210<br>• <b>Placement Cell:</b> +91 98765 43211<br>• <b>Hostel Warden:</b> +91 98765 43212<br>• <b>Exam Cell:</b> +91 98765 43213<br>• <b>General:</b> +91 80 2345 6789<br>• <b>Email:</b> admissions@nics.edu.in<br>• <b>Website:</b> www.nics.edu.in<br>• <b>WhatsApp:</b> +91 98765 43210",
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
        "answer": "📝 <b>[ADMISSION PROCESS 2026]</b><br>• <b>Step 1:</b> Apply online at www.nics.edu.in/apply<br>• <b>Step 2:</b> Attend counseling (July 10-20)<br>• <b>Step 3:</b> Document verification & fee payment<br>• <b>Step 4:</b> Seat allotment confirmation<br>• <b>Documents:</b> 10th/12th marks, JEE/KCET scorecard, Aadhar, Photos (6), TC<br>• <b>Application Fee:</b> ₹500 (online) / ₹600 (offline)<br>• <b>Helpline:</b> +91 98765 43210",
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
        "answer": "💼 <b>[PLACEMENTS 2025-26]</b><br>• <b>Highest:</b> ₹45 LPA (Amazon)<br>• <b>Average:</b> ₹8.5 LPA | <b>Median:</b> ₹6.5 LPA<br>• <b>Students Placed:</b> 92% overall<br>• <b>150+ Companies</b> visit campus annually<br>• <b>Top Recruiters:</b> Google, Microsoft, Amazon, Adobe, TCS, Infosys, Wipro, Flipkart<br>• <b>Dream Offers (20+ LPA):</b> 35+ students<br>• <b>Internship → PPO:</b> 40% conversion rate",
        "tag": "placement"
    },
    
    # --- ENTITY-AWARE FAQs: EXAM SCHEDULES ---
    {
        "question": "When is semester 5 sem5 s5 fifth exam examination date schedule",
        "answer": "📅 <b>[SEM 5 EXAMS]</b><br>• Theory Exams: 15-25 May 2026<br>• Practical Exams: 1-5 June 2026<br>• Results: By 30 June 2026",
        "tag": "exams"
    },
    {
        "question": "When is semester 3 sem3 s3 third exam examination date schedule",
        "answer": "📅 <b>[SEM 3 EXAMS]</b><br>• Theory Exams: 10-20 November 2026<br>• Practical Exams: 25-29 November 2026<br>• Results: By 20 December 2026",
        "tag": "exams"
    },
    {
        "question": "When is semester 7 sem7 s7 seventh exam examination date schedule",
        "answer": "📅 <b>[SEM 7 EXAMS]</b><br>• Theory Exams: 20-30 May 2026<br>• Practical Exams: 2-8 June 2026<br>• Results: By 5 July 2026",
        "tag": "exams"
    },
    {
        "question": "When exam schedule semester 1 sem1 first s1",
        "answer": "📅 <b>[SEM 1 EXAMS]</b><br>• Mid-term: 15-18 October 2026<br>• End-term: 5-15 December 2026<br>• Results: By 31 December 2026",
        "tag": "exams"
    },
    {
        "question": "When exam schedule semester 2 sem2 second s2",
        "answer": "📅 <b>[SEM 2 EXAMS]</b><br>• Mid-term: 10-13 March 2027<br>• End-term: 1-10 May 2027<br>• Results: By 31 May 2027",
        "tag": "exams"
    },
    
    # --- COURSE-SPECIFIC FAQs: CS/CSE ---
    {
        "question": "computer science cse cs branch course program curriculum subjects",
        "answer": "💻 <b>[CSE/CS PROGRAM]</b><br>• Core: Data Structures, Algorithms, DBMS, OS, CN<br>• Specializations: AI/ML, Cloud Computing, Cybersecurity<br>• Labs: Advanced Programming, ML Lab<br>• Industry Tie-ups: Google, Microsoft, Amazon",
        "tag": "academics"
    },
    {
        "question": "cs cse computer science placement package salary average highest",
        "answer": "💼 <b>[CS PLACEMENTS]</b><br>• Avg Package: ₹12 LPA<br>• Highest: ₹45 LPA (Google)<br>• Top Recruiters: Microsoft, Amazon, Adobe, TCS<br>• Placement Rate: 98%",
        "tag": "placement"
    },
    
    # --- COURSE-SPECIFIC FAQs: IT ---
    {
        "question": "information technology it branch course program curriculum subjects",
        "answer": "🖥️ <b>[IT PROGRAM]</b><br>• Core: Software Engineering, Web Tech, Mobile App Dev, Cloud<br>• Specializations: IoT, Blockchain, DevOps<br>• Labs: Web Lab, Mobile Dev Lab<br>• Certifications: AWS, Azure offered",
        "tag": "academics"
    },
    {
        "question": "it information technology placement package salary jobs average highest",
        "answer": "💼 <b>[IT PLACEMENTS]</b><br>• Avg Package: ₹10 LPA<br>• Highest: ₹38 LPA (Flipkart)<br>• Top Recruiters: Infosys, Wipro, Cognizant, Accenture<br>• Placement Rate: 95%",
        "tag": "placement"
    },
    
    # --- COURSE-SPECIFIC FAQs: ECE ---
    {
        "question": "electronics communication ece ec branch course program curriculum subjects",
        "answer": "📡 <b>[ECE PROGRAM]</b><br>• Core: Digital Electronics, Signals, VLSI, Embedded Systems<br>• Specializations: VLSI Design, Communication Systems<br>• Labs: VLSI Lab, Communication Lab<br>• Industry: Qualcomm, Intel, Texas Instruments",
        "tag": "academics"
    },
    {
        "question": "ece electronics communication placement package salary jobs average highest",
        "answer": "💼 <b>[ECE PLACEMENTS]</b><br>• Avg Package: ₹7.5 LPA<br>• Highest: ₹28 LPA (Qualcomm)<br>• Top Recruiters: Intel, Texas Instruments, Broadcom<br>• Placement Rate: 90%",
        "tag": "placement"
    },
    
    # --- COURSE-SPECIFIC FAQs: MECH ---
    {
        "question": "mechanical mech me branch course program curriculum subjects engineering",
        "answer": "⚙️ <b>[MECH PROGRAM]</b><br>• Core: Thermodynamics, Fluid Mechanics, CAD/CAM, Manufacturing<br>• Specializations: Robotics, Automobile, Production<br>• Labs: CAD Lab, Manufacturing Lab, Robotics<br>• Industry: Bosch, L&T, Tata Motors",
        "tag": "academics"
    },
    {
        "question": "mechanical mech placement package salary jobs core average highest",
        "answer": "💼 <b>[MECH PLACEMENTS]</b><br>• Avg Package: ₹6.5 LPA<br>• Highest: ₹22 LPA (Bosch)<br>• Top Recruiters: L&T, Tata Motors, Ashok Leyland<br>• Placement Rate: 88%",
        "tag": "placement"
    },
    
    # --- COURSE-SPECIFIC FAQs: CIVIL ---
    {
        "question": "civil ce branch course program curriculum subjects engineering construction",
        "answer": "🏗️ <b>[CIVIL PROGRAM]</b><br>• Core: Structural Analysis, Geotechnical, Transportation, Hydraulics<br>• Specializations: Construction Management, Environmental Engineering<br>• Labs: Concrete Testing, Surveying Lab<br>• Industry: L&T, Shapoorji Pallonji, DLF",
        "tag": "academics"
    },
    {
        "question": "civil engineering placement package salary jobs construction psu average highest",
        "answer": "💼 <b>[CIVIL PLACEMENTS]</b><br>• Avg Package: ₹5.5 LPA<br>• Highest: ₹18 LPA (L&T)<br>• Top Recruiters: L&T, Shapoorji, NBCC, PSUs<br>• Placement Rate: 85%",
        "tag": "placement"
    },
    
    # --- BTech & MTech General ---
    {
        "question": "btech bachelor technology undergraduate ug course duration eligibility admission",
        "answer": "🎓 <b>[B.TECH PROGRAM]</b><br>• Duration: 4 years (8 semesters)<br>• Eligibility: JEE Main/KCET with Physics, Chemistry, Math<br>• Branches: CSE, IT, ECE, MECH, CIVIL, EEE<br>• Total Seats: 1200",
        "tag": "academics"
    },
    {
        "question": "mtech master technology postgraduate pg course duration eligibility admission gate",
        "answer": "🎓 <b>[M.TECH PROGRAM]</b><br>• Duration: 2 years (4 semesters)<br>• Eligibility: GATE score mandatory<br>• Specializations: CSE (AI/ML), VLSI, Power Systems, Structural<br>• Total Seats: 240",
        "tag": "academics"
    },
    
    # --- SEMESTER-SPECIFIC GENERAL INFO ---
    {
        "question": "semester courses subjects what study sem learn curriculum",
        "answer": "📚 <b>[SEMESTER STRUCTURE]</b><br>• Odd Sems (1,3,5,7): July-December<br>• Even Sems (2,4,6,8): January-June<br>• Each semester: 6-7 subjects + 1 lab<br>• Credit system: 20-24 credits/sem",
        "tag": "academics"
    },
    {
        "question": "exam pattern marks grading system cgpa gpa percentage credit",
        "answer": "📊 <b>[GRADING SYSTEM]</b><br>• Pattern: Mid-term (30%) + End-term (50%) + Internals (20%)<br>• Grading: 10-point CGPA scale<br>• Grade: O(10), A+(9), A(8), B+(7), B(6), C(5)<br>• Pass: Minimum 40% in each subject",
        "tag": "academics"
    },
    
    # --- DATE-SPECIFIC INFORMATION ---
    {
        "question": "january february march april may june exam dates 2026 2027 schedule academic calendar",
        "answer": "📅 <b>[ACADEMIC CALENDAR 2026-27]</b><br>• Odd Sem: July 15 - Dec 20, 2026<br>• Even Sem: Jan 10 - June 15, 2027<br>• Exam Months: May-June (Odd), Nov-Dec (Even)<br>• Holidays: Diwali, Christmas, Republic Day",
        "tag": "calendar"
    },
    {
        "question": "admission application registration form apply when deadline last date 2026",
        "answer": "📝 <b>[ADMISSIONS 2026]</b><br>• Application Opens: March 1, 2026<br>• Deadline: June 30, 2026<br>• Counseling: July 10-20, 2026<br>• Classes Start: July 25, 2026<br>• Apply: www.nics.edu.in/admissions",
        "tag": "admissions"
    },

    # --- SCHOLARSHIPS & FINANCIAL AID ---
    {
        "question": "scholarship merit financial aid fee waiver discount concession income economic",
        "answer": "🎖️ <b>[SCHOLARSHIPS & FINANCIAL AID]</b><br>• <b>Merit:</b> 25% fee waiver for 12th marks > 90%<br>• <b>JEE Topper:</b> 50% waiver for rank < 5000<br>• <b>SC/ST/OBC:</b> Govt fee reimbursement applicable<br>• <b>Sports Quota:</b> 15% concession for state/national players<br>• <b>Sibling Discount:</b> 10% off for siblings<br>• <b>Education Loans:</b> Tie-ups with SBI, HDFC, Axis Bank<br>• Apply: scholarship@nics.edu.in",
        "tag": "fees"
    },
    # --- LIBRARY ---
    {
        "question": "library books reading study digital online journals ieee access hours open",
        "answer": "📚 <b>[LIBRARY & DIGITAL RESOURCES]</b><br>• <b>Central Library:</b> 50,000+ books, 200+ seating<br>• <b>Digital:</b> IEEE, Springer, ACM, ScienceDirect access<br>• <b>E-Library:</b> 24/7 online via student portal<br>• <b>Hours:</b> Mon-Sat 8 AM - 9 PM, Sun 9 AM - 5 PM<br>• <b>Book Issue:</b> 4 books for 14 days (renewable)<br>• <b>Reading Rooms:</b> AC silent zones + group discussion rooms",
        "tag": "infrastructure"
    },
    # --- WIFI ---
    {
        "question": "wifi internet connectivity network speed bandwidth data connection",
        "answer": "📶 <b>[WIFI & INTERNET]</b><br>• <b>Speed:</b> 1 Gbps backbone, 100 Mbps per user<br>• <b>Coverage:</b> 100% campus (classrooms, labs, hostel, canteen)<br>• <b>Login:</b> Student ID-based authentication<br>• <b>Data:</b> Unlimited academic hours, 5GB/day hostel<br>• <b>Blocked:</b> Torrents, gaming during class hours<br>• <b>Support:</b> IT Help Desk, Ground Floor, Admin Block",
        "tag": "infrastructure"
    },
    # --- SPORTS ---
    {
        "question": "sports gym fitness cricket football basketball volleyball tennis badminton ground playground athletics swimming",
        "answer": "⚽ <b>[SPORTS & FITNESS]</b><br>• <b>Outdoor:</b> Cricket ground, Football field, Athletics track<br>• <b>Indoor:</b> Badminton, Table Tennis, Chess, Carrom<br>• <b>Gym:</b> Modern fitness center (cardio + weights)<br>• <b>Courts:</b> Floodlit Basketball & Volleyball<br>• <b>Swimming:</b> Semi-Olympic pool (seasonal)<br>• <b>Annual Meet:</b> February every year<br>• <b>Coaching:</b> Professional coaches available<br>• <b>Awards:</b> Sports scholarships for state/national players",
        "tag": "facilities"
    },
    # --- EVENTS & FESTS ---
    {
        "question": "event fest festival cultural techfest hackathon workshop seminar conference annual celebration",
        "answer": "🎉 <b>[EVENTS & FESTS]</b><br>• <b>TechVista (Feb):</b> Tech fest — hackathons, robotics, coding<br>• <b>Spandan (Mar):</b> Cultural fest — music, dance, drama, fashion<br>• <b>Innovate (Aug):</b> Innovation summit — startup pitches<br>• <b>Monthly Workshops:</b> AI, Cloud, Blockchain by industry experts<br>• <b>Hackathons:</b> 4-5/year (prizes up to ₹1 Lakh)<br>• <b>Guest Lectures:</b> IIT/IISc professors, industry leaders<br>• <b>IEEE/ACM Chapters:</b> Regular technical talks",
        "tag": "general"
    },
    # --- ALUMNI ---
    {
        "question": "alumni network graduates pass seniors connection linkedin mentorship old students",
        "answer": "🤝 <b>[ALUMNI NETWORK]</b><br>• <b>Total Alumni:</b> 15,000+ across 20+ countries<br>• <b>Notable:</b> Engineers at Google, Microsoft, Amazon, Apple<br>• <b>Portal:</b> alumni.nics.edu.in (mentorship & networking)<br>• <b>Annual Reunion:</b> December every year<br>• <b>Mentorship:</b> Connect with alumni for career guidance<br>• <b>LinkedIn Group:</b> 8,000+ members<br>• <b>Alumni Talks:</b> Monthly webinars on industry trends",
        "tag": "general"
    },
    # --- INTERNSHIPS ---
    {
        "question": "internship intern summer winter training industrial practice company work experience stipend",
        "answer": "💼 <b>[INTERNSHIPS & TRAINING]</b><br>• <b>Mandatory:</b> 6-week summer internship after 6th sem<br>• <b>Top Companies:</b> Google, Microsoft, Amazon, Infosys, TCS<br>• <b>Stipend Range:</b> ₹10,000 - ₹80,000/month<br>• <b>Support:</b> Resume building, interview prep by Placement Cell<br>• <b>Winter:</b> Optional Dec-Jan (2-4 weeks)<br>• <b>Research:</b> IIT/IISc internships via SPARK/SURGE programs<br>• <b>Credits:</b> Counts as 4 academic credits",
        "tag": "placement"
    },
    # --- ATTENDANCE ---
    {
        "question": "attendance minimum percentage proxy leave absent shortage condonation detention biometric",
        "answer": "📋 <b>[ATTENDANCE POLICY]</b><br>• <b>Minimum:</b> 75% attendance mandatory per subject<br>• <b>Below 65%:</b> Detained from writing exams<br>• <b>65-75%:</b> Condonation with ₹500 fine per subject<br>• <b>Medical Leave:</b> Accepted with certificate (up to 15 days)<br>• <b>Tracking:</b> Biometric + faculty marking (dual system)<br>• <b>Portal:</b> Real-time attendance on Student ERP<br>• <b>Parent Alert:</b> SMS sent when attendance drops below 80%",
        "tag": "academics"
    },
    # --- BACKLOG ---
    {
        "question": "backlog atkt supplementary arrear reappear fail reexam revaluation improvement",
        "answer": "📝 <b>[BACKLOG & REVALUATION]</b><br>• <b>Supplementary Exam:</b> Within 2 months of results<br>• <b>Max Backlogs:</b> Carry up to 4 to next semester<br>• <b>Revaluation:</b> Apply within 15 days (₹300/paper)<br>• <b>Improvement:</b> Re-appear to improve grade<br>• <b>Max Attempts:</b> 3 per subject<br>• <b>Fee:</b> ₹1,000 per subject per attempt<br>• <b>Apply:</b> Through Student ERP portal",
        "tag": "academics"
    },
    # --- LATERAL ENTRY ---
    {
        "question": "lateral entry diploma polytechnic direct second year 2nd year dcet engineering",
        "answer": "🔄 <b>[LATERAL ENTRY ADMISSION]</b><br>• <b>Eligibility:</b> Diploma holders (3-year engineering diploma)<br>• <b>Entry:</b> Direct admission to 2nd year (3rd semester)<br>• <b>Exam:</b> DCET (Diploma Common Entrance Test)<br>• <b>Branches:</b> CSE, ECE, MECH, CIVIL, EEE (limited seats)<br>• <b>Seats:</b> 10% supernumerary per branch<br>• <b>Fees:</b> Same as regular B.Tech students<br>• <b>Documents:</b> Diploma marksheets, DCET scorecard, TC",
        "tag": "admission"
    },
    # --- DRESS CODE ---
    {
        "question": "dress code uniform rules formal wear id card identity",
        "answer": "👔 <b>[DRESS CODE & ID CARD]</b><br>• <b>Weekdays:</b> Formal/smart casual (no shorts, slippers)<br>• <b>Lab Days:</b> Closed-toe shoes mandatory<br>• <b>ID Card:</b> Must be worn visibly on campus<br>• <b>Lost ID:</b> Replacement at Admin Office (₹200)<br>• <b>PE:</b> Sports uniform provided (included in fees)<br>• <b>Fests:</b> Relaxed dress code during cultural events",
        "tag": "general"
    },
    # --- ANTI-RAGGING ---
    {
        "question": "ragging anti complaint safety security harassment bully report helpline",
        "answer": "🛡️ <b>[ANTI-RAGGING & SAFETY]</b><br>• <b>Zero Tolerance:</b> Ragging = punishable offense (expulsion)<br>• <b>Committee:</b> Led by Principal + senior faculty<br>• <b>Helpline:</b> 1800-180-5522 (National Anti-Ragging)<br>• <b>CCTV:</b> 24/7 surveillance across all campus areas<br>• <b>Complaint Box:</b> Anonymous boxes in each building<br>• <b>Counselor:</b> Full-time student counselor available<br>• <b>UGC Affidavit:</b> Mandatory at admission",
        "tag": "general"
    },
    # --- CLUBS & SOCIETIES ---
    {
        "question": "club society technical cultural coding robotics debate drama music dance photography student",
        "answer": "🎭 <b>[STUDENT CLUBS & SOCIETIES]</b><br>• <b>Technical:</b> Coding Club, Robotics, AI/ML Society, Cyber Security<br>• <b>Cultural:</b> Music Society, Dance Crew, Drama Club, Art Circle<br>• <b>Literary:</b> Debate Society, Quiz Club, Writers' Guild<br>• <b>Special:</b> Photography, Film Society, E-Cell (Entrepreneurship)<br>• <b>Community:</b> NSS, NCC, Red Cross, Environment Club<br>• <b>Membership:</b> Free — join during Orientation Week<br>• <b>Events:</b> Each club hosts 3-4 events per semester",
        "tag": "facilities"
    },
    # --- TIMETABLE ---
    {
        "question": "timetable class schedule lecture slot period day routine weekly daily",
        "answer": "🗓️ <b>[TIMETABLE & DAILY SCHEDULE]</b><br>• <b>Lectures:</b> 9:00 AM - 4:00 PM (7 periods/day)<br>• <b>Each Period:</b> 50 min + 10 min break<br>• <b>Lunch:</b> 12:30 PM - 1:30 PM<br>• <b>Labs:</b> 2-hour slots (typically afternoon)<br>• <b>Saturday:</b> Half-day 9 AM - 1 PM (remedial classes)<br>• <b>Portal:</b> Timetable on Student ERP app<br>• <b>Changes:</b> Notified via college app push notification",
        "tag": "academics"
    },
    # --- MEDICAL ---
    {
        "question": "medical health clinic hospital doctor nurse emergency first aid insurance",
        "answer": "🏥 <b>[MEDICAL & HEALTH SERVICES]</b><br>• <b>Campus Clinic:</b> Mon-Sat, 9 AM - 5 PM<br>• <b>Doctor:</b> Full-time MBBS doctor on campus<br>• <b>Emergency:</b> Ambulance on-call 24/7<br>• <b>Hospital:</b> Narayana Health (2 km away)<br>• <b>Insurance:</b> ₹1 Lakh medical insurance included in fees<br>• <b>Mental Health:</b> Counselor available Mon-Fri<br>• <b>First Aid:</b> Kits in every building + sports facility",
        "tag": "facilities"
    }
]

# Build the TF-IDF index
for faq in FAQ_DATA:
    tfidf_retriever.add_faq(faq['question'], faq['answer'], faq['tag'])

tfidf_retriever.build_index()

# --- 5.5 ENTITY-BOOSTED RETRIEVAL ---
def entity_boosted_retrieve(query, entities, threshold=0.1):
    """
    Two-phase entity-boosted retrieval:
    Phase 1: TF-IDF scores all FAQs for the original query
    Phase 2: Boost FAQs whose text matches detected entities (course names, semesters)
    """
    query_lower = query.lower()

    semesters = entities.get('semesters', [])
    courses = entities.get('courses', [])

    # If no entities, just use standard retrieval
    if not semesters and not courses:
        return tfidf_retriever.retrieve(query, threshold)

    # Detect sub-intent from query keywords
    exam_words = ['exam', 'exams', 'examination', 'test', 'schedule', 'date', 'when']
    placement_words = ['placement', 'placements', 'package', 'salary', 'job', 'recruit', 'career']
    course_words = ['course', 'branch', 'subject', 'curriculum', 'syllabus', 'program']

    wants_exam = any(w in query_lower for w in exam_words)
    wants_placement = any(w in query_lower for w in placement_words)
    wants_course = any(w in query_lower for w in course_words)

    # Default: if semesters mentioned but no clear intent, assume exam
    if semesters and not wants_placement and not wants_course:
        wants_exam = True

    # Phase 1: Get TF-IDF scores for ALL FAQs
    query_tokens = preprocess_text(query)
    if not query_tokens:
        return None

    query_vector = tfidf_retriever._calculate_tf_idf(query_tokens)

    scored_faqs = []
    for idx, doc_vector in enumerate(tfidf_retriever.tf_idf_vectors):
        tfidf_score = tfidf_retriever._cosine_similarity(query_vector, doc_vector)
        scored_faqs.append((idx, tfidf_score))

    # Phase 2: Boost FAQs that match detected entities
    # Build entity keywords to look for in FAQ question text
    entity_keywords = []
    for course in courses:
        entity_keywords.append(course.lower())  # e.g. 'mech', 'cs'
    for sem in semesters:
        entity_keywords.append(f"semester {sem}")
        entity_keywords.append(f"sem{sem}")
        entity_keywords.append(f"s{sem}")

    # Determine preferred tag based on sub-intent
    preferred_tags = []
    if wants_exam:
        preferred_tags.append('exams')
    if wants_placement:
        preferred_tags.append('placement')
    if wants_course:
        preferred_tags.append('academics')

    boosted_faqs = []
    for idx, tfidf_score in scored_faqs:
        faq = tfidf_retriever.faqs[idx]
        faq_question = faq['question'].lower()
        faq_tag = faq['tag']

        # Start with TF-IDF score
        final_score = tfidf_score

        # Boost if FAQ question contains detected entity keywords
        entity_match_count = 0
        for keyword in entity_keywords:
            if keyword in faq_question:
                entity_match_count += 1

        if entity_match_count > 0:
            # Strong boost: 0.3 per entity match
            final_score += entity_match_count * 0.3

        # Tag boost: prefer FAQs whose tag matches the detected sub-intent
        if preferred_tags and faq_tag in preferred_tags:
            final_score += 0.15

        boosted_faqs.append((idx, final_score, tfidf_score))

    # Sort by boosted score
    boosted_faqs.sort(key=lambda x: x[1], reverse=True)

    # Return the best match
    if boosted_faqs:
        best_idx, best_boosted_score, best_tfidf_score = boosted_faqs[0]
        if best_tfidf_score >= threshold or best_boosted_score >= threshold + 0.2:
            faq = tfidf_retriever.faqs[best_idx]
            return (faq['answer'], min(best_boosted_score, 1.0), faq['tag'])

    return None


# --- 6. GREETING DETECTION (SIMPLE PATTERN MATCHING) ---
GREETINGS = ["hello", "hi", "hey", "namaste", "greetings", "good morning", "good afternoon"]
FAREWELL = ["bye", "goodbye", "exit", "quit", "see you", "later"]

def is_greeting(text):
    text_lower = text.lower()
    return any(greeting in text_lower for greeting in GREETINGS)

def is_farewell(text):
    text_lower = text.lower()
    return any(word in text_lower for word in FAREWELL)

# --- 6.5 OUT-OF-SCOPE DETECTION ---
OUT_OF_SCOPE_PATTERNS = [
    # General knowledge / non-college
    'weather', 'temperature', 'rain', 'forecast',
    'movie', 'film', 'song', 'music', 'actor', 'actress',
    'cricket score', 'football score', 'ipl', 'world cup',
    'recipe', 'cook', 'food recipe',
    'joke', 'funny', 'riddle',
    'news', 'politics', 'election', 'minister', 'president',
    'stock', 'share market', 'bitcoin', 'crypto',
    'calculate', 'solve', 'math problem', 'equation',
    'translate', 'meaning of', 'define',
    'who is', 'who was', 'capital of', 'population of',
    'distance between', 'how far',
    'game', 'play', 'download',
    'instagram', 'facebook', 'twitter', 'youtube', 'tiktok',
    'boyfriend', 'girlfriend', 'love', 'relationship',
    'your name', 'how old are you', 'are you human', 'are you real', 'who made you',
]

def is_out_of_scope(text):
    """Detect queries that are clearly outside the college chatbot's domain"""
    text_lower = text.lower().strip()
    return any(pattern in text_lower for pattern in OUT_OF_SCOPE_PATTERNS)

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

def update_context(session_id, query, response, tag=None, entities=None, intent=None):
    """Update conversation context for a session, storing entities and intent per turn"""
    if session_id not in conversation_contexts:
        conversation_contexts[session_id] = {
            'history': [],
            'last_tag': None,
            'last_entities': None,
            'last_intent': None,
            'query_count': 0,
            'consecutive_fallbacks': 0
        }
    
    context = conversation_contexts[session_id]
    context['history'].append({
        'query': query,
        'response': response,
        'tag': tag,
        'entities': entities or {},
        'intent': intent,
        'timestamp': datetime.now().isoformat()
    })
    context['last_tag'] = tag
    context['last_entities'] = entities or {}
    context['last_intent'] = intent
    context['query_count'] += 1
    
    # Track consecutive fallbacks for escalation
    if tag in ('fallback', 'out-of-scope'):
        context['consecutive_fallbacks'] = context.get('consecutive_fallbacks', 0) + 1
    else:
        context['consecutive_fallbacks'] = 0
    
    # Keep only last 10 interactions to save memory
    if len(context['history']) > 10:
        context['history'] = context['history'][-10:]

def get_context_response(session_id, query, new_entities=None, new_intent=None):
    """
    Handle follow-up queries by merging new entities/intent with previous context.
    Detects short follow-ups like "For third year?", "and ECE?", "What about placements?"
    Returns: (response, tag, merged_entities, entity_context) or None
    """
    if session_id not in conversation_contexts:
        return None
    
    context = conversation_contexts[session_id]
    if not context['history']:
        return None
    
    query_lower = query.lower().strip()
    words = query_lower.split()
    new_entities = new_entities or {}
    
    # --- Detect if this is a follow-up ---
    is_followup = False
    
    # Check 1: "tell me more", "elaborate", "details" etc.
    more_phrases = ["more", "detail", "details", "elaborate", "explain", "tell me more", "anything else"]
    if any(phrase in query_lower for phrase in more_phrases):
        if context['last_tag']:
            return (
                f"For more details about <b>{context['last_tag']}</b>, please contact our admission cell at +91 98765 43210 or email admissions@nics.edu.in",
                context['last_tag'],
                context['last_entities'],
                ''
            )
    
    # Check 2: Short query starting with follow-up words
    followup_starters = ['for', 'and', 'what about', 'how about', 'in', 'of']
    starts_with_followup = any(query_lower.startswith(s) for s in followup_starters)
    
    # Check 3: Very short query (1-4 words) that has entities
    has_new_entities = (
        bool(new_entities.get('courses')) or 
        bool(new_entities.get('semesters')) or
        bool(new_entities.get('years'))
    )
    is_short_with_entities = len(words) <= 4 and has_new_entities
    
    # Check 4: Query is just a topic word + entity (e.g. "cs placements?", "semester 3?")
    topic_words = ['exam', 'exams', 'placement', 'placements', 'course', 'fee', 'fees', 'salary', 'package']
    is_topic_switch = len(words) <= 3 and any(w in query_lower for w in topic_words)
    
    if starts_with_followup or is_short_with_entities or is_topic_switch:
        is_followup = True
    
    if not is_followup:
        return None
    
    # --- Merge entities and intent with previous context ---
    prev_entities = context.get('last_entities', {}) or {}
    prev_intent = context.get('last_intent')
    prev_tag = context.get('last_tag')
    
    merged_entities = {
        'courses': list(new_entities.get('courses', []) or prev_entities.get('courses', [])),
        'semesters': list(new_entities.get('semesters', []) or prev_entities.get('semesters', [])),
        'dates': list(new_entities.get('dates', []) or prev_entities.get('dates', [])),
        'months': list(new_entities.get('months', []) or prev_entities.get('months', [])),
        'years': list(new_entities.get('years', []) or prev_entities.get('years', []))
    }
    
    # Determine the effective intent/topic
    # If user mentions a new topic word, use that; otherwise carry forward
    exam_words = ['exam', 'exams', 'examination', 'schedule', 'date']
    placement_words = ['placement', 'placements', 'package', 'salary', 'job']
    course_words = ['course', 'branch', 'subject', 'curriculum']
    fee_words = ['fee', 'fees', 'cost', 'tuition']
    
    if any(w in query_lower for w in exam_words):
        effective_topic = 'exams'
    elif any(w in query_lower for w in placement_words):
        effective_topic = 'placement'
    elif any(w in query_lower for w in course_words):
        effective_topic = 'academics'
    elif any(w in query_lower for w in fee_words):
        effective_topic = 'fees'
    else:
        effective_topic = prev_tag  # carry forward from previous turn
    
    # If the user explicitly switched topics, drop irrelevant entities
    # Semesters are only meaningful for exam queries
    user_switched_topic = effective_topic != prev_tag
    if user_switched_topic and effective_topic in ('placement', 'academics', 'fees'):
        merged_entities['semesters'] = []
    
    # Build a synthetic query from merged entities + topic
    query_parts = []
    if effective_topic:
        query_parts.append(effective_topic)
    for course in merged_entities.get('courses', []):
        query_parts.append(course.lower())
    for sem in merged_entities.get('semesters', []):
        query_parts.append(f"semester {sem}")
    
    if not query_parts:
        return None
    
    synthetic_query = ' '.join(query_parts)
    
    # Run entity-boosted retrieval with merged entities
    result = entity_boosted_retrieve(synthetic_query, merged_entities, threshold=0.05)
    
    if result:
        answer, confidence, tag = result
        entity_ctx = entity_extractor.format_entity_context(merged_entities)
        if entity_ctx:
            answer = f"🔍 <b>[Detected: {entity_ctx}]</b><br><br>{answer}"
        return (answer, tag, merged_entities, entity_ctx)
    
    return None

# --- 7. FLASK ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

# --- MULTICHANNEL: Core Engine (channel-agnostic) ---

def process_message(raw_input, session_id):
    """
    Channel-agnostic message processor. Runs the full 6-priority pipeline
    and returns a raw dict with all response fields.
    This is the core engine that all channel adapters call.
    """
    # Priority 1: Check for greetings (time-aware)
    if is_greeting(raw_input):
        hour = datetime.now().hour
        if hour < 12:
            time_greeting = "Good Morning"
        elif hour < 17:
            time_greeting = "Good Afternoon"
        else:
            time_greeting = "Good Evening"
        response = f"<b>{time_greeting}! 🙏</b> Welcome to NICS. I can help with admissions, fees, placements, exams, hostel, courses, and more! Ask me anything."
        update_context(session_id, raw_input, response, 'greeting')
        return {
            'response': response,
            'method': 'greeting',
            'confidence': 1.0,
            'intent': 'greeting',
            'intent_confidence': 1.0,
            'entities': {},
            'entity_context': '',
            'suggestions': []
        }
    
    # Priority 2: Check for farewell
    if is_farewell(raw_input):
        response = "Goodbye! All the best for your engineering journey. <b>Jai Hind! 🇮🇳</b>"
        update_context(session_id, raw_input, response, 'farewell')
        return {
            'response': response,
            'method': 'farewell',
            'confidence': 1.0,
            'intent': 'farewell',
            'intent_confidence': 1.0,
            'entities': {},
            'entity_context': '',
            'suggestions': []
        }
    
    # CLASSIFY INTENT
    detected_intent, intent_confidence = intent_classifier.classify(raw_input)
    
    # EXTRACT ENTITIES (dates, courses, semesters)
    extracted_entities = entity_extractor.extract_entities(raw_input)
    entity_context = entity_extractor.format_entity_context(extracted_entities)
    
    # Priority 3: Check conversation context (follow-up questions)
    context_result = get_context_response(session_id, raw_input, extracted_entities, detected_intent)
    if context_result:
        ctx_response, ctx_tag, ctx_entities, ctx_entity_context = context_result
        update_context(session_id, raw_input, ctx_response, ctx_tag, ctx_entities, detected_intent)
        return {
            'response': ctx_response,
            'method': 'context',
            'confidence': 0.95,
            'intent': detected_intent,
            'intent_confidence': round(float(intent_confidence), 3),
            'entities': ctx_entities,
            'entity_context': ctx_entity_context,
            'suggestions': []
        }
    
    # Priority 4: Rule-based pattern matching for edge cases
    rule_result = rule_based_matcher(raw_input)
    if rule_result:
        answer, confidence = rule_result
        update_context(session_id, raw_input, answer, 'rule-based', extracted_entities, detected_intent)
        return {
            'response': answer,
            'method': 'rule-based',
            'confidence': confidence,
            'intent': detected_intent,
            'intent_confidence': round(intent_confidence, 3),
            'entities': extracted_entities,
            'entity_context': entity_context,
            'suggestions': []
        }
    
    # Priority 5: Use ENTITY-BOOSTED TF-IDF retrieval for FAQ matching
    result = entity_boosted_retrieve(raw_input, extracted_entities, threshold=0.1)
    
    if result:
        answer, confidence, tag = result
        # Prepend entity context so user sees what was detected
        if entity_context:
            answer = f"🔍 <b>[Detected: {entity_context}]</b><br><br>{answer}"
        update_context(session_id, raw_input, answer, tag, extracted_entities, detected_intent)
        return {
            'response': answer,
            'method': 'tfidf',
            'confidence': round(confidence, 3),
            'tag': tag,
            'intent': detected_intent,
            'intent_confidence': round(intent_confidence, 3),
            'entities': extracted_entities,
            'entity_context': entity_context,
            'suggestions': []
        }
    
    # --- THREE-TIER FALLBACK STRATEGY ---
    ctx = conversation_contexts.get(session_id, {})
    consecutive = ctx.get('consecutive_fallbacks', 0)
    
    # Quick-reply suggestions based on detected intent
    intent_quick_replies = {
        'admissions': [
            'How do I apply?',
            'What is the admission process?',
            'What are the eligibility criteria?'
        ],
        'exams': [
            'Which exams are accepted?',
            'What is the JEE cutoff?',
            'When are semester exams?'
        ],
        'fees': [
            'What are the fees?',
            'Are there scholarships?',
            'What is the hostel fee?'
        ],
        'placements': [
            'Tell me about placements',
            'What is the average package?',
            'Which companies visit campus?'
        ],
        'facilities': [
            'What facilities are available?',
            'Tell me about the hostel',
            'Is there a library?'
        ],
        'academics': [
            'What courses are offered?',
            'Tell me about CS program',
            'Who are the faculty?'
        ],
        'general': [
            'Tell me about admissions',
            'What are the fees?',
            'Tell me about placements'
        ]
    }
    
    suggestions = intent_quick_replies.get(detected_intent, intent_quick_replies['general'])
    
    # TIER 2: Out-of-scope detection
    if is_out_of_scope(raw_input):
        fallback = (
            "🚫 <b>Out of Scope</b><br>"
            "I'm the <b>NICS College Assistant</b> — I can only help with college-related queries.<br><br>"
            "Here are some things I can help with:"
        )
        update_context(session_id, raw_input, fallback, 'out-of-scope', extracted_entities, detected_intent)
        return {
            'response': fallback,
            'method': 'out-of-scope',
            'confidence': 0.0,
            'intent': detected_intent,
            'intent_confidence': round(float(intent_confidence), 3),
            'entities': extracted_entities,
            'entity_context': entity_context,
            'suggestions': ['Tell me about admissions', 'What are the fees?', 'Tell me about placements']
        }
    
    # TIER 3: Human handover (2+ consecutive fallbacks)
    if consecutive >= 1:
        fallback = (
            "😔 I'm still having trouble understanding your question.<br><br>"
            "<div style='background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 12px; padding: 14px; margin-top: 8px; border-left: 4px solid #f59e0b;'>"
            "<b>📞 Talk to a Human Advisor</b><br><br>"
            "📧 Email: <a href='mailto:admissions@nics.edu.in' style='color: #1d4ed8; font-weight: 600;'>admissions@nics.edu.in</a><br>"
            "📱 Phone: <a href='tel:+919876543210' style='color: #1d4ed8; font-weight: 600;'>+91 98765 43210</a><br>"
            "🏢 Visit: Admission Office, NICS Campus<br>"
            "⏰ Hours: Mon-Sat, 9:00 AM - 5:00 PM"
            "</div>"
        )
        update_context(session_id, raw_input, fallback, 'fallback', extracted_entities, detected_intent)
        return {
            'response': fallback,
            'method': 'handover',
            'confidence': 0.0,
            'intent': detected_intent,
            'intent_confidence': round(float(intent_confidence), 3),
            'entities': extracted_entities,
            'entity_context': entity_context,
            'suggestions': suggestions
        }
    
    # TIER 1: Clarification with suggestions (1st fallback)
    fallback = (
        f"🤔 I didn't quite understand that.<br>"
        f"It seems you might be asking about <b>{detected_intent}</b>.<br><br>"
        f"Try one of these:"
    )
    
    update_context(session_id, raw_input, fallback, 'fallback', extracted_entities, detected_intent)
    return {
        'response': fallback,
        'method': 'fallback',
        'confidence': 0.0,
        'intent': detected_intent,
        'intent_confidence': round(float(intent_confidence), 3),
        'entities': extracted_entities,
        'entity_context': entity_context,
        'suggestions': suggestions
    }


# --- MULTICHANNEL: HTML Stripping Utility ---

def strip_html(html_text):
    """Strip HTML tags from response text, preserving emoji and line breaks."""
    import re as _re
    text = html_text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    text = _re.sub(r'<div[^>]*>', '\n', text)
    text = text.replace('</div>', '\n')
    text = _re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>[^<]*</a>', r'\1', text)
    text = _re.sub(r'<[^>]+>', '', text)
    text = _re.sub(r'\n{3,}', '\n\n', text).strip()
    return text


# --- CHANNEL 1: Web (existing HTML route) ---

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    data = request.get_json()
    raw_input = data.get('message', '')
    session_id = get_or_create_session()
    result = process_message(raw_input, session_id)
    log_interaction(raw_input, result, channel='web', session_id=session_id)
    return jsonify(result)


# --- CHANNEL 2: Mobile API (compact plain-text JSON) ---

@app.route('/api/v1/chat', methods=['POST'])
def mobile_chat():
    """
    Mobile-optimized API endpoint.
    Returns plain-text responses (no HTML) with compact JSON structure.
    """
    data = request.get_json()
    raw_input = data.get('message', '')
    session_id = data.get('session_id', get_or_create_session())
    
    result = process_message(raw_input, session_id)
    log_interaction(raw_input, result, channel='mobile', session_id=session_id)
    
    return jsonify({
        'channel': 'mobile',
        'text': strip_html(result['response']),
        'intent': result.get('intent', 'general'),
        'confidence': result.get('confidence', 0.0),
        'method': result.get('method', 'unknown'),
        'suggestions': result.get('suggestions', []),
        'entities': result.get('entities', {}),
        'session_id': session_id
    })


# --- CHANNEL 3: WhatsApp Webhook (WhatsApp-formatted payload) ---

@app.route('/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    WhatsApp-style webhook endpoint.
    Returns plain-text with numbered quick-replies instead of HTML chips.
    Simulates the payload format a WhatsApp Business API would expect.
    """
    data = request.get_json()
    raw_input = data.get('message', data.get('Body', ''))
    sender = data.get('from', data.get('From', '+910000000000'))
    session_id = data.get('session_id', sender)
    
    result = process_message(raw_input, session_id)
    log_interaction(raw_input, result, channel='whatsapp', session_id=session_id)
    
    # Convert HTML to plain text
    body = strip_html(result['response'])
    
    # Append numbered quick-replies (WhatsApp style)
    suggestions = result.get('suggestions', [])
    quick_replies = []
    if suggestions:
        body += '\n\n'
        for i, s in enumerate(suggestions, 1):
            body += f"Reply {i}: {s}\n"
            quick_replies.append({'id': str(i), 'title': s})
    
    return jsonify({
        'channel': 'whatsapp',
        'to': sender,
        'type': 'text',
        'body': body.strip(),
        'method': result.get('method', 'unknown'),
        'intent': result.get('intent', 'general'),
        'confidence': result.get('confidence', 0.0),
        'quick_replies': quick_replies,
        'session_id': session_id
    })


# --- 10. ANALYTICS & CONTINUOUS IMPROVEMENT ---

import json
import os
from datetime import datetime as _dt

CHAT_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chat_logs.json')

def _load_logs():
    """Load chat logs from file."""
    if not os.path.exists(CHAT_LOG_FILE):
        return []
    try:
        with open(CHAT_LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def _save_logs(logs):
    """Save chat logs to file."""
    with open(CHAT_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def log_interaction(query, result, channel='web', session_id=None):
    """
    Log every interaction to chat_logs.json with auto-labeling.
    Labels: successful, low-confidence, fallback, out-of-scope, handover, greeting, farewell
    """
    method = result.get('method', 'unknown')
    confidence = result.get('confidence', 0.0)
    
    # Auto-label based on method and confidence
    if method in ('greeting', 'farewell'):
        label = method
    elif method == 'out-of-scope':
        label = 'out-of-scope'
    elif method == 'handover':
        label = 'handover'
    elif method == 'fallback':
        label = 'fallback'
    elif confidence < 0.3:
        label = 'low-confidence'
    else:
        label = 'successful'
    
    entry = {
        'timestamp': _dt.now().isoformat(),
        'query': query,
        'channel': channel,
        'session_id': session_id or 'unknown',
        'method': method,
        'confidence': round(confidence, 3),
        'intent': result.get('intent', 'general'),
        'entities': result.get('entities', {}),
        'label': label,
        'response_preview': strip_html(result.get('response', ''))[:120]
    }
    
    logs = _load_logs()
    logs.append(entry)
    _save_logs(logs)
    return entry


# --- Analytics Dashboard ---

@app.route('/analytics', methods=['GET'])
def analytics_dashboard():
    """
    Analytics dashboard showing interaction stats:
    - Total queries, success rate, fallback rate
    - Intent distribution, channel breakdown
    - Low-confidence and failed queries for review
    """
    logs = _load_logs()
    
    if not logs:
        return jsonify({'message': 'No interactions logged yet.', 'total': 0})
    
    total = len(logs)
    
    # Label distribution
    label_counts = {}
    for entry in logs:
        lbl = entry.get('label', 'unknown')
        label_counts[lbl] = label_counts.get(lbl, 0) + 1
    
    # Intent distribution
    intent_counts = {}
    for entry in logs:
        intent = entry.get('intent', 'unknown')
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
    
    # Channel distribution
    channel_counts = {}
    for entry in logs:
        ch = entry.get('channel', 'unknown')
        channel_counts[ch] = channel_counts.get(ch, 0) + 1
    
    # Method distribution
    method_counts = {}
    for entry in logs:
        m = entry.get('method', 'unknown')
        method_counts[m] = method_counts.get(m, 0) + 1
    
    # Average confidence
    confidences = [e.get('confidence', 0) for e in logs if e.get('label') not in ('greeting', 'farewell')]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    # Success/fallback rates
    successful = label_counts.get('successful', 0)
    fallbacks = label_counts.get('fallback', 0) + label_counts.get('out-of-scope', 0) + label_counts.get('handover', 0)
    low_conf = label_counts.get('low-confidence', 0)
    
    success_rate = round(successful / total * 100, 1) if total else 0
    fallback_rate = round(fallbacks / total * 100, 1) if total else 0
    
    # Recent low-confidence and fallback queries (for review)
    needs_review = [
        {
            'query': e['query'],
            'label': e['label'],
            'intent': e['intent'],
            'confidence': e['confidence'],
            'timestamp': e['timestamp']
        }
        for e in logs
        if e.get('label') in ('fallback', 'out-of-scope', 'handover', 'low-confidence')
    ][-20:]  # Last 20
    
    return jsonify({
        'total_interactions': total,
        'success_rate': f"{success_rate}%",
        'fallback_rate': f"{fallback_rate}%",
        'average_confidence': round(avg_confidence, 3),
        'label_distribution': label_counts,
        'intent_distribution': dict(sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)),
        'channel_distribution': channel_counts,
        'method_distribution': method_counts,
        'queries_needing_review': needs_review
    })


# --- Improvement Proposals ---

@app.route('/analytics/improvements', methods=['GET'])
def analytics_improvements():
    """
    Auto-propose improvements based on logged data:
    1. Frequent fallback queries → suggest new FAQs
    2. Low-confidence intent matches → suggest better keywords
    3. Repeated out-of-scope topics → suggest new intents or scope expansion
    4. Pattern gaps → suggest new rule-based patterns
    """
    logs = _load_logs()
    
    if not logs:
        return jsonify({'message': 'No data to analyze. Interact with the chatbot first.', 'proposals': []})
    
    proposals = []
    
    # --- 1. Frequent fallback queries → New FAQ suggestions ---
    fallback_queries = [e['query'] for e in logs if e.get('label') in ('fallback', 'low-confidence')]
    
    if fallback_queries:
        # Group similar fallback queries by detected intent
        intent_groups = {}
        for e in logs:
            if e.get('label') in ('fallback', 'low-confidence'):
                intent = e.get('intent', 'general')
                if intent not in intent_groups:
                    intent_groups[intent] = []
                intent_groups[intent].append(e['query'])
        
        for intent, queries in intent_groups.items():
            if len(queries) >= 2:
                proposals.append({
                    'type': 'NEW_FAQ',
                    'priority': 'HIGH' if len(queries) >= 3 else 'MEDIUM',
                    'description': f"Add new FAQ for '{intent}' intent — {len(queries)} failed queries detected",
                    'sample_queries': list(set(queries))[:5],
                    'suggestion': f"Create a FAQ entry in FAQ_DATA with tag='{intent}' covering these query patterns"
                })
    
    # --- 2. Out-of-scope trends → Scope expansion ---
    oos_queries = [e['query'] for e in logs if e.get('label') == 'out-of-scope']
    
    if len(oos_queries) >= 2:
        # Check if any out-of-scope queries share common themes
        oos_words = {}
        for q in oos_queries:
            for word in q.lower().split():
                if len(word) > 3:
                    oos_words[word] = oos_words.get(word, 0) + 1
        
        frequent_oos = {w: c for w, c in oos_words.items() if c >= 2}
        if frequent_oos:
            proposals.append({
                'type': 'SCOPE_EXPANSION',
                'priority': 'LOW',
                'description': f"Frequently asked out-of-scope topics ({len(oos_queries)} queries)",
                'frequent_topics': dict(sorted(frequent_oos.items(), key=lambda x: x[1], reverse=True)),
                'suggestion': "Consider whether these topics should be added to the chatbot's scope"
            })
    
    # --- 3. Low-confidence matches → Better keywords ---
    low_conf = [e for e in logs if e.get('label') == 'low-confidence']
    
    if low_conf:
        # Group by intent
        for e in low_conf:
            query_words = set(e['query'].lower().split())
            intent = e.get('intent', 'general')
            intent_keywords = set(INTENT_DEFINITIONS.get(intent, {}).get('keywords', []))
            missing_words = query_words - intent_keywords - STOP_WORDS
            
            if missing_words:
                proposals.append({
                    'type': 'KEYWORD_GAP',
                    'priority': 'MEDIUM',
                    'description': f"Query '{e['query']}' matched '{intent}' with low confidence ({e['confidence']})",
                    'missing_keywords': list(missing_words)[:5],
                    'suggestion': f"Add these keywords to INTENT_DEFINITIONS['{intent}']['keywords']: {list(missing_words)[:3]}"
                })
    
    # --- 4. Handover frequency → FAQ gaps ---
    handover_count = sum(1 for e in logs if e.get('label') == 'handover')
    if handover_count >= 2:
        handover_queries = [e['query'] for e in logs if e.get('label') == 'handover']
        proposals.append({
            'type': 'FAQ_GAP',
            'priority': 'HIGH',
            'description': f"{handover_count} conversations escalated to human handover",
            'queries': list(set(handover_queries))[:5],
            'suggestion': "These queries caused repeated failures. Create new FAQs to cover these topics."
        })
    
    # --- 5. Overall statistics summary ---
    total = len(logs)
    success_count = sum(1 for e in logs if e.get('label') == 'successful')
    
    intent_coverage = {}
    for intent in INTENT_DEFINITIONS:
        matched = sum(1 for e in logs if e.get('intent') == intent and e.get('label') == 'successful')
        total_for_intent = sum(1 for e in logs if e.get('intent') == intent)
        if total_for_intent > 0:
            intent_coverage[intent] = {
                'total': total_for_intent,
                'successful': matched,
                'success_rate': f"{round(matched/total_for_intent*100, 1)}%"
            }
    
    # Deduplicate proposals by description
    seen = set()
    unique_proposals = []
    for p in proposals:
        key = p['description']
        if key not in seen:
            seen.add(key)
            unique_proposals.append(p)
    
    return jsonify({
        'analysis_timestamp': _dt.now().isoformat(),
        'total_interactions_analyzed': total,
        'overall_success_rate': f"{round(success_count/total*100, 1)}%" if total else "0%",
        'intent_coverage': intent_coverage,
        'improvement_proposals': unique_proposals,
        'proposal_count': len(unique_proposals)
    })


@app.route('/analytics/logs', methods=['GET'])
def analytics_logs():
    """Return raw interaction logs (paginated, last N entries)."""
    limit = request.args.get('limit', 50, type=int)
    label_filter = request.args.get('label', None)
    
    logs = _load_logs()
    
    if label_filter:
        logs = [e for e in logs if e.get('label') == label_filter]
    
    return jsonify({
        'total': len(logs),
        'showing': min(limit, len(logs)),
        'logs': logs[-limit:]
    })


@app.route('/analytics/clear', methods=['POST'])
def analytics_clear():
    """Clear all interaction logs (for testing)."""
    _save_logs([])
    return jsonify({'message': 'All logs cleared.', 'total': 0})


# --- FEEDBACK ENDPOINT ---

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit thumbs up/down feedback for a bot response."""
    data = request.get_json()
    query = data.get('query', '')
    vote = data.get('vote', '')  # 'up' or 'down'

    logs = _load_logs()
    for entry in reversed(logs):
        if entry.get('query') == query:
            entry['feedback'] = vote
            break
    _save_logs(logs)

    return jsonify({'status': 'ok', 'vote': vote})


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

@app.route('/test_entities', methods=['POST'])
def test_entity_extraction():
    """Test endpoint specifically for entity extraction"""
    data = request.get_json()
    query = data.get('message', '')
    
    # Extract entities
    entities = entity_extractor.extract_entities(query)
    entity_context = entity_extractor.format_entity_context(entities)
    
    return jsonify({
        'query': query,
        'entities': entities,
        'entity_context': entity_context,
        'status': 'Entity extraction working!'
    })

if __name__ == '__main__':
    app.run(debug=True)
