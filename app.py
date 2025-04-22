import feedparser
import streamlit as st
import requests
import re

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

# 🔗 RSS feeds
rss_feeds = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://www.technologyreview.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.wired.com/feed/rss",
]

# 📥 Collect news
@st.cache_data
def collect_news():
    articles = []
    for feed_url in rss_feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:3]:
            title = entry.title
            content = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
            link = entry.link
            if content:
                articles.append({"title": title, "content": content, "link": link})
    return articles

def clean_content(text):
    text = re.sub(r'\b(\w+\s*)\1{2,}', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('\n', ' ').strip()
    return text

def is_relevant(line):
    line = line.lower()
    return not any(x in line for x in [
        "follow us", "visit", "facebook", "instagram", "twitter", "linkedin", "cnn.com", "sign up", "subscribe"
    ])

def summarize_article(content, title, link):
    content = clean_content(content)
    try:
        headers = {
            "Authorization": "Bearer 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"
        }

        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": content,
                "parameters": {
                    "max_length": 500,
                    "min_length": 150,
                    "do_sample": False
                }
            }
        )

        if response.status_code == 200:
            raw_summary = response.json()[0]["summary_text"]
            raw_summary = raw_summary.strip().replace("\n", " ")
            lines = raw_summary.split(". ")

            # Deduplicate and filter
            seen = set()
            clean_lines = []
            for line in lines:
                line = line.strip().rstrip(".")
                if len(line) > 20 and is_relevant(line) and line not in seen:
                    seen.add(line)
                    clean_lines.append(f"- {line}")

            news_style = "\n".join(clean_lines[:5])  # Keep top 5 lines
            return f"📢 *Headline:* **{title}**\n\n🗞️ *News Summary:*\n{news_style}\n\n🧭 For full details, visit the original article: [Read More]({link})"
        else:
            st.error(f"Error during API request: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API request failed: {e}")
        return None

# 🌐 Streamlit UI
st.title("📰 Daily Tech News")

articles = collect_news()
titles = [article["title"] for article in articles]

choice = st.selectbox("Choose an article to summarize", titles)

if st.button("Summarize"):
    idx = titles.index(choice)
    with st.spinner("Summarizing the article..."):
        summary = summarize_article(
            articles[idx]["content"],
            articles[idx]["title"],
            articles[idx]["link"]
        )

    if summary:
        st.subheader("📝 Summary")
        st.markdown(summary)
    else:
        st.warning("Failed to generate a summary. Please try again.")
