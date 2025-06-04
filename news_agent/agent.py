import logging
import os
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from dotenv import load_dotenv
from google.adk.agents import Agent
from newsapi import NewsApiClient
from newspaper import Article, ArticleException


from .prompt import PROMPT

logging.basicConfig(level=logging.INFO)

load_dotenv()
news_api_key = os.getenv("NEWS_API_KEY")



class News(BaseModel):
    title: str = Field(description="The title of the news article.")
    url: str = Field(description="The URL of the news article.")
    description: Optional[str] = Field(description="A brief description of the news article.")
    source_name: str = Field(description="The name of the source of the news article.")

class NewsDetails(BaseModel):
    url: str = Field(description="The URL of the news article.")
    text: Optional[str] = Field(description="The first 5000 char of the news article.")


def get_news(query: str, past_days: int = 7, domains: Optional[str] = None, max_results:int = 30) -> List[News]:
    """
    Get news on the given parameters like query, past_days and domains.
    Args:
        query: search news about this topic
        past_days: For how many days in the past should we search?
        domains: search news in these resources
        max_results: Maximum number of news to look for
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
                                                  page_size=max_results
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
                          ][:max_results]
    return simplified_articles


def get_full_articles(urls: List[str]) -> List[NewsDetails]:
    """
    Fetches and extracts the main text content of a list of news articles from a given URLs, for later analysis.

    Args:
        urls (List[str]): A list of URLs representing the news articles to fetch and parse.

    Returns:
        List[NewsDetails]: The extracted main text content of the article. Returns an empty string if fetching, parsing, or extraction fails.
    """
    news_details_list = []
    for url in urls:
        try:
            logging.info(f"Attempting to fetch article from URL: {url}")
            article = Article(url)

            # Download the article HTML
            article.download()
            if article.download_state != 2:
                raise ArticleException(
                    f"Failed to download article. State: {article.download_state}, Exception: {article.download_exception_msg}")

            article.parse()

            content = article.text
            if not content:
                logging.warning(f"Could not extract main text content from URL: {url}")
                news_details_list.append(NewsDetails(url=url, text=""))

            logging.info(f"Successfully extracted article content from URL: {url} (Length: {len(content)})")
            short_content = content[:5000] + ("..." if len(content) > 5000 else "")
            news_details_list.append(NewsDetails(url=url, text=short_content))

        except ArticleException as e:
            logging.error(f"Newspaper ArticleException for URL {url}: {e}")
            news_details_list.append(NewsDetails(url=url, text=""))
        except Exception as e:
            logging.error(f"Unexpected error fetching article from URL {url}: {e}")
            news_details_list.append(NewsDetails(url=url, text=""))
    return news_details_list


MODEL = "gemini-2.5-flash-preview-05-20"

# Corrected Agent definition
root_agent = Agent(
    model=MODEL,
    name="root_agent",
    description="Agent to provide news lists or summaries.",
    instruction=PROMPT,
    tools=[get_news, get_full_articles])
