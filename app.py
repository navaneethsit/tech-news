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

# 🌐 Streamlit UI with Custom CSS for Page Coloring
st.markdown("""
    <style>
    .main {
        background-color: #f4f4f9;
        color: #333;
    }
    .header {
        color: #2e4a7d;
    }
    .summary {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .link {
        color: #1e90ff;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='header'>📰 **Daily Tech & AI News Summarizer**</h1>", unsafe_allow_html=True)
st.markdown("Stay updated with the latest news and get summaries on the go! Select an article to get a concise summary.")

# Collect news articles
articles = collect_news()
titles = [article["title"] for article in articles]

# Display all headlines if no article is selected
if 'selected_article' not in st.session_state:
    st.session_state.selected_article = None

# When no article is selected, show the list of articles
if st.session_state.selected_article is None:
    for i, title in enumerate(titles):
        if st.button(f"🔍 {title}", key=f"title-{i}"):
            # When user clicks on an article, display only that one
            st.session_state.selected_article = i
            st.experimental_rerun()

# If an article is selected, show only that article
if st.session_state.selected_article is not None:
    idx = st.session_state.selected_article
    selected_article = articles[idx]
    
    with st.spinner("Summarizing..."):
        summary = summarize_article(selected_article["content"])
    
    if summary:
        st.markdown(f"### **{selected_article['title']}**", unsafe_allow_html=True)
        st.markdown(f"**Link**: [Read Full Article]({selected_article['link']})", unsafe_allow_html=True)
        st.markdown("<div class='summary'>", unsafe_allow_html=True)
        st.write(summary)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(f"Failed to summarize: {selected_article['title']}")
    
    # Button to go back to the list of articles
    if st.button("Back to Articles"):
        st.session_state.selected_article = None
        st.experimental_rerun()