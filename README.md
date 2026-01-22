# FishCatch AI Agent

A complete AI-powered system for commercial fishermen to manage catches, check prices, and coordinate sales with buyers.

## Features

- **Mobile-Friendly Dashboard**: Easy to use on a phone while on the boat.
- **Catch Logging**: Quickly log fish type and weight.
- **AI Sales Coordinator**: Automatically generates personalized messages to buyers.
- **Universal Coach Guardrails**: Ensures all messages are accurate, safe, and professional.
- **Price Scraping**: Automatically checks cannery prices (Westport, WA).
- **Email-to-SMS**: Sends text messages to buyers without extra costs (using carrier gateways).
- **Buyer Management**: Import contacts from Excel.

## Setup Instructions

### 1. Prerequisites

- Docker and Docker Compose installed
- An Anthropic API Key (for Claude)
- A Gmail account (or other SMTP provider) for sending SMS
- A Neon (Postgres) Database URL

### 2. Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your details:
   - `ANTHROPIC_API_KEY`: Your Claude API key
   - `SMTP_USER`: Your Gmail address
   - `SMTP_PASSWORD`: Your Gmail App Password (not your login password)
   - `SECRET_KEY`: Generate a random string for security
   - `DATABASE_URL`: Your Neon connection string (e.g., `postgres://user:pass@ep-xyz.neon.tech/neondb?sslmode=require`)

### 3. Running the App

1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

2. Open your browser:
   - Frontend: http://localhost:3000
   - Backend API Docs: http://localhost:8000/docs

### 4. Initial Setup

1. Log in with the default password: `fisherman` (you can change this in `.env`)
2. Go to **Settings** and add a Cannery URL (e.g., for Westport).
3. Go to **Buyer Management** and upload your buyer list using the Excel template.
   - You can download the template from the Settings page.

## Deployment

### Backend (Render/Railway)
1. Push code to GitHub.
2. Create a new Web Service on Render/Railway.
3. Set Environment Variables:
   - `ANTHROPIC_API_KEY`
   - `SMTP_USER`
   - `SMTP_PASSWORD`
   - `SECRET_KEY`
   - `DATABASE_URL` (Neon Postgres URL)
4. Deploy.

### Frontend (Vercel)
1. Import GitHub repo to Vercel.
2. Set Environment Variable:
   - `NEXT_PUBLIC_API_URL`: The URL of your deployed backend (e.g., `https://fishcatch-backend.onrender.com`)
3. Deploy.

## Usage Guide

### Daily Workflow

1. **Log Catch**: When you catch fish, open the app and click "Log Catch". Select the fish type and enter the weight.
2. **Contact Buyers**: Click "Contact Buyers". The AI will:
   - Check the current cannery price.
   - Find buyers who like that fish.
   - Write a draft message for each buyer.
3. **Review & Send**: Review the drafts. If they look good, click "Send".
   - The AI will NEVER send a message without your approval.
   - Messages go to buyers as SMS texts.
4. **Close the Deal**: Buyers will reply to your phone directly. When you sell, log it in "Catch History".

### Safety Guardrails

The system includes a "Universal Coach" that checks every action:
- **No Hallucinations**: It verifies that the price in the message matches the real cannery price.
- **No Math Errors**: It checks that pounds × price is calculated correctly.
- **Privacy**: It never shares your full buyer list with anyone.
- **Respect**: It warns you if you try to message the same buyer twice in one day.

## Tech Stack

- **Frontend**: Next.js 14, TailwindCSS, TypeScript
- **Backend**: Python FastAPI, SQLAlchemy
- **Database**: PostgreSQL (Neon) or SQLite (Local)
- **AI**: Anthropic Claude (claude-sonnet-4-5-20250929)
