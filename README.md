# GitHub Pull Request Review Agent

🎉 **Ready-to-Use GitHub App Available!** 🎉

A Python-based backend application that automatically reviews GitHub pull requests using AI (Gemini) and posts detailed, structured feedback on code quality, suggestions, and improvement areas.

> **✨ No Setup Required!** Install our pre-built GitHub App on your repository and start getting AI-powered PR reviews instantly!

## 📋 Table of Contents

- [🚀 Quick Start - Install GitHub App](#quick-start## 🚀 Project Overviewinstall-github-app)
- [Project Overview](#project-overview)
- [Features](#features)
- [Architecture](#architecture)
- [Backend Implementation](#backend-implementation)
- [GitHub App Setup (For Developers)](#github-app-setup-for-developers)
- [Deployment](#deployment)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
- [Future Improvements](#future-improvements)
- [License](#license)

## 🚀 Quick Start - Install GitHub App

**Ready to use immediately!** No configuration or setup required.

### 📦 Installation Steps:

1. **[Click here to install the GitHub App](https://github.com/apps/pr-review-agent)** *(Replace with your actual GitHub App URL)*
2. **Select repositories** where you want AI PR reviews
3. **Grant permissions** (Pull requests, Contents, Issues)
4. **Done!** 🎉 Open any PR and get instant AI reviews

### 🎯 What happens after installation:
- ✅ Automatic AI reviews on every new PR
- ✅ Detailed code suggestions and improvements
- ✅ Structured feedback with effort estimation
- ✅ Bot queries with `$bot` prefix

---

The Pull Request Review Agent automates code review on GitHub using AI. When a pull request is opened or updated, the agent:

1. **Analyzes** added and modified files
2. **Generates** structured feedback with sections:
   - User Description
   - PR Type
   - Description
   - Changes Walkthrough (table format, expandable code)
   - PR Review (effort, recommendation)
   - PR Code Suggestions (table format with impact)
3. **Posts** the review as a comment on the PR

This helps developers save time, improve code quality, and maintain consistency across repositories.

## ✨ Features

- **🤖 AI-Powered PR Review**: Uses Gemini API to generate detailed code feedback
- **📋 Structured Feedback**: Feedback sections include description, changes, review effort, and suggestions
- **🌐 Multi-Language Support**: Works with Python, JavaScript, and other common programming languages
- **⚡ Webhook-Based**: Triggered automatically on PR events like opened or updated
- **💬 Optional Bot Query**: Prefix `$bot` to ask direct questions to the AI

## 🏗️ Architecture

```
GitHub PR Event → Webhook Endpoint (FastAPI) → AI Analysis (Gemini) → Post Comment on GitHub
```

### Components:

- **FastAPI Backend**: Handles GitHub webhook events and communicates with Gemini API
- **PyJWT**: Generates JWT tokens for GitHub App authentication
- **Google Generative AI (Gemini)**: Performs AI-based code review
- **GitHub App**: Installed on the target repository to receive events and post reviews

## 🛠️ Backend Implementation

### Tech Stack

- **Python 3.13+**
- **FastAPI** for backend
- **Uvicorn** as ASGI server
- **PyJWT** for GitHub App authentication
- **Requests** for HTTP communication
- **Google Generative AI (Gemini)** for AI analysis
- **python-dotenv** for environment variable management

### Key Files

#### `main.py`
- Handles `/webhook` endpoint
- Processes PR events (opened, synchronize)
- Generates JWT and installation token
- Calls Gemini API for AI code review
- Posts structured comment on GitHub

#### `requirements.txt`
```txt
fastapi
uvicorn
requests
pyjwt
google-generativeai
python-dotenv
cryptography
```

#### `.env` (optional)
```env
GITHUB_APP_ID=<your_github_app_id>
GITHUB_PRIVATE_KEY_PATH=pr-review-agent.private-key.pem
GITHUB_APP_INSTALLATION_ID=<installation_id>
GEMINI_API_KEY=<your_gemini_api_key>
```

### Key Functionality

#### JWT Generation for GitHub App:
```python
def generate_jwt():
    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()
    payload = {"iat": int(time.time()), "exp": int(time.time()) + 600, "iss": APP_ID}
    return jwt.encode(payload, private_key, algorithm="RS256")
```

#### Webhook Handling:
```python
@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    if payload["action"] in ["opened", "synchronize"]:
        # Fetch PR files, analyze via Gemini, post review
        pass
```

#### AI Code Review Prompt:
The prompt instructs Gemini to provide feedback in the following format:
- User Description
- PR Type
- Description
- Changes Walkthrough (table with expandable code)
- PR Review (effort, recommendation)
- PR Code Suggestions (table with impact)

#### Bot Query Support:
```python
if user_message.startswith("$bot"):
    response = generate_gemini_response(user_message[4:])
```

## ⚙️ GitHub App Setup (For Developers)

> **📝 Note:** This section is for developers who want to create their own instance. **Most users should use the [ready-to-install GitHub App](#quick-start---install-github-app) above!**

### Creating Your Own GitHub App:

1. Go to **GitHub Developer Settings** > **GitHub Apps** > **New GitHub App**

2. **Configure**:
   - **Webhook URL**: `https://<your-backend-url>/webhook`
   - **Webhook secret**: Optional (for security)

3. **Permissions**:
   - **Pull requests**: Read & write
   - **Contents**: Read
   - **Issues**: Read & write (for posting review comments)

4. **Install** the app on your repository

5. **Download** the Private Key `.pem` file

## 🚀 Deployment

### Using Render (example):

1. Go to [Render](https://render.com) and create a **Web Service**
2. Connect your GitHub repository
3. Set **Start Command**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```
4. Add environment variables in Render if required
5. **Deploy** → Render assigns a URL like `https://pull-request-review-agent-hackathon.onrender.com`

## 📡 API Endpoints

| Endpoint   | Method | Description                      |
|------------|--------|----------------------------------|
| `/webhook` | POST   | Receives GitHub webhook events   |
| `/health`  | GET    | Health check endpoint            |
| `/`        | GET    | Default root endpoint (optional) |

## 📖 Usage

### 🎯 For End Users:

1. **[Install the GitHub App](#quick-start---install-github-app)** on your repository
2. **Open a pull request** - that's it! 🚀

### 🤖 Automatic Features:

The AI will automatically comment on every PR with:
- **📊 Structured review** with clear sections
- **💡 Code suggestions** with impact analysis  
- **⏱️ Estimated effort** and recommendation
- **📝 Changes walkthrough** in table format

### 🗨️ Interactive Bot Queries:

Ask specific questions by prefixing with `$bot`:

```
$bot How can I optimize the function calculate_average in code.py?
$bot What are the potential security issues in this code?
$bot Suggest better variable names for this function
```

### 📈 Review Structure:

Every PR gets a comprehensive review including:
- **User Description**: Summary of the changes
- **PR Type**: Feature, bugfix, refactor, etc.
- **Changes Walkthrough**: Detailed table with expandable code
- **PR Review**: Effort estimation and recommendation
- **Code Suggestions**: Actionable improvements with impact ratings

## 🔮 Future Improvements

- [ ] Add support for multiple languages and frameworks
- [ ] Cache previous reviews to avoid repetitive analysis
- [ ] Add a web dashboard for PR analytics
- [ ] Integrate with Slack/Teams notifications

## 📄 License

MIT License – see [LICENSE](LICENSE)

---

## 🌟 **Live GitHub App Available!**

**[📦 Install PR Review Agent GitHub App](https://github.com/apps/pr-review-agent)** *(Replace with your actual app URL)*

**Backend URL**: https://pull-request-review-agent-hackathon.onrender.com

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you have any questions or issues, please open an issue on GitHub.
