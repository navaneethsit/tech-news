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
            json={"inputs": content}
        )
        if response.status_code == 200:
            return response.json()[0]["summary_text"]
        else:
            st.error(f"Error during API request: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API request failed: {e}")
        return None

# 🌐 Streamlit UI
st.markdown("# 📰 **Daily Tech News Summarizer**")
st.markdown("Stay updated with the latest news and get summaries on the go! Select an article to get a concise summary.")

# Layout with columns
col1, col2 = st.columns([3, 2])  # Adjust the width ratio as needed

with col1:
    articles = collect_news()
    titles = [article["title"] for article in articles]
    for i, article in enumerate(articles):
        if st.button(f"Summarize: {article['title']}"):
            with st.spinner("Summarizing..."):
                summary = summarize_article(article["content"])
            if summary:
                st.subheader(f"📝 Summary of {article['title']}")
                st.write(summary)
                st.markdown(f"[🔗 Read full article]({article['link']})")
            else:
                st.error(f"Failed to summarize: {article['title']}")

with col2:
    st.markdown("**Article Previews**")
    for article in articles:
        st.markdown(f"**{article['title']}**")
        st.write(article["content"][:300] + "...")
        st.write("[Read More](" + article['link'] + ")")
        st.markdown("---")

# Footer section
st.markdown("---")
