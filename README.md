# Google ADK News Assistant POC

This repository serves as a Proof of Concept (POC) to demonstrate how to build conversational agents using the Google
Agent Development Kit (ADK). The example agent is a news discovery assistant that can fetch, process, and discuss news
articles based on user interaction.

## Overview

This POC illustrates key Google ADK concepts:

- Defining an agent with an LLM (e.g., Gemini).
- Crafting an instructional prompt for agent behavior.
- Creating and integrating custom Python tools for external interactions.
- Managing API keys and configurations.

The news assistant can understand user news interests, fetch articles via NewsAPI, extract full content using
Newspaper3k, and discuss them, always providing source URLs.

## Features

- Conversational news discovery.
- Targeted news search (keywords, domains, recency).
- Full article retrieval for summarization/discussion.
- Source attribution for all news.
- Customizable agent persona via a detailed prompt.

## Setup and Installation

1. **Clone the Repository:**

```shell
bash git clone https://github.com/patricio-navarro/agents_poc cd agents_poc 
```

2. **Create and Activate a Virtual Environment (Recommended):**

```shell
bash python -m venv venv # On macOS/Linux source venv/bin/activate # On Windows # venv\Scripts\activate
```

3. **Install Dependencies:**

Ensure `pip` is up-to-date, then install requirements:

```shell
bash pip install --upgrade pip pip install -r requirements.txt
```

4. **Set Up Environment Variables:**

Create a `.env` file in the news_agent directory with your API keys:

    -   `NEWS_API_KEY`: From newsapi.org.
    -   `GOOGLE_API_KEY`: For Google's Generative AI services (e.g., Gemini) from Google AI Studio.
    -   `GOOGLE_GENAI_USE_VERTEXAI=FALSE`: Ensures direct use of Google AI Generative Language API.

## How to Run
To interact with the agent run:
```shell
adk web
```
## Deploy
Set environment variables
```
# Set your Google Cloud Project ID
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

# Set your desired Google Cloud Location
export GOOGLE_CLOUD_LOCATION="us-central1" 

# Set the path to your agent code directory
export AGENT_PATH="./news_agent" 

# Set a name for your Cloud Run service (optional)
export SERVICE_NAME="news-agent-service"

# Set an application name (optional)
export APP_NAME="news-agent-app"
```
Deploy container
```shell
adk deploy cloud_run
```

**Note**: Check that `.env` and `requirements.txt` files are store in the agent folder