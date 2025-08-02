import sys
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from src.spotify.api_client import SpotifyClient
from src.ml.models import HybridRecommendationSystem
from src.ml.debiasing import DiversityInjector
from src.ui.components import MusicPlayerComponent, FeedbackComponent
from src.utils.config import Config
from src.utils.helpers import UIHelpers, DataProcessor

# Display Python version in sidebar for verification
st.sidebar.write(f"🐍 Python Version: {sys.version}")
if "3.11" in sys.version:
    st.sidebar.success("✅ Using Python 3.11")
else:
    st.sidebar.warning(f"⚠️ Using Python {sys.version.split()[0]}")

# Page configuration
st.set_page_config(
    page_title="Advanced Music Discovery",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1DB954, #1ed760);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #1DB954;
    margin: 0.5rem 0;
}
.recommendation-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
    border: 1px solid #e0e0e0;
}
.section-header {
    color: #1DB954;
    border-bottom: 2px solid #1DB954;
    padding-bottom: 0.5rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'spotify_client' not in st.session_state:
        st.session_state.spotify_client = None
    if 'recommendation_system' not in st.session_state:
        st.session_state.recommendation_system = None
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'liked_tracks': [],
            'disliked_tracks': [],
            'mood': 'neutral',
            'activity': 'general',
            'exploration_level': 0.3
        }
    if 'current_recommendations' not in st.session_state:
        st.session_state.current_recommendations = {
            'for_you': [],
            'new_niche': [],
            'experimental': []
        }

def render_header():
    """Render the main application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎵 Advanced Music Discovery</h1>
        <p>Breaking bias, exploring diversity, personalizing your musical journey</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with user controls"""
    st.sidebar.title("🎛️ Control Panel")
    
    # Spotify Authentication
    st.sidebar.subheader("🔐 Spotify Connection")
    if st.session_state.spotify_client is None:
        if st.sidebar.button("Connect to Spotify", type="primary"):
            try:
                config = Config()
                st.session_state.spotify_client = SpotifyClient(
                    config.SPOTIFY_CLIENT_ID,
                    config.SPOTIFY_CLIENT_SECRET
                )
                st.sidebar.success("Connected to Spotify!")
            except Exception as e:
                st.sidebar.error(f"Connection failed: {str(e)}")
    else:
        st.sidebar.success("✅ Connected to Spotify")
        if st.sidebar.button("Disconnect"):
            st.session_state.spotify_client = None
            st.rerun()
    
    # Context Selection
    st.sidebar.subheader("🎭 Current Context")
    mood = st.sidebar.selectbox(
        "Mood",
        ["happy", "sad", "energetic", "calm", "focused", "party", "romantic"],
        index=0
    )
    
    activity = st.sidebar.selectbox(
        "Activity",
        ["working", "exercising", "studying", "relaxing", "commuting", "socializing"],
        index=0
    )
    
    exploration_level = st.sidebar.slider(
        "Exploration Level",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Higher values = more experimental recommendations"
    )
    
    # Update preferences
    st.session_state.user_preferences.update({
        'mood': mood,
        'activity': activity,
        'exploration_level': exploration_level
    })
    
    # Analytics Toggle
    st.sidebar.subheader("📊 Analytics")
    show_analytics = st.sidebar.checkbox("Show Analytics Dashboard", value=True)
    
    return show_analytics

def render_music_player():
    """Render the music player interface"""
    st.subheader("🎵 Music Player")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input("Search for music", placeholder="Artist, song, or album...")
    
    with col2:
        if st.button("🔍 Search", type="primary"):
            if search_query and st.session_state.spotify_client:
                # Implement search functionality
                st.info("Search functionality will be implemented")
    
    with col3:
        if st.button("🎲 Surprise Me"):
            # Generate random recommendations
            st.info("Random recommendation feature")

def render_recommendations():
    """Render the three recommendation sections"""
    st.markdown('<h2 class="section-header">🎯 Your Recommendations</h2>', unsafe_allow_html=True)
    
    # Create tabs for different recommendation types
    tab1, tab2, tab3 = st.tabs(["🎵 For You", "🌟 New & Niche", "🚀 Experimental"])
    
    with tab1:
        render_recommendation_section("for_you", "Personalized picks based on your taste")
    
    with tab2:
        render_recommendation_section("new_niche", "Discover emerging and independent artists")
    
    with tab3:
        render_recommendation_section("experimental", "Bold picks to expand your horizons")

def render_recommendation_section(section_type, description):
    """Render a specific recommendation section"""
    st.write(description)
    
    # Generate sample recommendations for demo
    sample_tracks = [
        {"name": "Sample Track 1", "artist": "Artist A", "popularity": 45, "novelty": 0.8},
        {"name": "Sample Track 2", "artist": "Artist B", "popularity": 23, "novelty": 0.9},
        {"name": "Sample Track 3", "artist": "Artist C", "popularity": 67, "novelty": 0.6},
    ]
    
    for i, track in enumerate(sample_tracks):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                st.write(f"**{track['name']}** by {track['artist']}")
            
            with col2:
                st.write(f"Popularity: {track['popularity']}")
            
            with col3:
                if st.button("👍", key=f"{section_type}_like_{i}"):
                    st.session_state.user_preferences['liked_tracks'].append(track)
                    st.success("Added to liked!")
            
            with col4:
                if st.button("👎", key=f"{section_type}_dislike_{i}"):
                    st.session_state.user_preferences['disliked_tracks'].append(track)
                    st.info("Noted your preference")
            
            st.divider()

def render_analytics(show_analytics):
    """Render analytics dashboard"""
    if not show_analytics:
        return
    
    st.markdown('<h2 class="section-header">📊 Discovery Analytics</h2>', unsafe_allow_html=True)
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Diversity Score",
            value="78%",
            delta="+5%",
            help="Percentage of non-mainstream recommendations"
        )
    
    with col2:
        st.metric(
            label="New Artists",
            value="12",
            delta="+3",
            help="New artists discovered this week"
        )
    
    with col3:
        st.metric(
            label="Exploration Rate",
            value="34%",
            delta="+8%",
            help="Rate of exploring outside comfort zone"
        )
    
    with col4:
        st.metric(
            label="Satisfaction",
            value="4.2/5",
            delta="+0.3",
            help="Average rating of recommendations"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Diversity over time chart
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        diversity_scores = np.random.normal(0.75, 0.1, 30)
        
        fig = px.line(
            x=dates,
            y=diversity_scores,
            title="Diversity Score Over Time",
            labels={'x': 'Date', 'y': 'Diversity Score'}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Genre distribution
        genres = ['Pop', 'Rock', 'Electronic', 'Jazz', 'Classical', 'Hip-Hop', 'Indie']
        values = [20, 15, 25, 10, 8, 12, 10]
        
        fig = px.pie(
            values=values,
            names=genres,
            title="Genre Distribution"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function"""
    initialize_session_state()
    render_header()
    
    # Sidebar
    show_analytics = render_sidebar()
    
    # Main content
    render_music_player()
    render_recommendations()
    render_analytics(show_analytics)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🎵 Advanced Music Discovery - Breaking bias, exploring diversity</p>
        <p>Powered by Spotify Web API & Advanced ML</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()