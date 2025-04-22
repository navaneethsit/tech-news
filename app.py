import feedparser
import streamlit as st
import requests
import re
from datetime import datetime

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

# 🔗 Focused RSS feeds (AI, software, dev news)
rss_feeds = [
    "https://venturebeat.com/category/ai/feed/",
    "https://www.technologyreview.com/feed/",
    "https://pub.towardsai.net/feed",
    "https://huggingface.co/blog/rss.xml",
    "https://thenewstack.io/feed/",
    "https://dev.to/feed/tag/ai",
    "https://github.blog/feed/",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
]

# 📥 News Collector with keyword filtering
@st.cache_data
def collect_news():
    articles = []
    keywords = [
        "AI", "Artificial Intelligence", "LLM", "OpenAI", "GPT", "Generative",
        "Machine Learning", "ML", "Transformer", "NVIDIA", "Neural", "Copilot",
        "Python", "GitHub", "Open Source", "Developer", "Framework"
    ]

    for feed_url in rss_feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            title = entry.title
            content = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
            link = entry.link
            if any(kw.lower() in title.lower() or kw.lower() in content.lower() for kw in keywords):
                articles.append({"title": title, "content": content, "link": link})
    return articles

def clean_content(text):
    text = re.sub(r'\b(\w+\s*)\1{2,}', r'\1', text)  # Removes repeated phrases
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = text.replace('\n', ' ').strip()
    return text

# 📝 Summarize article using Hugging Face
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
            raw_summary = response.json()[0]["summary_text"].strip().replace("\n", " ")
            lines = raw_summary.split(". ")
            bullets = [f"- {line.strip().rstrip('.')}" for line in lines if line.strip()]
            summary_bullets = "\n".join(bullets[:5])

            return f"""
📢 *Headline:* **{title}**

🗞️ *News Summary:*
{summary_bullets}

🧭 [Read full article]({link})
"""
        else:
            st.error(f"Error during API request: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API request failed: {e}")
        return None

# 🌐 Streamlit UI
st.title("📰 Daily Tech News")
st.markdown(f"🕒 Last updated: **{datetime.now().strftime('%b %d, %Y %I:%M %p')}**")

articles = collect_news()

if not articles:
    st.warning("No relevant tech/AI articles found. Try again later.")
else:
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
