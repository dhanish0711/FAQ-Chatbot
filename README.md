# 🤖 Smart FAQ Chatbot with Intent Classification

An intelligent, context-aware FAQ chatbot for educational institutions built with Flask — featuring TF-IDF retrieval, entity-boosted search, multi-turn conversation handling, voice input, dark mode, feedback system, and a three-tier fallback strategy with human handover.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![NLP](https://img.shields.io/badge/NLP-Custom_TF--IDF-orange.svg)

---

## ✨ Features

### 🔍 Core NLP Pipeline
- **Advanced Text Preprocessing** — Lowercasing, tokenization, stopword removal, punctuation handling, spelling correction (50+ common errors)
- **Synonym-Aware Matching** — 110+ synonym mappings across 20+ semantic categories (fees, courses, placements, hostel, scholarships, library, clubs, attendance, medical, parking, backlog, timetable, etc.)
- **TF-IDF Retrieval** — Custom cosine-similarity implementation for intelligent FAQ matching (no external NLP libraries)
- **Intent Classification** — 7-category weighted keyword classifier (admissions, exams, fees, placements, facilities, academics, general)

### 🧠 Entity Extraction & Boosted Retrieval
- **Course Detection**: CS, IT, ECE, MECH, CIVIL, EEE, BTECH, MTECH — with word-boundary matching to prevent false positives
- **Semester Detection**: Formats like "sem 5", "semester 3", "5th sem", "s5"
- **Date / Month / Year Extraction**: Multiple formats (dd/mm/yyyy, "15 March 2026", etc.)
- **Entity-Boosted Retrieval**: Two-phase scoring — TF-IDF base score + entity overlap boost (+0.3 per entity match) + sub-intent tag boost (+0.15)

### 💬 Multi-Turn Conversation Context
- **Follow-up Detection** — Recognizes short follow-ups ("for semester 3?", "and ECE?", "what about placements?")
- **Entity Merging** — New entities from follow-ups replace same-type entities from context; others carry forward
- **Topic-Switch Filtering** — When user explicitly switches topics (exams → placements), irrelevant entities (semesters) are automatically dropped
- **Session Memory** — Tracks last 10 interactions per session with full entity/intent history

### 🛡️ Three-Tier Fallback & Human Handover
| Tier | Trigger | Response |
|------|---------|----------|
| **Tier 1** | 1st unclear query | 🤔 Clarification message + 3 clickable quick-reply suggestions |
| **Tier 2** | Off-topic query (weather, movies, etc.) | 🚫 Polite out-of-scope redirect + topic suggestions |
| **Tier 3** | 2+ consecutive failures | 📞 Human advisor card with email, phone, office hours |

- **30+ out-of-scope patterns** detected (weather, sports, movies, jokes, politics, crypto, etc.)
- **Auto-reset**: Counter resets when user gets a successful response

### 🎨 Modern Web UI
- Glassmorphic chat interface with smooth animations
- **🌙 Dark/Light theme toggle** with CSS variable system
- **🎙️ Voice input** via Web Speech API (microphone button)
- **👍/👎 Feedback buttons** on every bot response (logged for analytics)
- Color-coded method badges (green/yellow/red by confidence)
- Entity detection badges (🔍 Courses: CS | Semesters: 3)
- Quick-reply suggestion buttons with hover effects
- 8 quick-access topic chips in the suggestion bar
- Time-aware welcome greeting (Good Morning/Afternoon/Evening)
- Typing indicator and responsive design

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+

### Installation

```bash
# Clone the repository
git clone https://github.com/dhanish0711/FAQ-Chatbot.git
cd FAQ-Chatbot

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Open http://localhost:5000 in your browser.

---

## 📁 Project Structure

```
FAQ-Chatbot/
├── app.py                 # Main Flask application
│   ├── process_message()  — Channel-agnostic core engine
│   ├── /get_response      — Web channel (HTML)
│   ├── /api/v1/chat       — Mobile channel (plain-text JSON)
│   ├── /whatsapp/webhook  — WhatsApp channel (numbered replies)
│   ├── TF-IDF Retriever, Entity Extractor, Intent Classifier
│   ├── Context Manager, Three-Tier Fallback, Human Handover
│   ├── Feedback endpoint (/feedback)
│   └── Debug routes (/debug, /classify_intent, /context)
├── multichannel_cli.py    # CLI simulator for all 3 channels
├── templates/
│   └── index.html         # Web interface (glassmorphic UI)
├── requirements.txt       # Dependencies (Flask)
├── .gitignore             # Python/Flask gitignore
├── LICENSE                # MIT License
└── README.md
```

---

## 🔧 API Endpoints

### 1. Chat — `POST /get_response`

```json
// Request
{ "message": "What are the MECH placements?" }

// Response
{
  "response": "🔍 [Detected: Courses: MECH] ... MECH PLACEMENTS ...",
  "method": "tfidf",
  "confidence": 0.95,
  "tag": "placement",
  "intent": "placements",
  "intent_confidence": 1.1,
  "entities": { "courses": ["MECH"], "semesters": [] },
  "entity_context": "Courses: MECH"
}
```

### 2. Fallback Response (with suggestions)

```json
// Request
{ "message": "asdfgh" }

// Response
{
  "response": "🤔 I didn't quite understand that...",
  "method": "fallback",
  "confidence": 0.0,
  "suggestions": ["Tell me about admissions", "What are the fees?", "Tell me about placements"]
}
```

### 3. Mobile Chat — `POST /api/v1/chat`
Plain-text response for mobile apps (no HTML):
```json
{ "message": "What are the fees?", "session_id": "user-123" }
// → { "channel": "mobile", "text": "💰 [FEES STRUCTURE]\n...", "intent": "fees", ... }
```

### 4. WhatsApp Webhook — `POST /whatsapp/webhook`
WhatsApp-formatted with numbered quick-replies:
```json
{ "message": "asdfgh", "from": "+919999999999" }
// → { "channel": "whatsapp", "body": "...\nReply 1: Tell me about admissions\n...", "quick_replies": [...] }
```

### 5. Debug — `POST /debug`
Returns TF-IDF scores for all FAQs against the query.

### 6. Intent Classification — `POST /classify_intent`
Returns intent scores for a given query.

### 7. Context — `GET /context`
Returns the current conversation context for the session.

### 8. Analytics Dashboard — `GET /analytics`
Returns interaction stats: success rate, fallback rate, intent/channel distribution, queries needing review.

### 9. Improvement Proposals — `GET /analytics/improvements`
Auto-proposes: new FAQs, keyword gaps, scope expansion, FAQ gap analysis with per-intent coverage.

### 10. Raw Logs — `GET /analytics/logs?limit=50&label=fallback`
Returns paginated interaction logs, filterable by label.

### 11. Clear Logs — `POST /analytics/clear`
Resets all interaction logs (for testing).

### 12. Feedback — `POST /feedback`
Submit thumbs up/down feedback for a bot response:
```json
{ "query": "What are the fees?", "vote": "up" }
// → { "status": "ok", "vote": "up" }
```

---

## 📊 Analytics & Continuous Improvement

Every interaction is automatically logged to `chat_logs.json` with auto-labeling:

| Label | Trigger |
|-------|---------|
| `successful` | Confidence ≥ 0.3 |
| `low-confidence` | Confidence < 0.3 |
| `fallback` | No FAQ match (1st time) |
| `out-of-scope` | Off-topic query |
| `handover` | 2+ consecutive failures |
| `greeting` / `farewell` | Hi/Bye messages |

### Dashboard (`GET /analytics`)
```json
{
  "total_interactions": 9,
  "success_rate": "55.6%",
  "fallback_rate": "33.3%",
  "channel_distribution": { "web": 7, "mobile": 1, "whatsapp": 1 },
  "queries_needing_review": [...]
}
```

### Auto-Improvement Proposals (`GET /analytics/improvements`)
| Type | Priority | Trigger |
|------|----------|---------|
| `NEW_FAQ` | HIGH | 3+ fallback queries with same intent |
| `KEYWORD_GAP` | MEDIUM | Low-confidence intent match |
| `SCOPE_EXPANSION` | LOW | Repeated out-of-scope topics |
| `FAQ_GAP` | HIGH | 2+ human handover escalations |

---

## 🧪 Example Conversations

### Basic Query
```
User: "What are the fees?"
Bot:  💰 [FEES STRUCTURE 2026-27] B.Tech: ₹1.5L/yr, M.Tech: ₹90K/yr, Ph.D: ₹60K/yr ...
      [Confidence: 98.3%] [TFIDF]  [👍 Helpful] [👎 Not helpful]
```

### Entity-Boosted Query
```
User: "Tell me about MECH placements"
Bot:  🔍 [Detected: Courses: MECH]
      💼 [MECH PLACEMENTS] Avg: ₹6.5 LPA, Highest: ₹18 LPA ...
      [Confidence: 95.0%] [TFIDF]
```

### Multi-Turn Follow-Up
```
User: "When is the exam?"         → ENTRANCE EXAMS (JEE/KCET)
User: "for semester 3?"           → SEM 3 EXAMS (Nov 10-20)  ← context follow-up
User: "and placements?"           → PLACEMENTS 2025-26        ← topic switch
User: "for ECE?"                  → ECE PLACEMENTS            ← entity switch
```

### Out-of-Scope & Handover
```
User: "What's the weather?"       → 🚫 Out of Scope + suggestion buttons
User: "asdfgh"                    → 🤔 Clarification + quick-reply buttons
User: "xyz123"  (2nd failure)     → 📞 Human Advisor card (email, phone, office)
User: "What are the fees?"        → 💰 Normal response (counter resets)
```

---

## 🏗️ Architecture

### Preprocessing Pipeline
```
Input → Lowercase → Remove Punctuation → Tokenize
     → Spelling Correction → Stopword Removal → Synonym Normalization
     → Processed Tokens
```

### Response Generation Flow (6 Priorities)
```
1. ✋ Greetings / Farewells        (exact match)
2. 🔗 Conversation Context         (follow-up detection + entity merging)
3. 📏 Rule-Based Patterns          (edge case matching)
4. 🔍 Entity-Boosted TF-IDF       (two-phase retrieval)
5. 🛡️ Three-Tier Fallback          (clarification → out-of-scope → handover)
```

### Entity-Boosted Retrieval (Two-Phase)
```
Phase 1: TF-IDF cosine similarity scores all FAQs
Phase 2: Boost FAQs matching detected entities (+0.3/entity)
       + Boost FAQs matching sub-intent tag (+0.15)
       → Best match selected
```

---

## 🌐 Multichannel Deployment

The chatbot uses a **channel-agnostic engine** (`process_message()`) with per-channel adapters:

```
                    ┌─────────────────┐
                    │  process_message │  ← Core Engine (channel-agnostic)
                    │  (NLP Pipeline)  │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  /get_response│  │ /api/v1/chat │  │  /whatsapp/  │
    │   (Web)       │  │  (Mobile)    │  │   webhook    │
    └──────────────┘  └──────────────┘  └──────────────┘
    HTML + badges      Plain-text JSON    Numbered replies
```

### Channel Comparison

| Feature | Web | Mobile | WhatsApp |
|---------|-----|--------|----------|
| Response format | HTML with `<b>`, `<br>` | Plain text (no HTML) | Plain text + emoji |
| Suggestions | Clickable chip buttons | JSON array | `Reply 1: ...` numbered |
| Handover card | Styled `<div>` with links | Plain text emails/phones | Plain text contact info |
| Session | Flask cookie | `session_id` in body | `from` phone number |
| Endpoint | `POST /get_response` | `POST /api/v1/chat` | `POST /whatsapp/webhook` |

### CLI Simulator

```bash
# Interactive mode — pick a channel
python multichannel_cli.py

# Auto-run demo on all 3 channels
python multichannel_cli.py --demo

# Interactive on specific channel
python multichannel_cli.py --channel whatsapp
```

## 🎯 Intent Classification

| Intent | Weight | Sample Keywords |
|--------|--------|-----------------|
| **Admissions** | 1.2 | admission, apply, register, eligibility |
| **Exams** | 1.0 | exam, jee, gate, cutoff, marks |
| **Fees** | 1.3 | fee, tuition, cost, scholarship |
| **Placements** | 1.1 | placement, job, salary, package |
| **Facilities** | 0.9 | hostel, transport, library, sports |
| **Academics** | 1.0 | course, program, faculty, branch |
| **General** | 0.8 | time, contact, address, location |

---

## 🎨 Customization

### Adding New FAQs
```python
FAQ_DATA.append({
    "question": "keywords for matching",
    "answer": "HTML formatted answer",
    "tag": "category"
})
```

### Adding New Intents
```python
INTENT_DEFINITIONS["new_intent"] = {
    "keywords": ["keyword1", "keyword2"],
    "examples": ["example question"],
    "weight": 1.0
}
```

### Adding Synonyms
```python
NORMALIZATION_MAP["synonym"] = "canonical_form"
```

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| FAQs | 45+ topics |
| Synonyms | 110+ mappings |
| Spelling Corrections | 50+ common errors |
| Intents | 7 categories |
| Out-of-Scope Patterns | 30+ |
| Response Time | < 100ms |
| Context Memory | Last 10 turns/session |
| Dark Mode | ✅ CSS variable system |
| Voice Input | ✅ Web Speech API |
| Feedback System | ✅ 👍/👎 per response |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Dhanish Ladwani** — [GitHub](https://github.com/dhanish0711)

---

**⭐ Star this repository if you found it helpful!**
