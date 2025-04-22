import feedparser
import streamlit as st
import requests

# Fetch API Key securely from Streamlit secrets
api_key = st.secrets["api_key"]  # Ensure this is stored in your secrets.toml file
url = "https://api.deepai.org/api/summarization"

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
        for entry in feed.entries[:3]:
            title = entry.title
            content = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
            link = entry.link
            if content:
                articles.append({"title": title, "content": content, "link": link})
    return articles

# 📝 Function to summarize articles using DeepAI API
def summarize_article(title, content):
    try:
        response = requests.post(
            url,
            data={'text': content},
            headers={'api-key': api_key}
        )

        if response.status_code == 200:
            return response.json().get('output', 'No summary returned')
        else:
            st.error(f"Error during API request: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None

# 🌐 Streamlit UI
st.title("📰 Tech & AI News Summarizer")

articles = collect_news()
titles = [article["title"] for article in articles]

choice = st.selectbox("Choose an article to summarize", titles)

if st.button("Summarize"):
    idx = titles.index(choice)

    with st.spinner("Summarizing the article..."):
        summary = summarize_article(articles[idx]["title"], articles[idx]["content"])

    if summary:
        st.subheader("📝 Summary")
        st.write(summary)
        st.markdown(f"[🔗 Read full article]({articles[idx]['link']})")
    else:
        st.warning("Failed to generate a summary. Please try again.")
