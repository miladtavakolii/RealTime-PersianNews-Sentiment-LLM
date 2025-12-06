import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

from services.data_loader import SentimentDataLoader


st.set_page_config(
    page_title='News Sentiment Dashboard',
    layout='wide',
)

st.title('📰 News Sentiment Analysis Dashboard')

# Load Data
loader = SentimentDataLoader('data/sentiments')

@st.cache_data(ttl=5)
def load_data() -> pd.DataFrame:
    df = loader.load_all()

    # Normalize nested fields
    df['sentiment_label'] = df['sentiment'].apply(lambda x: x.get('sentiment'))
    df['sentiment_confidence'] = df['sentiment'].apply(lambda x: int(x.get('confidence', 0)))
    df['sentiment_reason'] = df['sentiment'].apply(lambda x: x.get('reason'))

    # Convert list → string for table display
    df['category_str'] = df['category'].apply(lambda c: ', '.join(c) if isinstance(c, list) else '')
    df['tags_str'] = df['tags'].apply(lambda t: ', '.join(t) if isinstance(t, list) else '')

    return df


df = load_data()

if df.empty:
    st.warning('No sentiment data found.')
    st.stop()

# Sidebar Time Filters
st.sidebar.header('⏱ Time Range')

time_filter = st.sidebar.radio(
    'Show news from:',
    ['All', 'Last 24 Hours', 'Last 48 Hours', 'Last 7 Days', 'Custom Range']
)

now = datetime.now()

if time_filter == 'Last 24 Hours':
    df = df[df['publication_date'] >= now - timedelta(hours=24)]

elif time_filter == 'Last 48 Hours':
    df = df[df['publication_date'] >= now - timedelta(hours=48)]

elif time_filter == 'Last 7 Days':
    df = df[df['publication_date'] >= now - timedelta(days=7)]

elif time_filter == 'Custom Range':
    date_range = st.sidebar.date_input('Select Range:', [])
    if len(date_range) == 2:
        start, end = date_range
        df = df[
            (df['publication_date'] >= datetime.combine(start, datetime.min.time())) &
            (df['publication_date'] <= datetime.combine(end, datetime.max.time()))
        ]

if df.empty:
    st.warning('No news found for this time range.')
    st.stop()

site_filter = st.sidebar.radio(
    'Show news from website:',
    ['All'] + list(df['site_name'].unique())
)

if site_filter != 'All':
    df = df[df['site_name'] == site_filter]

# Sentiment Distribution
st.subheader('📊 Sentiment Distribution')

sent_counts = df['sentiment_label'].value_counts()

fig1 = px.bar(
    sent_counts,
    title='Sentiment Distribution',
    labels={'index': 'Sentiment', 'value': 'Count'},
)
st.plotly_chart(fig1, width='stretch')

# Sentiment Count Trend (Frequency Over Time)
st.subheader('📈 Sentiment Frequency Trend Over Time')

# Ensure publication_date is datetime
df['publication_date'] = pd.to_datetime(df['publication_date'])


# User selects timeframe
time_options = {
    "15 Minute": "15min",
    "30 Minute": "30min",
    "1 Hour": "1h",
    "3 Hour": "3h",
    "5 Hour": "5h",
    "10 Hour": "10h",
    "1 Day": "1d",
}

selected_label = st.select_slider(
    "Time Range:",
    list(time_options.keys()),
)

# Convert selected label to Pandas resample rule
time_rule = time_options[selected_label]

# Group by day + sentiment and count number of news per sentiment per day
trend_df = (
    df.groupby([df['publication_date'].dt.floor(time_rule), 'sentiment_label'])
      .size()
      .reset_index(name='count')
)

# Convert date back to datetime for plotly
trend_df['publication_date'] = pd.to_datetime(trend_df['publication_date'])

fig2 = px.line(
    trend_df,
    x='publication_date',
    y='count',
    color='sentiment_label',
    markers=True,
    title='Sentiment Count Trend Over Time',
)

st.plotly_chart(fig2, width='stretch')

# Latest News Table
st.subheader('🆕 Latest News')

st.dataframe(
    df.sort_values('publication_date', ascending=False)[[
        'site_name',
        'publication_date',
        'title',
        'sentiment_label',
        'sentiment_confidence',
        'content',
        'category_str',
        'tags_str',
        'sentiment_reason',
        'url'
    ]].head(50),
    width='stretch',
)
