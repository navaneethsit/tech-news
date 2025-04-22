import feedparser
import streamlit as st
import requests

# Fetch API Key securely from Streamlit secrets (ensure you add this in secrets.toml)
api_key = st.secrets["api_key"]  # Update the key name to match your secret's name
url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

# 🔗 Supported RSS feeds
rss_feeds = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://www.technologyreview.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.wired.com/feed/rss",
]

# 📥 News Collector
@st.cache_data
def collect_news():
    articles = []
    for feed_url in rss_feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:3]:  # Collecting only the top 3 articles
            title = entry.title
            content = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
            link = entry.link
            if content:
                articles.append({"title": title, "content": content, "link": link})
    return articles

# 📝 Function to summarize articles using Hugging Face API
def summarize_article(content):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": content
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()[0]['summary_text']
        else:
            st.error(f"Error during API request: {response.status_code}")
            return "Failed to summarize the article."
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return "Failed to summarize the article."

# 🌐 Streamlit UI
st.title("📰 Tech & AI News Summarizer")

# Collect articles from RSS feeds
articles = collect_news()
titles = [article["title"] for article in articles]

# Dropdown to select an article
choice = st.selectbox("Choose an article to summarize", titles)

# Summarize article upon button click
if st.button("Summarize"):
    idx = titles.index(choice)

    with st.spinner("Summarizing the article..."):
        summary = summarize_article(articles[idx]["content"])

    # Display summary or warning if failed
    if summary:
        st.subheader("📝 Summary")
        st.write(summary)
        st.markdown(f"[🔗 Read full article]({articles[idx]['link']})")
    else:
        st.warning("Failed to generate a summary. Please try again.")
