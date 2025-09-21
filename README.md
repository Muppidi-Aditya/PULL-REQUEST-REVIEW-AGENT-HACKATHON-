# GitHub Pull Request Review Agent

![PR Review Agent](https://img.shields.io/badge/status-active-success)

A Python-based backend application that automatically reviews GitHub pull requests using AI (Gemini) and posts structured feedback, code suggestions, and improvement recommendations.

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Architecture](#architecture)  
4. [Backend Implementation](#backend-implementation)  
5. [GitHub App Setup](#github-app-setup)  
6. [Deployment](#deployment)  
7. [API Endpoints](#api-endpoints)  
8. [Usage](#usage)  
9. [Future Improvements](#future-improvements)  
10. [License](#license)  

---

## Project Overview

The Pull Request Review Agent is designed to **automate GitHub PR code reviews** using AI. It allows developers to get:

- **Detailed feedback** on their code changes  
- **Suggested improvements** and best practices  
- **Structured review** with effort estimates and recommendations  

The agent listens to GitHub PR events via a webhook, analyzes changed files using the Gemini AI API, and posts structured reviews as comments on the pull request.

---

## Features

- **Automated AI PR Review** – Uses Gemini API to provide feedback on code quality, readability, and performance.  
- **Structured Feedback** – Feedback is divided into sections:  
  1. User Description  
  2. PR Type  
  3. Description  
  4. Changes Walkthrough (table with expandable code)  
  5. PR Review (effort estimate, recommendation)  
  6. PR Code Suggestions (with impact rating)  
- **Bot Query Support** – Prefix `$bot` in a comment to get direct answers from AI.  
- **Webhook-Based Triggering** – Automatically analyzes PRs when they are opened or updated.  
- **Multi-Language Support** – Currently supports Python and can be extended for other languages.

---

## Architecture

```text
GitHub PR Event 
       |
       v
Webhook Endpoint (FastAPI) 
       |
       v
AI Analysis (Gemini API) 
       |
       v
Post Structured Review on GitHub PR
