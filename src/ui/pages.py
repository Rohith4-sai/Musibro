import streamlit as st
from typing import Dict, List, Optional, Any
from src.ui.components import (
    MusicPlayerComponent, SearchComponent, RecommendationCard,
    AnalyticsComponent, ContextSelector, FeedbackComponent, PlaylistComponent
)
from src.spotify.api_client import SpotifyClient
from src.ml.models import HybridRecommendationSystem
from src.ml.evaluation import RecommendationEvaluator
import pandas as pd
from datetime import datetime

class HomePage:
    """Main home page with personalized recommendations"""
    
    def __init__(self, spotify_client: SpotifyClient, recommendation_system: HybridRecommendationSystem):
        self.spotify_client = spotify_client
        self.recommendation_system = recommendation_system
        self.evaluator = RecommendationEvaluator()
    
    def render(self):
        """Render the home page"""
        st.title("🎵 Your Personal Music Discovery Hub")
        
        # Context selector
        context = ContextSelector.render_context_selector()
        if context:
            st.session_state['current_context'] = context
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs(["For You 💝", "New & Niche 🌟", "Experimental 🚀", "Search 🔍"])
        
        with tab1:
            self._render_for_you_section()
        
        with tab2:
            self._render_niche_section()
        
        with tab3:
            self._render_experimental_section()
        
        with tab4:
            self._render_search_section()
    
    def _render_for_you_section(self):
        """Render personalized recommendations"""
        st.markdown("### 💝 Curated Just For You")
        st.caption("Personalized recommendations that balance your taste with discovery")
        
        # Get user context
        context = st.session_state.get('current_context', {})
        user_profile = st.session_state.get('user_profile', {})
        
        # Generate recommendations
        if st.button("🎯 Get My Recommendations", key="get_for_you"):
            with st.spinner("Crafting your perfect playlist..."):
                try:
                    # Get user's top tracks for context
                    user_tracks = self.spotify_client.get_user_top_tracks(limit=20)
                    
                    if user_tracks:
                        # Generate hybrid recommendations
                        recommendations = self.recommendation_system.get_recommendations(
                            user_id=st.session_state.get('user_id', 'default'),
                            context=context,
                            num_recommendations=10,
                            diversity_weight=0.3
                        )
                        
                        if recommendations:
                            st.session_state['for_you_recommendations'] = recommendations
                            st.success(f"✨ Found {len(recommendations)} perfect tracks for you!")
                        else:
                            st.warning("No recommendations available. Try adjusting your context.")
                    else:
                        st.info("🎵 Connect your Spotify account to get personalized recommendations!")
                        
                except Exception as e:
                    st.error(f"Failed to get recommendations: {str(e)}")
        
        # Display recommendations
        recommendations = st.session_state.get('for_you_recommendations', [])
        if recommendations:
            self._display_recommendations(recommendations, "for_you")
    
    def _render_niche_section(self):
        """Render niche and emerging artist recommendations"""
        st.markdown("### 🌟 New & Niche Discoveries")
        st.caption("Emerging artists and hidden gems you won't find on mainstream playlists")
        
        # Niche discovery controls
        col1, col2 = st.columns(2)
        
        with col1:
            niche_level = st.slider(
                "Discovery Level",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Slightly off the beaten path, 5 = Deep underground",
                key="niche_level"
            )
        
        with col2:
            focus_area = st.selectbox(
                "Focus Area",
                options=["New Artists", "Independent Labels", "Emerging Genres", "Local Scenes"],
                key="niche_focus"
            )
        
        if st.button("🔍 Discover Hidden Gems", key="get_niche"):
            with st.spinner("Digging through the underground..."):
                try:
                    # Get niche recommendations based on low popularity
                    niche_recommendations = self.spotify_client.get_niche_recommendations(
                        max_popularity=30 - (niche_level * 5),
                        limit=10
                    )
                    
                    if niche_recommendations:
                        # Add reasoning for niche picks
                        for rec in niche_recommendations:
                            rec['reasoning'] = self._generate_niche_reasoning(rec, focus_area)
                        
                        st.session_state['niche_recommendations'] = niche_recommendations
                        st.success(f"🎯 Discovered {len(niche_recommendations)} hidden gems!")
                    else:
                        st.warning("No niche tracks found. Try adjusting the discovery level.")
                        
                except Exception as e:
                    st.error(f"Failed to discover niche music: {str(e)}")
        
        # Display niche recommendations
        niche_recommendations = st.session_state.get('niche_recommendations', [])
        if niche_recommendations:
            self._display_recommendations(niche_recommendations, "niche")
    
    def _render_experimental_section(self):
        """Render experimental recommendations that break user patterns"""
        st.markdown("### 🚀 Experimental Zone")
        st.caption("Bold recommendations that intentionally break from your usual patterns")
        
        # Experimental controls
        col1, col2 = st.columns(2)
        
        with col1:
            exploration_intensity = st.slider(
                "Exploration Intensity",
                min_value=0.1,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="How far outside your comfort zone to venture",
                key="exploration_intensity"
            )
        
        with col2:
            experiment_type = st.selectbox(
                "Experiment Type",
                options=["Genre Fusion", "Decade Jump", "Mood Opposite", "Cultural Bridge"],
                key="experiment_type"
            )
        
        if st.button("🧪 Start Musical Experiment", key="get_experimental"):
            with st.spinner("Conducting musical experiments..."):
                try:
                    user_profile = st.session_state.get('user_profile', {})
                    
                    # Generate experimental recommendations
                    experimental_recs = self._generate_experimental_recommendations(
                        user_profile, exploration_intensity, experiment_type
                    )
                    
                    if experimental_recs:
                        st.session_state['experimental_recommendations'] = experimental_recs
                        st.success(f"🔬 Generated {len(experimental_recs)} experimental tracks!")
                    else:
                        st.warning("No experimental tracks found. Try a different experiment type.")
                        
                except Exception as e:
                    st.error(f"Experiment failed: {str(e)}")
        
        # Display experimental recommendations
        experimental_recs = st.session_state.get('experimental_recommendations', [])
        if experimental_recs:
            self._display_recommendations(experimental_recs, "experimental")
    
    def _render_search_section(self):
        """Render search interface"""
        search_params = SearchComponent.render_search_bar()
        
        if search_params:
            with st.spinner("Searching for music..."):
                try:
                    # Perform search
                    search_results = self.spotify_client.search_tracks(
                        query=search_params['query'],
                        limit=20
                    )
                    
                    if search_results:
                        # Apply filters
                        filtered_results = self._apply_search_filters(search_results, search_params)
                        
                        st.session_state['search_results'] = filtered_results
                        st.success(f"Found {len(filtered_results)} tracks matching your criteria!")
                    else:
                        st.warning("No tracks found. Try a different search term.")
                        
                except Exception as e:
                    st.error(f"Search failed: {str(e)}")
        
        # Display search results
        search_results = st.session_state.get('search_results', [])
        if search_results:
            st.markdown("### 🎵 Search Results")
            self._display_recommendations(search_results, "general")
    
    def _display_recommendations(self, recommendations: List[Dict], section_type: str):
        """Display a list of recommendations"""
        for i, track in enumerate(recommendations):
            with st.container():
                action = RecommendationCard.render_card(track, section_type)
                
                if action:
                    self._handle_track_action(action, track, section_type)
                
                # Add separator
                if i < len(recommendations) - 1:
                    st.markdown("---")
    
    def _handle_track_action(self, action: Dict, track: Dict, section_type: str):
        """Handle user actions on tracks"""
        action_type = action.get('action')
        
        if action_type == 'play':
            st.session_state['current_track'] = track
            st.session_state['is_playing'] = True
            st.success(f"🎵 Now playing: {track.get('name', 'Unknown')}")
        
        elif action_type == 'like':
            # Add to liked tracks
            if 'liked_tracks' not in st.session_state:
                st.session_state['liked_tracks'] = []
            
            if track not in st.session_state['liked_tracks']:
                st.session_state['liked_tracks'].append(track)
                st.success(f"❤️ Added {track.get('name', 'Unknown')} to your liked tracks!")
            else:
                st.info("Track already in your liked tracks!")
        
        elif action_type == 'add_to_playlist':
            # Show playlist selection
            self._show_playlist_selector(track)
        
        elif action_type == 'show_info':
            # Show detailed track information
            self._show_track_details(track)
    
    def _generate_niche_reasoning(self, track: Dict, focus_area: str) -> str:
        """Generate reasoning for niche recommendations"""
        popularity = track.get('popularity', 0)
        artist = track.get('artist', 'Unknown')
        
        if focus_area == "New Artists":
            return f"Emerging artist {artist} with only {popularity}% mainstream recognition - perfect for early discovery!"
        elif focus_area == "Independent Labels":
            return f"Independent release from {artist} - supporting the underground music scene!"
        elif focus_area == "Emerging Genres":
            return f"Genre-bending track that's pushing musical boundaries - {popularity}% popularity means you're ahead of the curve!"
        else:
            return f"Local scene gem from {artist} - discover music before it goes mainstream!"
    
    def _generate_experimental_recommendations(self, user_profile: Dict, intensity: float, experiment_type: str) -> List[Dict]:
        """Generate experimental recommendations"""
        try:
            if experiment_type == "Genre Fusion":
                # Mix user's favorite genres with completely different ones
                return self.spotify_client.get_genre_fusion_recommendations(limit=8)
            
            elif experiment_type == "Decade Jump":
                # Jump to a different decade
                return self.spotify_client.get_decade_jump_recommendations(limit=8)
            
            elif experiment_type == "Mood Opposite":
                # Recommend opposite mood
                return self.spotify_client.get_mood_opposite_recommendations(limit=8)
            
            else:  # Cultural Bridge
                # Explore different cultural music
                return self.spotify_client.get_cultural_bridge_recommendations(limit=8)
        
        except Exception as e:
            st.error(f"Failed to generate experimental recommendations: {e}")
            return []
    
    def _apply_search_filters(self, results: List[Dict], filters: Dict) -> List[Dict]:
        """Apply search filters to results"""
        filtered = []
        
        for track in results:
            # Check popularity range
            popularity = track.get('popularity', 0)
            if not (filters['popularity_range'][0] <= popularity <= filters['popularity_range'][1]):
                continue
            
            # Check year range
            release_date = track.get('release_date')
            if release_date:
                try:
                    year = pd.to_datetime(release_date).year
                    if not (filters['year_range'][0] <= year <= filters['year_range'][1]):
                        continue
                except:
                    pass
            
            # Check audio features
            audio_features = track.get('audio_features', {})
            if audio_features:
                energy = audio_features.get('energy', 0.5)
                if not (filters['energy_range'][0] <= energy <= filters['energy_range'][1]):
                    continue
                
                danceability = audio_features.get('danceability', 0.5)
                if not (filters['danceability_range'][0] <= danceability <= filters['danceability_range'][1]):
                    continue
                
                valence = audio_features.get('valence', 0.5)
                if not (filters['valence_range'][0] <= valence <= filters['valence_range'][1]):
                    continue
            
            # Check genres
            if filters['genres']:
                track_genres = track.get('genres', [])
                if not any(genre.lower() in [g.lower() for g in track_genres] for genre in filters['genres']):
                    continue
            
            filtered.append(track)
        
        return filtered
    
    def _show_playlist_selector(self, track: Dict):
        """Show playlist selection modal"""
        playlists = st.session_state.get('user_playlists', [])
        
        if playlists:
            selected_playlist = st.selectbox(
                "Add to playlist:",
                options=[p['name'] for p in playlists],
                key=f"playlist_select_{track.get('id')}"
            )
            
            if st.button("Add to Playlist", key=f"add_to_pl_{track.get('id')}"):
                # Add track to selected playlist
                for playlist in playlists:
                    if playlist['name'] == selected_playlist:
                        if 'tracks' not in playlist:
                            playlist['tracks'] = []
                        playlist['tracks'].append(track)
                        st.success(f"Added to {selected_playlist}!")
                        break
        else:
            st.info("Create a playlist first to add tracks!")
    
    def _show_track_details(self, track: Dict):
        """Show detailed track information"""
        with st.expander(f"📊 Details for {track.get('name', 'Unknown')}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Artist:** {track.get('artist', 'Unknown')}")
                st.write(f"**Album:** {track.get('album', 'Unknown')}")
                st.write(f"**Release Date:** {track.get('release_date', 'Unknown')}")
                st.write(f"**Popularity:** {track.get('popularity', 0)}/100")
            
            with col2:
                audio_features = track.get('audio_features', {})
                if audio_features:
                    st.write("**Audio Features:**")
                    for feature, value in audio_features.items():
                        if isinstance(value, (int, float)):
                            st.write(f"- {feature.title()}: {value:.2f}")

