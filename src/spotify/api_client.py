import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import time
import logging
from datetime import datetime, timedelta

class SpotifyClient:
    """Enhanced Spotify API client with bias-aware data collection"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8501/callback"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        # Initialize both auth methods
        self.client_credentials = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        
        self.oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-read-private user-read-email user-library-read user-top-read playlist-read-private user-read-recently-played"
        )
        
        # Initialize Spotify clients
        self.sp_public = spotipy.Spotify(client_credentials_manager=self.client_credentials)
        self.sp_user = None
        
        self.logger = logging.getLogger(__name__)
    
    def authenticate_user(self) -> bool:
        """Authenticate user for personalized features"""
        try:
            token_info = self.oauth.get_access_token(as_dict=False)
            if token_info:
                self.sp_user = spotipy.Spotify(auth=token_info)
                return True
        except Exception as e:
            self.logger.error(f"User authentication failed: {e}")
        return False
    
    def search_tracks(self, query: str, limit: int = 50, market: str = "US") -> List[Dict]:
        """Search for tracks with enhanced metadata"""
        try:
            results = self.sp_public.search(q=query, type='track', limit=limit, market=market)
            tracks = []
            
            for track in results['tracks']['items']:
                track_data = self._extract_track_features(track)
                tracks.append(track_data)
            
            return tracks
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def get_track_audio_features(self, track_ids: List[str]) -> List[Dict]:
        """Get audio features for multiple tracks"""
        try:
            # Spotify API allows max 100 tracks per request
            all_features = []
            for i in range(0, len(track_ids), 100):
                batch = track_ids[i:i+100]
                features = self.sp_public.audio_features(batch)
                all_features.extend([f for f in features if f is not None])
            
            return all_features
        except Exception as e:
            self.logger.error(f"Failed to get audio features: {e}")
            return []
    
    def get_user_top_tracks(self, time_range: str = "medium_term", limit: int = 50) -> List[Dict]:
        """Get user's top tracks with bias analysis"""
        if not self.sp_user:
            return []
        
        try:
            results = self.sp_user.current_user_top_tracks(
                time_range=time_range, 
                limit=limit
            )
            
            tracks = []
            for track in results['items']:
                track_data = self._extract_track_features(track)
                tracks.append(track_data)
            
            return tracks
        except Exception as e:
            self.logger.error(f"Failed to get top tracks: {e}")
            return []
    
    def get_recommendations(self, seed_tracks: List[str] = None, seed_artists: List[str] = None, 
                          seed_genres: List[str] = None, target_features: Dict = None, 
                          limit: int = 20, market: str = "US") -> List[Dict]:
        """Get recommendations with bias-aware parameters"""
        try:
            # Prepare parameters
            kwargs = {
                'limit': limit,
                'market': market
            }
            
            if seed_tracks:
                kwargs['seed_tracks'] = seed_tracks[:5]  # Max 5 seeds
            if seed_artists:
                kwargs['seed_artists'] = seed_artists[:5]
            if seed_genres:
                kwargs['seed_genres'] = seed_genres[:5]
            
            # Add target audio features for fine-tuning
            if target_features:
                for feature, value in target_features.items():
                    if feature in ['danceability', 'energy', 'valence', 'acousticness', 
                                 'instrumentalness', 'liveness', 'speechiness']:
                        kwargs[f'target_{feature}'] = value
            
            results = self.sp_public.recommendations(**kwargs)
            
            tracks = []
            for track in results['tracks']:
                track_data = self._extract_track_features(track)
                tracks.append(track_data)
            
            return tracks
        except Exception as e:
            self.logger.error(f"Failed to get recommendations: {e}")
            return []
    
    def discover_niche_artists(self, genre: str = None, limit: int = 20) -> List[Dict]:
        """Discover lesser-known artists and tracks"""
        try:
            # Search for tracks with low popularity
            if genre:
                query = f"genre:{genre}"
            else:
                query = "year:2020-2024"  # Recent tracks more likely to be niche
            
            results = self.sp_public.search(
                q=query, 
                type='track', 
                limit=50,
                market="US"
            )
            
            # Filter for low popularity (niche) tracks
            niche_tracks = []
            for track in results['tracks']['items']:
                if track['popularity'] < 50:  # Low popularity threshold
                    track_data = self._extract_track_features(track)
                    niche_tracks.append(track_data)
                
                if len(niche_tracks) >= limit:
                    break
            
            return niche_tracks
        except Exception as e:
            self.logger.error(f"Failed to discover niche artists: {e}")
            return []
    
    def get_genre_seeds(self) -> List[str]:
        """Get available genre seeds from Spotify"""
        try:
            genres = self.sp_public.recommendation_genre_seeds()
            return genres['genres']
        except Exception as e:
            self.logger.error(f"Failed to get genre seeds: {e}")
            return []
    
    def analyze_user_bias(self) -> Dict:
        """Analyze user's listening patterns for bias detection"""
        if not self.sp_user:
            return {}
        
        try:
            # Get user's top tracks and artists
            top_tracks = self.get_user_top_tracks(limit=50)
            top_artists = self.sp_user.current_user_top_artists(limit=50)
            
            # Calculate bias metrics
            popularity_scores = [track['popularity'] for track in top_tracks]
            avg_popularity = np.mean(popularity_scores) if popularity_scores else 0
            
            # Genre diversity
            genres = set()
            for artist in top_artists['items']:
                genres.update(artist.get('genres', []))
            
            bias_analysis = {
                'avg_popularity': avg_popularity,
                'popularity_bias': 'high' if avg_popularity > 70 else 'medium' if avg_popularity > 40 else 'low',
                'genre_diversity': len(genres),
                'total_genres': list(genres),
                'mainstream_ratio': len([p for p in popularity_scores if p > 70]) / len(popularity_scores) if popularity_scores else 0
            }
            
            return bias_analysis
        except Exception as e:
            self.logger.error(f"Failed to analyze user bias: {e}")
            return {}
    
    def _extract_track_features(self, track: Dict) -> Dict:
        """Extract and standardize track features"""
        return {
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
            'artist_id': track['artists'][0]['id'] if track['artists'] else None,
            'album': track['album']['name'],
            'popularity': track['popularity'],
            'duration_ms': track['duration_ms'],
            'explicit': track['explicit'],
            'preview_url': track.get('preview_url'),
            'external_urls': track.get('external_urls', {}),
            'release_date': track['album'].get('release_date'),
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'uri': track['uri']
        }
    
    def get_artist_info(self, artist_id: str) -> Dict:
        """Get detailed artist information"""
        try:
            artist = self.sp_public.artist(artist_id)
            return {
                'id': artist['id'],
                'name': artist['name'],
                'genres': artist['genres'],
                'popularity': artist['popularity'],
                'followers': artist['followers']['total'],
                'image_url': artist['images'][0]['url'] if artist['images'] else None
            }
        except Exception as e:
            self.logger.error(f"Failed to get artist info: {e}")
            return {}
    
    def create_diversity_playlist(self, user_preferences: Dict, size: int = 30) -> List[Dict]:
        """Create a diverse playlist based on user preferences and bias reduction"""
        try:
            playlist = []
            
            # Get some mainstream tracks (30%)
            mainstream_count = int(size * 0.3)
            mainstream_tracks = self.search_tracks("year:2023-2024", limit=mainstream_count * 2)
            mainstream_tracks = [t for t in mainstream_tracks if t['popularity'] > 60][:mainstream_count]
            playlist.extend(mainstream_tracks)
            
            # Get niche tracks (40%)
            niche_count = int(size * 0.4)
            niche_tracks = self.discover_niche_artists(limit=niche_count)
            playlist.extend(niche_tracks)
            
            # Get experimental tracks (30%)
            experimental_count = size - len(playlist)
            genres = self.get_genre_seeds()
            if genres:
                experimental_tracks = self.get_recommendations(
                    seed_genres=np.random.choice(genres, min(3, len(genres))).tolist(),
                    limit=experimental_count
                )
                playlist.extend(experimental_tracks)
            
            return playlist[:size]
        except Exception as e:
            self.logger.error(f"Failed to create diversity playlist: {e}")
            return []