import feedparser
import openai
import streamlit as st

# 🗝️ API Config
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

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

# ✨ Summarizer
def summarize_article(title, content):
    prompt = f"Summarize this tech or AI news article into 3 sentences:\n\nTitle: {title}\nContent: {content}\n\nSummary:"
    response = openai.ChatCompletion.create(
        model="mistralai/mistral-7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    return response['choices'][0]['message']['content'].strip()

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

 