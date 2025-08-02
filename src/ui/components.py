import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional, Any
import base64
from datetime import datetime
import numpy as np

class MusicPlayerComponent:
    """Premium music player component with modern UI"""
    
    @staticmethod
    def render_player(track_info: Dict, is_playing: bool = False) -> Dict:
        """Render the main music player interface"""
        if not track_info:
            st.info("🎵 No track selected. Search for music to get started!")
            return {}
        
        # Player container with custom styling
        with st.container():
            st.markdown("""
            <style>
            .player-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 20px;
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            .track-title {
                color: white;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .track-artist {
                color: rgba(255,255,255,0.8);
                font-size: 18px;
                margin-bottom: 15px;
            }
            .player-controls {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
                margin: 20px 0;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Track info display
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                # Album art placeholder or actual image
                album_image = track_info.get('album_image')
                if album_image:
                    st.image(album_image, width=150)
                else:
                    st.markdown("""
                    <div style="
                        width: 150px; 
                        height: 150px; 
                        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                        border-radius: 10px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-size: 24px;
                    ">🎵</div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="player-container">
                    <div class="track-title">{track_info.get('name', 'Unknown Track')}</div>
                    <div class="track-artist">{track_info.get('artist', 'Unknown Artist')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Player controls
                control_cols = st.columns([1, 1, 1, 1, 1])
                
                with control_cols[0]:
                    if st.button("⏮️", key="prev_track"):
                        return {'action': 'previous'}
                
                with control_cols[1]:
                    if st.button("⏯️" if not is_playing else "⏸️", key="play_pause"):
                        return {'action': 'toggle_play', 'is_playing': not is_playing}
                
                with control_cols[2]:
                    if st.button("⏭️", key="next_track"):
                        return {'action': 'next'}
                
                with control_cols[3]:
                    if st.button("🔀", key="shuffle"):
                        return {'action': 'shuffle'}
                
                with control_cols[4]:
                    if st.button("❤️", key="like_track"):
                        return {'action': 'like', 'track_id': track_info.get('id')}
            
            with col3:
                # Track details
                st.markdown("**Track Details**")
                st.write(f"Album: {track_info.get('album', 'Unknown')}")
                st.write(f"Duration: {MusicPlayerComponent._format_duration(track_info.get('duration_ms', 0))}")
                st.write(f"Popularity: {track_info.get('popularity', 0)}/100")
                
                # Audio features visualization
                if 'audio_features' in track_info:
                    MusicPlayerComponent._render_audio_features(track_info['audio_features'])
        
        return {}
    
    @staticmethod
    def _format_duration(duration_ms: int) -> str:
        """Format duration from milliseconds to MM:SS"""
        if duration_ms == 0:
            return "0:00"
        
        minutes = duration_ms // 60000
        seconds = (duration_ms % 60000) // 1000
        return f"{minutes}:{seconds:02d}"
    
    @staticmethod
    def _render_audio_features(audio_features: Dict):
        """Render audio features as a mini radar chart"""
        features = ['danceability', 'energy', 'valence', 'acousticness']
        values = [audio_features.get(feature, 0) for feature in features]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=features,
            fill='toself',
            name='Audio Features',
            line_color='rgb(102, 126, 234)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=False,
            height=200,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)

class SearchComponent:
    """Advanced search component with filters"""
    
    @staticmethod
    def render_search_bar() -> Dict:
        """Render the main search interface"""
        st.markdown("### 🔍 Discover Music")
        
        # Search input
        search_query = st.text_input(
            "Search for tracks, artists, or albums",
            placeholder="Try 'indie rock', 'Billie Eilish', or 'chill vibes'...",
            key="main_search"
        )
        
        # Advanced filters in expander
        with st.expander("🎛️ Advanced Filters"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Genre filter
                genres = st.multiselect(
                    "Genres",
                    options=[
                        "pop", "rock", "hip-hop", "electronic", "indie", "jazz", 
                        "classical", "country", "r&b", "folk", "metal", "punk"
                    ],
                    key="genre_filter"
                )
                
                # Popularity range
                popularity_range = st.slider(
                    "Popularity Range",
                    min_value=0,
                    max_value=100,
                    value=(0, 100),
                    key="popularity_filter"
                )
                
                # Release year range
                current_year = datetime.now().year
                year_range = st.slider(
                    "Release Year Range",
                    min_value=1950,
                    max_value=current_year,
                    value=(2000, current_year),
                    key="year_filter"
                )
            
            with col2:
                # Audio feature filters
                st.markdown("**Audio Features**")
                
                energy_range = st.slider(
                    "Energy",
                    min_value=0.0,
                    max_value=1.0,
                    value=(0.0, 1.0),
                    step=0.1,
                    key="energy_filter"
                )
                
                danceability_range = st.slider(
                    "Danceability",
                    min_value=0.0,
                    max_value=1.0,
                    value=(0.0, 1.0),
                    step=0.1,
                    key="danceability_filter"
                )
                
                valence_range = st.slider(
                    "Positivity (Valence)",
                    min_value=0.0,
                    max_value=1.0,
                    value=(0.0, 1.0),
                    step=0.1,
                    key="valence_filter"
                )
        
        # Search button
        search_clicked = st.button("🎵 Search Music", type="primary", use_container_width=True)
        
        if search_clicked and search_query:
            return {
                'query': search_query,
                'genres': genres,
                'popularity_range': popularity_range,
                'year_range': year_range,
                'energy_range': energy_range,
                'danceability_range': danceability_range,
                'valence_range': valence_range
            }
        
        return {}

class RecommendationCard:
    """Individual recommendation card component"""
    
    @staticmethod
    def render_card(track: Dict, section_type: str = "general", show_reasoning: bool = True) -> Dict:
        """Render a single recommendation card"""
        with st.container():
            # Card styling based on section type
            card_styles = {
                "for_you": "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);",
                "niche": "background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);",
                "experimental": "background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);",
                "general": "background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);"
            }
            
            card_style = card_styles.get(section_type, card_styles["general"])
            
            st.markdown(f"""
            <div style="
                {card_style}
                border-radius: 15px;
                padding: 15px;
                margin: 10px 0;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            ">
                <h4 style="margin: 0 0 5px 0;">{track.get('name', 'Unknown Track')}</h4>
                <p style="margin: 0 0 10px 0; opacity: 0.9;">{track.get('artist', 'Unknown Artist')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            
            actions = {}
            
            with col1:
                if st.button("▶️", key=f"play_{track.get('id', '')}"):
                    actions['action'] = 'play'
                    actions['track'] = track
            
            with col2:
                if st.button("❤️", key=f"like_{track.get('id', '')}"):
                    actions['action'] = 'like'
                    actions['track'] = track
            
            with col3:
                if st.button("➕", key=f"add_{track.get('id', '')}"):
                    actions['action'] = 'add_to_playlist'
                    actions['track'] = track
            
            with col4:
                if st.button("ℹ️", key=f"info_{track.get('id', '')}"):
                    actions['action'] = 'show_info'
                    actions['track'] = track
            
            # Show reasoning if enabled
            if show_reasoning and 'reasoning' in track:
                with st.expander("Why this recommendation?"):
                    st.write(track['reasoning'])
            
            # Show track details
            if 'audio_features' in track:
                with st.expander("Track Analysis"):
                    RecommendationCard._render_track_analysis(track)
            
            return actions
    
    @staticmethod
    def _render_track_analysis(track: Dict):
        """Render detailed track analysis"""
        features = track.get('audio_features', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Energy", f"{features.get('energy', 0):.2f}")
            st.metric("Danceability", f"{features.get('danceability', 0):.2f}")
            st.metric("Valence", f"{features.get('valence', 0):.2f}")
        
        with col2:
            st.metric("Acousticness", f"{features.get('acousticness', 0):.2f}")
            st.metric("Instrumentalness", f"{features.get('instrumentalness', 0):.2f}")
            st.metric("Popularity", f"{track.get('popularity', 0)}/100")

class AnalyticsComponent:
    """Analytics and visualization component"""
    
    @staticmethod
    def render_diversity_metrics(metrics: Dict):
        """Render diversity metrics dashboard"""
        st.markdown("### 📊 Recommendation Diversity Analysis")
        
        if not metrics:
            st.info("No diversity metrics available yet. Get some recommendations first!")
            return
        
        # Key metrics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            diversity_score = metrics.get('diversity', {}).get('intra_list_diversity', 0)
            st.metric(
                "Diversity Score",
                f"{diversity_score:.2f}",
                delta=f"{diversity_score - 0.5:.2f}" if diversity_score > 0 else None
            )
        
        with col2:
            novelty_score = metrics.get('novelty', {}).get('combined_novelty', 0)
            st.metric(
                "Novelty Score",
                f"{novelty_score:.2f}",
                delta=f"{novelty_score - 0.5:.2f}" if novelty_score > 0 else None
            )
        
        with col3:
            unique_artists = metrics.get('diversity', {}).get('artist_diversity', {}).get('unique_artists', 0)
            st.metric("Unique Artists", unique_artists)
        
        with col4:
            niche_ratio = metrics.get('diversity', {}).get('popularity_diversity', {}).get('niche_ratio', 0)
            st.metric(
                "Niche Music %",
                f"{niche_ratio * 100:.1f}%",
                delta=f"{(niche_ratio - 0.3) * 100:.1f}%" if niche_ratio > 0 else None
            )
        
        # Detailed charts
        AnalyticsComponent._render_diversity_charts(metrics)
    
    @staticmethod
    def _render_diversity_charts(metrics: Dict):
        """Render detailed diversity charts"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Genre distribution
            genre_data = metrics.get('diversity', {}).get('genre_diversity', {}).get('genre_distribution', {})
            if genre_data:
                fig = px.pie(
                    values=list(genre_data.values()),
                    names=list(genre_data.keys()),
                    title="Genre Distribution"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Popularity distribution
            popularity_data = metrics.get('coverage', {}).get('popularity_tier_coverage', {})
            if popularity_data:
                fig = px.bar(
                    x=list(popularity_data.keys()),
                    y=list(popularity_data.values()),
                    title="Popularity Tier Distribution",
                    labels={'x': 'Popularity Tier', 'y': 'Proportion'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_user_profile(profile: Dict):
        """Render user profile analytics"""
        st.markdown("### 👤 Your Music Profile")
        
        if not profile:
            st.info("Your music profile will appear here as you interact with recommendations.")
            return
        
        # Profile summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Favorite Genres", len(profile.get('preferred_genres', {})))
        
        with col2:
            avg_popularity = profile.get('avg_popularity', 0)
            st.metric("Avg. Track Popularity", f"{avg_popularity:.0f}/100")
        
        with col3:
            exploration_score = profile.get('exploration_score', 0)
            st.metric("Exploration Score", f"{exploration_score:.2f}")
        
        # Detailed profile charts
        AnalyticsComponent._render_profile_charts(profile)
    
    @staticmethod
    def _render_profile_charts(profile: Dict):
        """Render detailed profile charts"""
        # Genre preferences
        preferred_genres = profile.get('preferred_genres', {})
        if preferred_genres:
            fig = px.bar(
                x=list(preferred_genres.keys()),
                y=list(preferred_genres.values()),
                title="Your Genre Preferences",
                labels={'x': 'Genre', 'y': 'Preference Score'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Audio feature preferences
        audio_preferences = profile.get('audio_feature_preferences', {})
        if audio_preferences:
            features = list(audio_preferences.keys())
            values = list(audio_preferences.values())
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=features,
                fill='toself',
                name='Your Preferences'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                showlegend=False,
                title="Your Audio Feature Preferences",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)

class ContextSelector:
    """Context selection component for mood and activity"""
    
    @staticmethod
    def render_context_selector() -> Dict:
        """Render context selection interface"""
        st.markdown("### 🎭 Set Your Context")
        
        col1, col2 = st.columns(2)
        
        with col1:
            mood = st.selectbox(
                "Current Mood",
                options=[
                    "Happy 😊", "Sad 😢", "Energetic ⚡", "Calm 😌", 
                    "Focused 🎯", "Romantic 💕", "Nostalgic 🌅", "Adventurous 🚀"
                ],
                key="mood_selector"
            )
        
        with col2:
            activity = st.selectbox(
                "Current Activity",
                options=[
                    "Working 💼", "Studying 📚", "Exercising 🏃", "Relaxing 🛋️",
                    "Commuting 🚗", "Cooking 👨‍🍳", "Partying 🎉", "Sleeping 😴"
                ],
                key="activity_selector"
            )
        
        # Time of day (auto-detected but can be overridden)
        current_hour = datetime.now().hour
        if 6 <= current_hour < 12:
            default_time = "Morning 🌅"
        elif 12 <= current_hour < 17:
            default_time = "Afternoon ☀️"
        elif 17 <= current_hour < 21:
            default_time = "Evening 🌆"
        else:
            default_time = "Night 🌙"
        
        time_of_day = st.selectbox(
            "Time of Day",
            options=["Morning 🌅", "Afternoon ☀️", "Evening 🌆", "Night 🌙"],
            index=["Morning 🌅", "Afternoon ☀️", "Evening 🌆", "Night 🌙"].index(default_time),
            key="time_selector"
        )
        
        return {
            'mood': mood.split(' ')[0].lower(),
            'activity': activity.split(' ')[0].lower(),
            'time_of_day': time_of_day.split(' ')[0].lower()
        }

class FeedbackComponent:
    """Interactive feedback component"""
    
    @staticmethod
    def render_rating_interface(track_id: str) -> Dict:
        """Render track rating interface"""
        st.markdown("### ⭐ Rate This Track")
        
        # Star rating
        rating = st.slider(
            "How much do you like this track?",
            min_value=1,
            max_value=5,
            value=3,
            key=f"rating_{track_id}"
        )
        
        # Detailed feedback
        col1, col2 = st.columns(2)
        
        with col1:
            feedback_type = st.selectbox(
                "Feedback Type",
                options=["Love it! 💕", "Like it 👍", "It's okay 😐", "Not for me 👎", "Hate it 😠"],
                key=f"feedback_type_{track_id}"
            )
        
        with col2:
            discovery_value = st.selectbox(
                "Discovery Value",
                options=["New favorite! 🌟", "Interesting find 🔍", "Expected 📋", "Too similar 🔄"],
                key=f"discovery_{track_id}"
            )
        
        # Optional text feedback
        text_feedback = st.text_area(
            "Additional Comments (Optional)",
            placeholder="Tell us more about why you liked or disliked this track...",
            key=f"text_feedback_{track_id}"
        )
        
        # Submit feedback
        if st.button("Submit Feedback", key=f"submit_feedback_{track_id}"):
            return {
                'track_id': track_id,
                'rating': rating,
                'feedback_type': feedback_type,
                'discovery_value': discovery_value,
                'text_feedback': text_feedback,
                'timestamp': datetime.now().isoformat()
            }
        
        return {}

class PlaylistComponent:
    """Playlist management component"""
    
    @staticmethod
    def render_playlist_manager(playlists: List[Dict]) -> Dict:
        """Render playlist management interface"""
        st.markdown("### 🎵 Your Playlists")
        
        # Create new playlist
        with st.expander("➕ Create New Playlist"):
            playlist_name = st.text_input("Playlist Name", key="new_playlist_name")
            playlist_description = st.text_area("Description (Optional)", key="new_playlist_desc")
            
            if st.button("Create Playlist", key="create_playlist"):
                if playlist_name:
                    return {
                        'action': 'create',
                        'name': playlist_name,
                        'description': playlist_description
                    }
        
        # Display existing playlists
        if playlists:
            for playlist in playlists:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{playlist.get('name', 'Untitled')}**")
                        st.caption(f"{len(playlist.get('tracks', []))} tracks")
                    
                    with col2:
                        if st.button("▶️", key=f"play_playlist_{playlist.get('id')}"):
                            return {
                                'action': 'play_playlist',
                                'playlist_id': playlist.get('id')
                            }
                    
                    with col3:
                        if st.button("📝", key=f"edit_playlist_{playlist.get('id')}"):
                            return {
                                'action': 'edit_playlist',
                                'playlist_id': playlist.get('id')
                            }
        else:
            st.info("No playlists yet. Create your first playlist above!")
        
        return {}