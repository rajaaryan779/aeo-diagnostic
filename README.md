# AEO Diagnostic Tool

> **Find out how GPT-4o, Claude, and Gemini rank your product in AI-powered search — before your competitors do.**

Answer Engine Optimization (AEO) is the new SEO. As people shift from Google to AI assistants for product discovery, your visibility in AI responses directly impacts sales. This tool gives you an instant report card.

---

## What It Does

Enter your product name and a customer search query. The tool simultaneously queries **3 major AI models** and returns a scored report:

- Whether each AI mentions your product by name
- Your ranking position (#1–5) in each model's recommendations
- An overall visibility score (0–100)
- Actionable steps to improve your AI presence

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| AI Models | DeepSeek R1, Claude 3 Haiku, Gemini 2.5 Flash |
| API Gateway | OpenRouter + Google AI Studio |
| Frontend | Vanilla HTML / CSS / JS |
| Deployment | Vercel |

---

## Quick Start

**1. Clone**
```bash
git clone https://github.com/rajaaryan779/aeo-diagnostic
cd aeo-diagnostic
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add API keys**
```bash
cp .env.example .env
# Open .env and fill in your keys
```

**4. Run locally**
```bash
uvicorn main:app --reload
```

**5. Open** → http://localhost:8000

---

## API Keys Required

| Variable | Where to get it | Cost |
|---|---|---|
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai) | Free tier available |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/app/apikey) | Free |

---

## Scoring System

Each model returns a ranked list of top 5 products. Your score per model:

| Rank | Score |
|---|---|
| #1 | 100 |
| #2 | 80 |
| #3 | 60 |
| #4 | 40 |
| #5 | 20 |
| Not mentioned | 0 |

Overall score = average across all 3 models → mapped to grade **A–F**.

---

## Why AEO Matters

Traditional SEO targets Google's 10 blue links. But in 2025, millions of buying decisions are made through AI chat. When someone asks *"what's the best running shoe under ₹5000?"* — if your product isn't in the AI's answer, you don't exist to that buyer. AEO fixes that.

---

## Built By

**Aarya Vaidya**  
[Portfolio](https://aarya-portfolio-kohl.vercel.app) · [GitHub](https://github.com/rajaaryan779)
