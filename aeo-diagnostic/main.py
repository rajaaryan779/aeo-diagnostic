from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv
import re

load_dotenv(Path(__file__).parent / ".env")

app = FastAPI(title="AEO Diagnostic Tool")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)


class QueryRequest(BaseModel):
    product: str
    query: str


def query_openrouter(query: str, model: str, model_name: str):
    try:
        session = requests.Session()
        session.trust_env = False
        response = session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "AEO Diagnostic"
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful shopping assistant. Recommend top 5 products as a numbered list with product names clearly mentioned."
                    },
                    {
                        "role": "user",
                        "content": f"{query}. Give me the top 5 recommendations."
                    }
                ],
                "max_tokens": 500
            },
            timeout=30
        )
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"Error: {data.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        return f"Error querying {model_name}: {str(e)}"


def query_gemini(query: str):
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-flash-latest"
    ]
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                f"You are a helpful shopping assistant. {query}. Give me the top 5 product recommendations as a numbered list with product names clearly mentioned."
            )
            return response.text
        except Exception:
            continue
    return "Error: No Gemini model available"


def check_product_mention(response_text: str, product: str) -> dict:
    product_lower = product.lower()
    response_lower = response_text.lower()
    mentioned = product_lower in response_lower
    rank = None
    lines = response_text.split('\n')
    for i, line in enumerate(lines):
        if product_lower in line.lower():
            numbers = re.findall(r'^\d+', line.strip())
            if numbers:
                rank = int(numbers[0])
            else:
                rank = i + 1
            break
    return {
        "mentioned": mentioned,
        "rank": rank,
        "score": calculate_score(mentioned, rank)
    }


def calculate_score(mentioned: bool, rank) -> int:
    if not mentioned:
        return 0
    if rank == 1:
        return 100
    elif rank == 2:
        return 80
    elif rank == 3:
        return 60
    elif rank == 4:
        return 40
    elif rank == 5:
        return 20
    else:
        return 10


def get_grade(score: float) -> dict:
    if score >= 80:
        return {"grade": "A", "label": "Excellent", "color": "#22c55e", "emoji": "🏆"}
    elif score >= 60:
        return {"grade": "B", "label": "Good", "color": "#84cc16", "emoji": "✅"}
    elif score >= 40:
        return {"grade": "C", "label": "Average", "color": "#f59e0b", "emoji": "⚠️"}
    elif score >= 20:
        return {"grade": "D", "label": "Poor", "color": "#ef4444", "emoji": "❌"}
    else:
        return {"grade": "F", "label": "Not Found", "color": "#6b7280", "emoji": "💀"}


def generate_recommendations(results: dict, product: str) -> list:
    recommendations = []
    avg_score = sum(r["score"] for r in results.values()) / len(results)
    if avg_score < 40:
        recommendations.append("🔴 Your product has low AI visibility. Improve product descriptions with specific keywords.")
    if not results.get("llama", {}).get("mentioned"):
        recommendations.append("🔍 DeepSeek doesn't rank your product. Ensure strong online presence and detailed specs.")
    if not results.get("claude", {}).get("mentioned"):
        recommendations.append("🧠 Claude doesn't rank your product. Add more detailed use cases and specifications.")
    if not results.get("gemini", {}).get("mentioned"):
        recommendations.append("✨ Gemini doesn't rank your product. Improve Google presence and listing quality.")
    if avg_score >= 60:
        recommendations.append("✅ Good AI visibility. Keep maintaining strong product descriptions and reviews.")
    if avg_score >= 80:
        recommendations.append("🏆 Excellent! Your product is well recognized across all AI models.")
    if not recommendations:
        recommendations.append("📈 Improve online presence, reviews, and detailed descriptions to boost AI visibility.")
    return recommendations


@app.post("/analyze")
async def analyze_product(request: QueryRequest):
    if not request.product or not request.query:
        raise HTTPException(status_code=400, detail="Product and query are required")

    llama_response = query_openrouter(
        request.query,
        "deepseek/deepseek-r1-0528:free",
        "LLaMA"
    )

    claude_response = query_openrouter(
        request.query,
        "anthropic/claude-3-haiku",
        "Claude"
    )

    gemini_response = query_gemini(request.query)

    llama_result = check_product_mention(llama_response, request.product)
    claude_result = check_product_mention(claude_response, request.product)
    gemini_result = check_product_mention(gemini_response, request.product)

    overall_score = (llama_result["score"] + claude_result["score"] + gemini_result["score"]) / 3
    overall_grade = get_grade(overall_score)

    recommendations = generate_recommendations({
        "llama": llama_result,
        "claude": claude_result,
        "gemini": gemini_result
    }, request.product)

    return {
        "product": request.product,
        "query": request.query,
        "overall_score": round(overall_score),
        "overall_grade": overall_grade,
        "models": {
            "llama": {
                "name": "DeepSeek",
                "emoji": "🔍",
                "response": llama_response,
                "mentioned": llama_result["mentioned"],
                "rank": llama_result["rank"],
                "score": llama_result["score"],
                "grade": get_grade(llama_result["score"])
            },
            "claude": {
                "name": "Claude",
                "emoji": "🧠",
                "response": claude_response,
                "mentioned": claude_result["mentioned"],
                "rank": claude_result["rank"],
                "score": claude_result["score"],
                "grade": get_grade(claude_result["score"])
            },
            "gemini": {
                "name": "Gemini 2.5",
                "emoji": "✨",
                "response": gemini_response,
                "mentioned": gemini_result["mentioned"],
                "rank": gemini_result["rank"],
                "score": gemini_result["score"],
                "grade": get_grade(gemini_result["score"])
            }
        },
        "recommendations": recommendations
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()