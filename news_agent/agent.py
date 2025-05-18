import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from dotenv import load_dotenv
from google.adk.agents import Agent
from newsapi import NewsApiClient
from newspaper import Article, ArticleException

from .prompt import PROMPT

logging.basicConfig(level=logging.INFO)

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

load_dotenv()
news_api_key = os.getenv("NEWS_API_KEY")


@dataclass
class News:
    title: str
    url: str
    description: str
    source_name: str


def get_news(query: str, past_days: int = 7, domains: Optional[str] = None) -> List[News]:
    """
    Get news on the given parameters like query, past_days and domains.
    Args:
        query: search news about this topic
        past_days: For how many days in the past should we search?
        domains: search news in these resources
    Returns:
        news_details: news articles formated as a dictionary with title, url, description, source_name if nothing found returns empty list
    """
    today = datetime.today()
    from_date = today - timedelta(days=past_days)
    news_api_client = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
    news_details = news_api_client.get_everything(q=query,
                                                  from_param=from_date,
                                                  domains=domains,
                                                  sort_by='relevancy',
                                                  page_size=20
                                                  )
    articles_found = news_details.get('articles', [])
    simplified_articles = [
                              News(
                                  title=article.get("title"),
                                  url=article.get("url"),
                                  description=article.get("description"),
                                  source_name=article.get("source", {}).get("name"),
                              )
                              for article in articles_found
                              if article.get("title") and article.get("url")
                          ][:50]
    return simplified_articles


def get_full_articles(urls: List[str]) -> Dict[str, str]:
    """
    Fetches and extracts the main text content of a list of news articles from a given URLs, for later analysis.

    Args:
        urls (List[str]): A list of URLs representing the news articles to fetch and parse.

    Returns:
        Dict[str, str]: The extracted main text content of the article. Returns an empty string if fetching, parsing, or extraction fails.
    """
    return_dict = {}
    for url in urls:
        try:
            logging.info(f"Attempting to fetch article from URL: {url}")
            article = Article(url)

            # Download the article HTML
            article.download()
            if article.download_state != 2:  # 2 means success
                raise ArticleException(
                    f"Failed to download article. State: {article.download_state}, Exception: {article.download_exception_msg}")

            # Parse the article to extract content
            article.parse()

            # Extract the main text
            content = article.text
            if not content:
                logging.warning(f"Could not extract main text content from URL: {url}")
                return_dict[url] = ""

            logging.info(f"Successfully extracted article content from URL: {url} (Length: {len(content)})")
            # Return only the first 5000 characters to avoid overly long responses for the LLM
            return_dict[url] = content[:10000] + ("..." if len(content) > 10000 else "")

        except ArticleException as e:
            logging.error(f"Newspaper ArticleException for URL {url}: {e}")
            return_dict[url] = ""
        except Exception as e:
            logging.error(f"Unexpected error fetching article from URL {url}: {e}")
            return_dict[url] = ""
    return return_dict


# Corrected Agent definition
root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    description="Agent to answer questions about news.",
    instruction=PROMPT,
    tools=[get_news, get_full_articles])
