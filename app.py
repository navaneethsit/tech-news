import feedparser
import streamlit as st
import requests

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"


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

# 📝 Summarize article using Hugging Face
def summarize_article(content):
    try:
        headers = {
    "Authorization": "Bearer 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"  # Replace with your actual Hugging Face API key
}

        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": content,
                "parameters": {
                    "max_length": 500,  # Max length of summary (more detailed)
                    "min_length": 100,  # Min length of summary (longer summaries)
                    "do_sample": False   # Set to False to get deterministic results (no randomness)
                }
            }
        )

        if response.status_code == 200:
            summary = response.json()[0]["summary_text"]
            # Ensure the summary has more lines and is more detailed
            if len(summary.split('\n')) < 5:
                # Try to get more details if summary is too short
                response = requests.post(
                    API_URL,
                    headers=headers,
                    json={
                        "inputs": content,
                        "parameters": {
                            "max_length": 800,  # Allow even more content if needed
                            "min_length": 200,  # Ensure summary is long enough
                            "do_sample": False
                        }
                    }
                )
                if response.status_code == 200:
                    summary = response.json()[0]["summary_text"]
            
            return summary
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
        summary = summarize_article(articles[idx]["content"])
    if summary:
        st.subheader("📝 Summary")
        st.write(summary)
        st.markdown(f"[🔗 Read full article]({articles[idx]['link']})")
    else:
        st.warning("Failed to generate a summary. Please try again.")
