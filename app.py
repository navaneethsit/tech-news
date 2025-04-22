import feedparser
import streamlit as st
import requests
import re

#API_URL = "https://api-inference.huggingface.co/models/google/pegasus-xsum"
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

def clean_content(text):
    # Remove repeating patterns or boilerplate
    text = re.sub(r'\b(\w+\s*)\1{2,}', r'\1', text)  # Removes repeated phrases
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = text.replace('\n', ' ').strip()
    return text

# 📝 Summarize article using Hugging Face
def format_as_news_headline(title, summary):
    return f"📢 *Headline:* **{title}**\n\n🗞️ *News Summary:* {summary}\n\n🧭 For full details, visit the original article."

def summarize_article(content):
    content = clean_content(content)
    try:
        headers = {
            "Authorization": "Bearer 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"
        }

        # Request summary
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
            raw_summary = response.json()[0]["summary_text"]

            # Reformat and clean the output
            raw_summary = raw_summary.strip().replace("\n", " ")

            # Handle sentences and combine fragments intelligently
            lines = raw_summary.split(". ")
            clean_lines = [f"- {line.strip().rstrip('.')}" for line in lines if line.strip()]
            news_style = "\n".join(clean_lines[:5])  # limit to 5 bullet points

            # Combine fragments if possible
            full_summary = ' '.join(news_style.split('\n'))

            # Format for a better news-style output
            return f"📢 *Headline:* **{articles[idx]['title']}**\n\n🗞️ *News Summary:* {full_summary}\n\n🧭 For full details, visit the original article."
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