class AnalyticsPage:
    """Analytics and insights page"""
    
    def __init__(self, evaluator: RecommendationEvaluator):
        self.evaluator = evaluator
    
    def render(self):
        """Render the analytics page"""
        st.title("📊 Music Discovery Analytics")
        
        # Analytics tabs
        tab1, tab2, tab3 = st.tabs(["Diversity Metrics 📈", "Your Profile 👤", "Discovery Journey 🗺️"])
        
        with tab1:
            self._render_diversity_analytics()
        
        with tab2:
            self._render_profile_analytics()
        
        with tab3:
            self._render_discovery_journey()
    
    def _render_diversity_analytics(self):
        """Render diversity metrics"""
        st.markdown("### 📈 Recommendation Diversity Analysis")
        
        # Get latest evaluation metrics
        evaluation_summary = self.evaluator.get_evaluation_summary()
        
        if evaluation_summary:
            AnalyticsComponent.render_diversity_metrics(evaluation_summary.get('latest_evaluation', {}))
        else:
            st.info("No analytics data available yet. Get some recommendations to see your diversity metrics!")
    
    def _render_profile_analytics(self):
        """Render user profile analytics"""
        user_profile = st.session_state.get('user_profile', {})
        AnalyticsComponent.render_user_profile(user_profile)
    
    def _render_discovery_journey(self):
        """Render discovery journey visualization"""
        st.markdown("### 🗺️ Your Musical Discovery Journey")
        
        # Discovery timeline
        liked_tracks = st.session_state.get('liked_tracks', [])
        
        if liked_tracks:
            # Create timeline of discoveries
            discovery_data = []
            for i, track in enumerate(liked_tracks):
                discovery_data.append({
                    'Track': track.get('name', 'Unknown'),
                    'Artist': track.get('artist', 'Unknown'),
                    'Discovery Order': i + 1,
                    'Popularity': track.get('popularity', 0),
                    'Genre': ', '.join(track.get('genres', ['Unknown'])[:2])
                })
            
            df = pd.DataFrame(discovery_data)
            
            # Discovery timeline chart
            fig = px.scatter(
                df,
                x='Discovery Order',
                y='Popularity',
                hover_data=['Track', 'Artist', 'Genre'],
                title="Your Discovery Timeline",
                labels={'Discovery Order': 'Order of Discovery', 'Popularity': 'Track Popularity'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Discovery stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Discoveries", len(liked_tracks))
            
            with col2:
                avg_popularity = df['Popularity'].mean()
                st.metric("Avg. Popularity", f"{avg_popularity:.1f}")
            
            with col3:
                niche_count = len(df[df['Popularity'] < 30])
                st.metric("Niche Discoveries", niche_count)
            
            with col4:
                unique_artists = df['Artist'].nunique()
                st.metric("Unique Artists", unique_artists)
        
        else:
            st.info("Start liking tracks to see your discovery journey!")

class PlaylistPage:
    """Playlist management page"""
    
    def render(self):
        """Render the playlist page"""
        st.title("🎵 Your Playlists")
        
        # Get user playlists
        playlists = st.session_state.get('user_playlists', [])
        
        # Playlist management
        action = PlaylistComponent.render_playlist_manager(playlists)
        
        if action:
            self._handle_playlist_action(action)
        
        # Display playlist details
        if playlists:
            st.markdown("### 📋 Playlist Details")
            
            selected_playlist = st.selectbox(
                "Select a playlist to view:",
                options=[p['name'] for p in playlists],
                key="playlist_viewer"
            )
            
            if selected_playlist:
                playlist = next(p for p in playlists if p['name'] == selected_playlist)
                self._display_playlist_details(playlist)
    
    def _handle_playlist_action(self, action: Dict):
        """Handle playlist actions"""
        if action['action'] == 'create':
            # Create new playlist
            new_playlist = {
                'id': f"playlist_{len(st.session_state.get('user_playlists', []))}",
                'name': action['name'],
                'description': action.get('description', ''),
                'tracks': [],
                'created_at': datetime.now().isoformat()
            }
            
            if 'user_playlists' not in st.session_state:
                st.session_state['user_playlists'] = []
            
            st.session_state['user_playlists'].append(new_playlist)
            st.success(f"✅ Created playlist '{action['name']}'!")
            st.rerun()
    
    def _display_playlist_details(self, playlist: Dict):
        """Display detailed playlist information"""
        st.markdown(f"**{playlist['name']}**")
        
        if playlist.get('description'):
            st.caption(playlist['description'])
        
        tracks = playlist.get('tracks', [])
        
        if tracks:
            st.markdown(f"**{len(tracks)} tracks**")
            
            # Display tracks
            for i, track in enumerate(tracks):
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"{i+1}. **{track.get('name', 'Unknown')}**")
                
                with col2:
                    st.write(track.get('artist', 'Unknown Artist'))
                
                with col3:
                    if st.button("▶️", key=f"play_track_{i}"):
                        st.session_state['current_track'] = track
                        st.session_state['is_playing'] = True
        else:
            st.info("This playlist is empty. Add some tracks from the recommendations!")

class SettingsPage:
    """Settings and preferences page"""
    
    def render(self):
        """Render the settings page"""
        st.title("⚙️ Settings & Preferences")
        
        # Settings tabs
        tab1, tab2, tab3 = st.tabs(["Recommendation Settings 🎯", "Account 👤", "Data & Privacy 🔒"])
        
        with tab1:
            self._render_recommendation_settings()
        
        with tab2:
            self._render_account_settings()
        
        with tab3:
            self._render_privacy_settings()
    
    def _render_recommendation_settings(self):
        """Render recommendation algorithm settings"""
        st.markdown("### 🎯 Recommendation Preferences")
        
        # Algorithm weights
        st.markdown("**Algorithm Balance**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            diversity_weight = st.slider(
                "Diversity vs. Familiarity",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get('diversity_weight', 0.3),
                step=0.1,
                help="Higher values = more diverse, unexpected recommendations",
                key="diversity_setting"
            )
            
            novelty_weight = st.slider(
                "Novelty vs. Popularity",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get('novelty_weight', 0.4),
                step=0.1,
                help="Higher values = more new/niche artists",
                key="novelty_setting"
            )
        
        with col2:
            exploration_rate = st.slider(
                "Exploration Rate",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get('exploration_rate', 0.2),
                step=0.1,
                help="How often to recommend completely new genres",
                key="exploration_setting"
            )
            
            context_sensitivity = st.slider(
                "Context Sensitivity",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get('context_sensitivity', 0.7),
                step=0.1,
                help="How much mood/activity affects recommendations",
                key="context_setting"
            )
        
        # Save settings
        if st.button("💾 Save Recommendation Settings"):
            st.session_state['diversity_weight'] = diversity_weight
            st.session_state['novelty_weight'] = novelty_weight
            st.session_state['exploration_rate'] = exploration_rate
            st.session_state['context_sensitivity'] = context_sensitivity
            st.success("✅ Settings saved!")
    
    def _render_account_settings(self):
        """Render account settings"""
        st.markdown("### 👤 Account Information")
        
        # Spotify connection status
        is_connected = st.session_state.get('spotify_connected', False)
        
        if is_connected:
            st.success("✅ Spotify account connected")
            
            if st.button("🔌 Disconnect Spotify"):
                # Clear Spotify session data
                for key in ['spotify_token', 'spotify_connected', 'user_profile']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("Spotify account disconnected")
                st.rerun()
        else:
            st.warning("⚠️ Spotify account not connected")
            st.info("Connect your Spotify account to get personalized recommendations based on your listening history.")
    
    def _render_privacy_settings(self):
        """Render privacy and data settings"""
        st.markdown("### 🔒 Data & Privacy")
        
        # Data collection preferences
        collect_listening_data = st.checkbox(
            "Allow collection of listening data for better recommendations",
            value=st.session_state.get('collect_listening_data', True),
            key="listening_data_setting"
        )
        
        share_anonymous_data = st.checkbox(
            "Share anonymous usage data to improve the service",
            value=st.session_state.get('share_anonymous_data', False),
            key="anonymous_data_setting"
        )
        
        # Data export/deletion
        st.markdown("**Data Management**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export My Data"):
                # Export user data
                user_data = {
                    'liked_tracks': st.session_state.get('liked_tracks', []),
                    'playlists': st.session_state.get('user_playlists', []),
                    'preferences': {
                        'diversity_weight': st.session_state.get('diversity_weight', 0.3),
                        'novelty_weight': st.session_state.get('novelty_weight', 0.4),
                        'exploration_rate': st.session_state.get('exploration_rate', 0.2)
                    }
                }
                
                st.download_button(
                    "📁 Download Data",
                    data=pd.DataFrame([user_data]).to_json(),
                    file_name=f"music_app_data_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("🗑️ Delete All Data", type="secondary"):
                # Confirm deletion
                if st.button("⚠️ Confirm Deletion", type="secondary"):
                    # Clear all user data
                    keys_to_clear = [
                        'liked_tracks', 'user_playlists', 'user_profile',
                        'for_you_recommendations', 'niche_recommendations',
                        'experimental_recommendations', 'search_results'
                    ]
                    
                    for key in keys_to_clear:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    st.success("All data deleted successfully")
                    st.rerun()
        
        # Save privacy settings
        if st.button("💾 Save Privacy Settings"):
            st.session_state['collect_listening_data'] = collect_listening_data
            st.session_state['share_anonymous_data'] = share_anonymous_data
            st.success("✅ Privacy settings saved!")