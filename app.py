import feedparser
import streamlit as st
import requests

# 🗝️ API Config
# openai.api_key = st.secrets["OPENAI_API_KEY"]
# openai.api_base = "https://openrouter.ai/api/v1"

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

def summarize_article(title, content):
    prompt = f"Summarize this tech or AI news article into 3 concise sentences:\n\nTitle: {title}\nContent: {content}\n\nSummary:"

    headers = {
        "Authorization": f"Bearer {st.secrets['OPENAI_API_KEY']}",
        "HTTP-Referer": "https://tech-news-101-is.streamlit.app/",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        st.error(f"Error during API request: {e}")
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

    st.subheader("📝 Summary")
    st.write(summary)
    st.markdown(f"[🔗 Read full article]({articles[idx]['link']})")

