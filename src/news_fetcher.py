import os
import json
from datetime import datetime, timedelta
import feedparser
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NewsFetcher:
    def __init__(self):
        # Trusted AI news sources (RSS)
        self.rss_feeds = [
            "https://techcrunch.com/category/artificial-intelligence/feed/",
            "https://blog.google/technology/ai/rss/",
            "https://www.artificialintelligence-news.com/feed/",
            "https://devblogs.microsoft.com/python/feed/" # Substitute for MS AI news
        ]
        
    def fetch_news(self):
        logging.info("Starting news collection...")
        all_news = []
        twenty_four_hours_ago = datetime.utcnow() - timedelta(days=1)
        
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    # Simple date parsing
                    try:
                        published = datetime(*entry.published_parsed[:6])
                    except (AttributeError, TypeError):
                        published = datetime.utcnow()
                        
                    if published > twenty_four_hours_ago:
                        all_news.append({
                            "title": entry.title,
                            "link": entry.link,
                            "summary": BeautifulSoup(entry.get("summary", ""), "html.parser").get_text(),
                            "published": published.isoformat(),
                            "source": feed_url
                        })
            except Exception as e:
                logging.error(f"Error fetching from {feed_url}: {e}")
                
        logging.info(f"Collected {len(all_news)} raw news items in the last 24h.")
        return self._rank_and_select(all_news)

    def _rank_and_select(self, news_items):
        if not news_items:
            return None
            
        # Basic heuristic ranking: virality, tech giants
        keywords = ["OpenAI", "Anthropic", "GPT-5", "Claude", "Nvidia", "AGI", "Google", "Gemini", "Sam Altman", "Meta", "Llama"]
        
        for item in news_items:
            score = 0
            text = f"{item['title']} {item['summary']}".lower()
            for kw in keywords:
                if kw.lower() in text:
                    score += 10
            # Boost longer summaries slightly as they might have more substance
            score += len(item['summary']) / 100 
            item['score'] = score
            
        # Sort by score descending
        ranked_news = sorted(news_items, key=lambda x: x.get('score', 0), reverse=True)
        
        # Deduplicate based on title similarity (simple approach)
        unique_news = []
        seen_titles = set()
        for item in ranked_news:
            title_words = frozenset(item['title'].lower().split())
            if title_words not in seen_titles:
                seen_titles.add(title_words)
                unique_news.append(item)
                
        logging.info(f"Selected top story: {unique_news[0]['title']}")
        return unique_news[:3] # Return top 3 for the script writer to analyze
        
if __name__ == "__main__":
    fetcher = NewsFetcher()
    top_news = fetcher.fetch_news()
    print(json.dumps(top_news, indent=2))
