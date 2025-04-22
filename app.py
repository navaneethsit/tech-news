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
st.markdown("# 📰 **Daily Tech & AI News Summarizer**")
st.markdown("Stay updated with the latest news and get summaries on the go! Select an article to get a concise summary.")

# Pagination Variables
if 'page' not in st.session_state:
    st.session_state.page = 0

# Collect news articles
articles = collect_news()
titles = [article["title"] for article in articles]

# Pagination for 10-15 articles per page
start = st.session_state.page * 10
end = start + 10

# Show only the headlines of the current page
current_page_titles = titles[start:end]
for i, title in enumerate(current_page_titles):
    if st.button(f"🔍 {title}", key=f"title-{start + i}"):
        # When user clicks on an article
        idx = start + i
        with st.spinner("Summarizing..."):
            summary = summarize_article(articles[idx]["content"])
        if summary:
            st.markdown(f"### **{articles[idx]['title']}**")
            st.markdown(f"**Link**: [Read Full Article]({articles[idx]['link']})")
            st.markdown("### **Summary**")
            st.write(summary)
        else:
            st.error(f"Failed to summarize: {articles[idx]['title']}")

# Navigation Buttons (Next/Previous)
col1, col2 = st.columns([1, 1])
with col1:
    if st.session_state.page > 0:
        if st.button("◀️ Previous"):
            st.session_state.page -= 1
            st.experimental_rerun()

with col2:
    if end < len(articles):
        if st.button("Next ▶️"):
            st.session_state.page += 1
            st.experimental_rerun()

# Footer section
st.markdown("---")