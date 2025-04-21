import feedparser
import requests
import streamlit as st

# 📡 RSS Feeds
rss_feeds = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://www.technologyreview.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.wired.com/feed/rss",
]

# 🔍 News Collector
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

# ✨ Summarizer using OpenRouter
def summarize_article(title, content):
    prompt = f"Summarize this tech or AI news article into 3 sentences:\n\nTitle: {title}\nContent: {content}\n\nSummary:"

    headers = {
        "Authorization": f"Bearer {st.secrets['openai']['api_key']}",
        "HTTP-Referer": "https://your-app-name.streamlit.app",  # 🔁 Replace with your actual deployed Streamlit app URL
        "X-Title": "Tech News Summarizer"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        st.error(f"API Error: {response.status_code} - {response.text}")
        return "Error: Could not summarize the article."

# 🖥️ Streamlit UI
st.title("📰 Tech & AI News Summarizer")

articles = collect_news()
titles = [article['title'] for article in articles]

choice = st.selectbox("Choose an article to summarize", titles)

if st.button("Summarize"):
    idx = titles.index(choice)
    summary = summarize_article(articles[idx]['title'], articles[idx]['content'])

    st.subheader("📝 Summary")
    st.write(summary)
    st.markdown(f"[🔗 Read full article]({articles[idx]['link']})")
 