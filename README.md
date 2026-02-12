# 🤖 Smart FAQ Chatbot with Intent Classification

An intelligent FAQ chatbot for educational institutions built with Flask, featuring advanced NLP techniques including TF-IDF retrieval, intent classification, and context-aware responses.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### Core Functionality
- **📚 13 Comprehensive FAQs** - Covers admissions, fees, placements, facilities, and more
- **🔍 Advanced Text Preprocessing** - Lowercasing, tokenization, stopword removal, punctuation handling, spelling correction
- **🎯 Synonym-Aware Matching** - 77+ synonym mappings across 10 semantic categories
- **📊 TF-IDF Retrieval** - Custom implementation with cosine similarity for intelligent FAQ matching
- **🧠 Intent Classification** - 7-category classifier for smart query routing (admissions, exams, fees, placements, facilities, academics, general)

### Advanced Features
- **✏️ Spelling Correction** - Auto-corrects 30+ common misspellings
- **🎲 Rule-Based Pattern Matching** - 7 pattern types for edge case handling
- **💬 Conversation Context** - Session-based memory tracking last 10 interactions
- **🔄 Multi-Layer Response Strategy** - 6-priority intelligent fallback chain
- **💡 Intent-Based Suggestions** - Smart query recommendations when no match found
- **🛠️ Debug Endpoints** - Testing and development utilities

## 🎯 Intent Classification

The chatbot intelligently classifies queries into 7 categories:

| Intent | Description | Weight | Keywords |
|--------|-------------|--------|----------|
| **Admissions** | Application process, eligibility | 1.2 | admission, apply, register, eligibility |
| **Exams** | Entrance exams, cutoffs, results | 1.0 | exam, jee, gate, cutoff, marks |
| **Fees** | Tuition, costs, scholarships | 1.3 | fee, tuition, cost, scholarship |
| **Placements** | Jobs, careers, salary | 1.1 | placement, job, salary, package |
| **Facilities** | Hostel, transport, infrastructure | 0.9 | hostel, transport, library, sports |
| **Academics** | Courses, curriculum, faculty | 1.0 | course, program, faculty, branch |
| **General** | Timings, contact, location | 0.8 | time, contact, address, location |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flask

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/dhanish0711/FAQ-Chatbot.git
cd FAQ-Chatbot
```

2. **Install dependencies**
```bash
pip install flask
```

3. **Run the application**
```bash
python app.py
```

4. **Open in browser**
```
http://localhost:5000
```

## 📁 Project Structure

```
FAQ-Chatbot/
├── app.py              # Main Flask application with all logic
├── templates/
│   └── index.html      # Web interface
└── README.md          # This file
```

## 🔧 API Endpoints

### 1. Get Response
```http
POST /get_response
Content-Type: application/json

{
  "message": "What are the fees?"
}
```

**Response:**
```json
{
  "response": "💰 [FEES STRUCTURE] B.Tech: ₹1.5 Lakhs/year...",
  "method": "tfidf",
  "confidence": 0.85,
  "tag": "fees",
  "intent": "fees",
  "intent_confidence": 1.3
}
```

### 2. Classify Intent (Debug)
```http
POST /classify_intent
Content-Type: application/json

{
  "message": "How do I apply for admission?"
}
```

**Response:**
```json
{
  "query": "How do I apply for admission?",
  "detected_intent": "admissions",
  "confidence": 1.2,
  "all_intent_scores": {
    "admissions": 1.2,
    "fees": 0.0,
    ...
  }
}
```

### 3. View TF-IDF Debug
```http
POST /debug
Content-Type: application/json

{
  "message": "fees and placements"
}
```

### 4. View Conversation Context
```http
GET /context
```

## 🧪 Testing Examples

### Example 1: Basic Query
```
User: "What are the fees?"
Bot: 💰 [FEES STRUCTURE] B.Tech: ₹1.5 Lakhs/year, M.Tech: ₹90,000/year
Intent: fees (confidence: 1.3)
```

### Example 2: Spelling Correction
```
User: "What are the feees?"  # Misspelled
Bot: (Auto-corrects to "fees")
     💰 [FEES STRUCTURE] ...
Intent: fees
```

### Example 3: Synonym Matching
```
User: "What's the tuition cost?"  # Synonyms
Bot: (Maps: tuition→fee, cost→fee)
     💰 [FEES STRUCTURE] ...
Intent: fees
```

### Example 4: Context Awareness
```
User: "What are the fees?"
Bot: 💰 [FEES STRUCTURE] ...

User: "Tell me more"  # Follow-up
Bot: "For more details about fees, contact +91 98765 43210"
Intent: context
```

## 🏗️ Architecture

### Preprocessing Pipeline
```
Input Query
    ↓
Lowercase → Remove Punctuation → Tokenize
    ↓
Spelling Correction → Stopword Removal → Synonym Normalization
    ↓
Processed Tokens
```

### Response Generation Flow
```
1. Greetings/Farewells (exact match)
2. Conversation Context (follow-ups)
3. Rule-Based Patterns (edge cases)
4. Intent Classification (7 categories)
5. TF-IDF Retrieval (FAQ matching)
6. Intelligent Fallback (with suggestions)
```

## 📊 Implementation Details

### TF-IDF Algorithm
- **Term Frequency (TF)**: `count(term) / total_words`
- **Inverse Document Frequency (IDF)**: `log(total_docs / docs_with_term)`
- **Cosine Similarity**: `dot(vec1, vec2) / (||vec1|| × ||vec2||)`

### Intent Classification
- **Hybrid Approach**: Keyword matching + TF-IDF-like vectors
- **Weighted Scoring**: Different priorities for different intents
- **Training Data**: Keywords + example phrases per intent

## 🎨 Customization

### Adding New FAQs
Edit `FAQ_DATA` in `app.py`:
```python
FAQ_DATA.append({
    "question": "keywords for matching",
    "answer": "HTML formatted answer",
    "tag": "category"
})
```

### Adding New Intents
Update `INTENT_DEFINITIONS` in `app.py`:
```python
INTENT_DEFINITIONS["new_intent"] = {
    "keywords": ["keyword1", "keyword2"],
    "examples": ["example question 1"],
    "weight": 1.0
}
```

### Adding Synonyms
Update `NORMALIZATION_MAP` in `app.py`:
```python
NORMALIZATION_MAP["synonym"] = "canonical_form"
```

## 📈 Performance Metrics

- **FAQs**: 13 topics
- **Synonyms**: 77+ mappings
- **Spelling Corrections**: 30+ common errors
- **Intents**: 7 categories
- **Response Time**: < 100ms average
- **Accuracy**: High confidence matching with TF-IDF

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Your Name - Dhanish Ladwani - (https://github.com/dhanish0711)

## 🙏 Acknowledgments

- Built with Flask framework
- Uses custom TF-IDF implementation (no external NLP libraries)
- Inspired by modern chatbot architectures

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**⭐ Star this repository if you found it helpful!**
