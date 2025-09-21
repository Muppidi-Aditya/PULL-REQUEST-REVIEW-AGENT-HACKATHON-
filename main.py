import hmac
import hashlib
import logging
from typing import Dict, List
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
import jwt
import time
import requests
from functools import lru_cache
import google.generativeai as genai

# ------------------------------
# CONFIGURATION
# ------------------------------
APP_ID = "1987429"
PRIVATE_KEY_PATH = "pr-review-agent-hackathon.2025-09-20.private-key.pem"
WEBHOOK_SECRET = None  # Optional: set for webhook signature verification

# Gemini AI Configuration
GEMINI_API_KEY = "AIzaSyCKMvVngUAnpsjEZp35Vh6hmKsq3z45UxM"  # Replace with your API key
GEMINI_MODEL = "gemini-1.5-flash"  # Flash model

# Configure Gemini AI
if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)
    print("🤖 Gemini AI configured successfully")
else:
    print("⚠️ Gemini API key not configured - using fallback AI logic")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

print("🚀 Starting GitHub PR Review Agent...")
logger.info("Application starting up")

app = FastAPI(title="PR Review Agent", version="1.0.0")

# ------------------------------
# HELPER FUNCTIONS
# ------------------------------

@lru_cache(maxsize=1)
def load_private_key() -> str:
    try:
        with open(PRIVATE_KEY_PATH, "r") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to load private key: {e}")
        raise HTTPException(status_code=500, detail="Failed to load private key")

def verify_webhook_signature(payload_body: bytes, signature: str) -> bool:
    if not WEBHOOK_SECRET:
        return True
    if not signature:
        return False
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_signature}", signature)

def generate_jwt() -> str:
    private_key = load_private_key()
    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": APP_ID
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

def get_installation_token(installation_id: int) -> str:
    jwt_token = generate_jwt()
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.post(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()["token"]

def fetch_pr_files(owner: str, repo: str, pull_number: int, token: str) -> List[Dict]:
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()

def analyze_code_with_gemini(file_data: Dict) -> Dict:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return {"analysis": "Gemini AI not configured", "suggestions": []}
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        filename = file_data["filename"]
        status = file_data["status"]
        additions = file_data.get("additions", 0)
        deletions = file_data.get("deletions", 0)
        patch = file_data.get("patch", "")

        prompt = f"""
You are an expert code reviewer. Analyze this file change:

File: {filename}
Status: {status}
Changes: +{additions}/-{deletions}


Output structured as:
1) User Description
2) PR Type
3) Description
4) Changes Walkthrough (table format)
5) PR Review (estimated effort, recommended)
6) PR Code Suggestions (table with impact)
"""
        response = model.generate_content(prompt)
        return {"analysis": response.text, "suggestions": [], "confidence": "high"}
    except Exception as e:
        logger.error(f"Gemini AI analysis failed: {e}")
        return {"analysis": f"AI analysis unavailable: {str(e)}", "suggestions": [], "confidence": "low"}

def generate_overall_pr_summary_with_gemini(pr_files: List[Dict], pr_info: Dict) -> str:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "Gemini AI not configured for overall analysis"
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        files_summary = []
        for f in pr_files[:10]:
            files_summary.append(f"- {f['filename']} ({f['status']}): +{f.get('additions', 0)}/-{f.get('deletions', 0)} lines")
        files_text = "\n".join(files_summary)

        prompt = f"""
You are a senior software architect reviewing a Pull Request.

PR Overview:
- Total files changed: {len(pr_files)}
- File summary:
{files_text}

Provide structured review with sections:
1) User Description
2) PR Type
3) Description
4) Changes Walkthrough (table format)
5) PR Review (estimated effort, recommended)
6) PR Code Suggestions (table with impact)
"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini PR summary failed: {e}")
        return f"Overall AI analysis unavailable: {str(e)}"

def generate_ai_review(pr_files: List[Dict]) -> str:
    if not pr_files:
        return "No files to review."
    review_comments = ["# 🤖 AI Code Review\n"]
    for i, file_data in enumerate(pr_files[:5]):
        filename = file_data["filename"]
        review_comments.append(f"## 📁 `{filename}`")
        gemini_analysis = analyze_code_with_gemini(file_data)
        review_comments.append(gemini_analysis["analysis"])
        review_comments.append("---")
    pr_info = {"total_files": len(pr_files)}
    overall_analysis = generate_overall_pr_summary_with_gemini(pr_files, pr_info)
    review_comments.append("## 🎯 Overall PR Assessment")
    review_comments.append(overall_analysis)
    return "\n\n".join(review_comments)

def post_pr_comment(owner: str, repo: str, pull_number: int, token: str, comment: str) -> Dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pull_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {"body": comment}
    response = requests.post(url, headers=headers, json=data, timeout=30)
    response.raise_for_status()
    return response.json()

# ------------------------------
# BOT FUNCTIONALITY
# ------------------------------

def generate_bot_response(user_query: str) -> str:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "Gemini AI not configured."
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = f"""
You are an expert software engineer and assistant. Answer the user query concisely:

User query: {user_query}
"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini bot response failed: {e}")
        return f"AI temporarily unavailable: {str(e)}"

def handle_bot_comment(owner: str, repo: str, comment_id: int, comment_body: str, token: str):
    query = comment_body.lstrip("$bot").strip()
    reply_text = "🤖 Please provide a query after `$bot`." if not query else generate_bot_response(query)
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{comment_id}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {"body": reply_text}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        logger.info(f"Posted bot response to comment {comment_id}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to post bot response: {e}")

# ------------------------------
# WEBHOOK ENDPOINT
# ------------------------------

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")
    action = payload.get("action")
    owner = payload["repository"]["owner"]["login"]
    repo = payload["repository"]["name"]
    installation_id = payload["installation"]["id"]
    token = get_installation_token(installation_id)

    # Handle Pull Request
    if event == "pull_request" and action in ["opened", "synchronize"]:
        pr_number = payload["number"]
        pr_files = fetch_pr_files(owner, repo, pr_number, token)
        ai_comment = generate_ai_review(pr_files)
        post_pr_comment(owner, repo, pr_number, token, ai_comment)
        return JSONResponse({"status": "success", "message": "PR reviewed"})

    # Handle Bot Queries
    if event == "issue_comment" and action == "created":
        comment_body = payload["comment"]["body"]
        comment_id = payload["issue"]["number"]
        if comment_body.startswith("$bot"):
            handle_bot_comment(owner, repo, comment_id, comment_body, token)
            return JSONResponse({"status": "success", "message": "Bot responded"})

    return JSONResponse({"status": "ignored", "reason": "Event/action not handled"})

# ------------------------------
# HEALTH & ROOT
# ------------------------------

@app.get("/health")
async def health_check():
    try:
        load_private_key()
        private_key_status = "✅ Available"
    except:
        private_key_status = "❌ Not found"
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "app_id": APP_ID,
        "private_key": private_key_status,
        "webhook_verification": "Enabled" if WEBHOOK_SECRET else "Disabled"
    }

@app.get("/")
async def root():
    return {
        "name": "GitHub PR Review Agent",
        "version": "1.0.0",
        "description": "Automated PR review bot + $bot query responder",
        "endpoints": {
            "webhook": "/webhook (POST)",
            "health": "/health (GET)",
            "root": "/ (GET)"
        }
    }

