import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from datetime import datetime, timedelta
import logging

class SpotifyDataProcessor:
    """Advanced data processor for Spotify music data with bias-aware preprocessing"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        self.pca = PCA(n_components=0.95)  # Retain 95% variance
        self.audio_features = [
            'danceability', 'energy', 'key', 'loudness', 'mode',
            'speechiness', 'acousticness', 'instrumentalness',
            'liveness', 'valence', 'tempo', 'duration_ms'
        ]
        self.logger = logging.getLogger(__name__)
    
    def process_track_data(self, tracks: List[Dict], audio_features: List[Dict] = None) -> pd.DataFrame:
        """Process raw track data into ML-ready format"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(tracks)
            
            if df.empty:
                return df
            
            # Add audio features if provided
            if audio_features:
                audio_df = pd.DataFrame(audio_features)
                df = df.merge(audio_df, on='id', how='left')
            
            # Feature engineering
            df = self._engineer_features(df)
            
            # Handle missing values
            df = self._handle_missing_values(df)
            
            # Add bias-related features
            df = self._add_bias_features(df)
            
            return df
        except Exception as e:
            self.logger.error(f"Failed to process track data: {e}")
            return pd.DataFrame()
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer additional features from raw data"""
        # Temporal features
        if 'release_date' in df.columns:
            df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
            df['release_year'] = df['release_date'].dt.year
            df['days_since_release'] = (datetime.now() - df['release_date']).dt.days
            df['is_recent'] = df['days_since_release'] < 365  # Released within last year
        
        # Duration features
        if 'duration_ms' in df.columns:
            df['duration_minutes'] = df['duration_ms'] / 60000
            df['is_long_track'] = df['duration_minutes'] > 5
            df['is_short_track'] = df['duration_minutes'] < 2.5
        
        # Popularity features
        if 'popularity' in df.columns:
            df['popularity_tier'] = pd.cut(
                df['popularity'], 
                bins=[0, 30, 60, 80, 100], 
                labels=['niche', 'emerging', 'popular', 'mainstream']
            )
            df['is_mainstream'] = df['popularity'] > 70
            df['is_niche'] = df['popularity'] < 30
        
        # Audio feature combinations
        if all(col in df.columns for col in ['energy', 'valence']):
            df['mood_energy'] = df['energy'] * df['valence']  # Happy energetic
            df['mood_calm'] = (1 - df['energy']) * df['valence']  # Happy calm
            df['mood_intense'] = df['energy'] * (1 - df['valence'])  # Sad energetic
            df['mood_melancholy'] = (1 - df['energy']) * (1 - df['valence'])  # Sad calm
        
        if all(col in df.columns for col in ['danceability', 'energy', 'valence']):
            df['party_score'] = (df['danceability'] + df['energy'] + df['valence']) / 3
        
        if all(col in df.columns for col in ['acousticness', 'instrumentalness']):
            df['organic_score'] = (df['acousticness'] + df['instrumentalness']) / 2
        
        # Key and mode features
        if 'key' in df.columns and 'mode' in df.columns:
            df['key_mode'] = df['key'].astype(str) + '_' + df['mode'].astype(str)
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently"""
        # Fill numeric audio features with median
        numeric_features = df.select_dtypes(include=[np.number]).columns
        for col in numeric_features:
            if col in self.audio_features:
                df[col] = df[col].fillna(df[col].median())
        
        # Fill categorical features
        categorical_features = df.select_dtypes(include=['object']).columns
        for col in categorical_features:
            df[col] = df[col].fillna('Unknown')
        
        return df
    
    def _add_bias_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features specifically for bias detection and mitigation"""
        # Novelty score (inverse of popularity with recency boost)
        if 'popularity' in df.columns and 'days_since_release' in df.columns:
            df['novelty_score'] = (100 - df['popularity']) / 100
            # Boost novelty for recent releases
            recent_boost = np.where(df['days_since_release'] < 365, 0.2, 0)
            df['novelty_score'] = np.clip(df['novelty_score'] + recent_boost, 0, 1)
        
        # Diversity potential (how different from mainstream)
        mainstream_features = ['danceability', 'energy', 'valence', 'popularity']
        if all(col in df.columns for col in mainstream_features):
            # Define mainstream profile (high energy, danceable, positive, popular)
            mainstream_profile = np.array([0.7, 0.7, 0.7, 80])
            
            feature_matrix = df[mainstream_features].values
            # Normalize to same scale
            feature_matrix[:, :-1] = feature_matrix[:, :-1]  # Audio features already 0-1
            feature_matrix[:, -1] = feature_matrix[:, -1] / 100  # Normalize popularity
            
            # Calculate distance from mainstream profile
            distances = np.linalg.norm(feature_matrix - mainstream_profile, axis=1)
            df['diversity_potential'] = distances / np.max(distances) if np.max(distances) > 0 else 0
        
        # Artist popularity tier (for artist-level bias detection)
        if 'popularity' in df.columns:
            df['artist_tier'] = pd.cut(
                df['popularity'],
                bins=[0, 20, 40, 60, 80, 100],
                labels=['underground', 'indie', 'emerging', 'established', 'superstar']
            )
        
        return df
    
    def create_user_profile(self, user_tracks: List[Dict], audio_features: List[Dict] = None) -> Dict:
        """Create comprehensive user profile from listening history"""
        try:
            df = self.process_track_data(user_tracks, audio_features)
            
            if df.empty:
                return {}
            
            # Audio feature preferences
            audio_profile = {}
            for feature in self.audio_features:
                if feature in df.columns:
                    audio_profile[f'avg_{feature}'] = df[feature].mean()
                    audio_profile[f'std_{feature}'] = df[feature].std()
            
            # Listening patterns
            listening_patterns = {
                'avg_popularity': df['popularity'].mean() if 'popularity' in df.columns else 0,
                'popularity_variance': df['popularity'].std() if 'popularity' in df.columns else 0,
                'mainstream_ratio': (df['popularity'] > 70).mean() if 'popularity' in df.columns else 0,
                'niche_ratio': (df['popularity'] < 30).mean() if 'popularity' in df.columns else 0,
                'avg_novelty': df['novelty_score'].mean() if 'novelty_score' in df.columns else 0,
                'diversity_preference': df['diversity_potential'].mean() if 'diversity_potential' in df.columns else 0
            }
            
            # Temporal patterns
            temporal_patterns = {}
            if 'release_year' in df.columns:
                temporal_patterns.update({
                    'avg_release_year': df['release_year'].mean(),
                    'year_range': df['release_year'].max() - df['release_year'].min(),
                    'recent_music_ratio': df['is_recent'].mean() if 'is_recent' in df.columns else 0
                })
            
            # Mood preferences
            mood_preferences = {}
            mood_features = ['mood_energy', 'mood_calm', 'mood_intense', 'mood_melancholy']
            for mood in mood_features:
                if mood in df.columns:
                    mood_preferences[mood] = df[mood].mean()
            
            # Combine all profiles
            user_profile = {
                'audio_preferences': audio_profile,
                'listening_patterns': listening_patterns,
                'temporal_patterns': temporal_patterns,
                'mood_preferences': mood_preferences,
                'total_tracks': len(df),
                'unique_artists': df['artist'].nunique() if 'artist' in df.columns else 0,
                'profile_created': datetime.now().isoformat()
            }
            
            return user_profile
        except Exception as e:
            self.logger.error(f"Failed to create user profile: {e}")
            return {}
    
    def calculate_track_similarity(self, track1: Dict, track2: Dict, weights: Dict = None) -> float:
        """Calculate similarity between two tracks"""
        try:
            if weights is None:
                weights = {
                    'audio_features': 0.6,
                    'popularity': 0.2,
                    'temporal': 0.1,
                    'artist': 0.1
                }
            
            similarity_score = 0.0
            
            # Audio feature similarity
            audio_sim = self._calculate_audio_similarity(track1, track2)
            similarity_score += audio_sim * weights['audio_features']
            
            # Popularity similarity
            pop_sim = self._calculate_popularity_similarity(track1, track2)
            similarity_score += pop_sim * weights['popularity']
            
            # Temporal similarity
            temp_sim = self._calculate_temporal_similarity(track1, track2)
            similarity_score += temp_sim * weights['temporal']
            
            # Artist similarity
            artist_sim = 1.0 if track1.get('artist_id') == track2.get('artist_id') else 0.0
            similarity_score += artist_sim * weights['artist']
            
            return similarity_score
        except Exception as e:
            self.logger.error(f"Failed to calculate track similarity: {e}")
            return 0.0
    
    def _calculate_audio_similarity(self, track1: Dict, track2: Dict) -> float:
        """Calculate audio feature similarity"""
        try:
            features = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness']
            
            similarities = []
            for feature in features:
                if feature in track1 and feature in track2:
                    # Use inverse of absolute difference
                    diff = abs(track1[feature] - track2[feature])
                    sim = 1 - diff
                    similarities.append(sim)
            
            return np.mean(similarities) if similarities else 0.0
        except Exception as e:
            self.logger.error(f"Failed to calculate audio similarity: {e}")
            return 0.0
    
    def _calculate_popularity_similarity(self, track1: Dict, track2: Dict) -> float:
        """Calculate popularity-based similarity"""
        try:
            pop1 = track1.get('popularity', 0)
            pop2 = track2.get('popularity', 0)
            
            # Normalize to 0-1 scale and calculate similarity
            diff = abs(pop1 - pop2) / 100
            return 1 - diff
        except Exception as e:
            self.logger.error(f"Failed to calculate popularity similarity: {e}")
            return 0.0
    
    def _calculate_temporal_similarity(self, track1: Dict, track2: Dict) -> float:
        """Calculate temporal similarity based on release dates"""
        try:
            date1 = track1.get('release_date')
            date2 = track2.get('release_date')
            
            if not date1 or not date2:
                return 0.5  # Neutral similarity if dates missing
            
            # Convert to datetime if string
            if isinstance(date1, str):
                date1 = pd.to_datetime(date1)
            if isinstance(date2, str):
                date2 = pd.to_datetime(date2)
            
            # Calculate year difference
            year_diff = abs(date1.year - date2.year)
            
            # Similarity decreases with year difference
            if year_diff == 0:
                return 1.0
            elif year_diff <= 2:
                return 0.8
            elif year_diff <= 5:
                return 0.6
            elif year_diff <= 10:
                return 0.4
            else:
                return 0.2
        except Exception as e:
            self.logger.error(f"Failed to calculate temporal similarity: {e}")
            return 0.5
    
    def prepare_ml_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """Prepare features for ML models"""
        try:
            # Select numeric features for ML
            feature_columns = []
            
            # Audio features
            for feature in self.audio_features:
                if feature in df.columns:
                    feature_columns.append(feature)
            
            # Engineered features
            engineered_features = [
                'novelty_score', 'diversity_potential', 'mood_energy',
                'mood_calm', 'mood_intense', 'mood_melancholy', 'party_score',
                'organic_score', 'duration_minutes', 'days_since_release'
            ]
            
            for feature in engineered_features:
                if feature in df.columns:
                    feature_columns.append(feature)
            
            # Extract feature matrix
            X = df[feature_columns].values
            
            # Handle any remaining NaN values
            X = np.nan_to_num(X, nan=0.0)
            
            return X, feature_columns
        except Exception as e:
            self.logger.error(f"Failed to prepare ML features: {e}")
            return np.array([]), []
    
    def normalize_features(self, X: np.ndarray, fit: bool = True) -> np.ndarray:
        """Normalize features for ML models"""
        try:
            if fit:
                return self.scaler.fit_transform(X)
            else:
                return self.scaler.transform(X)
        except Exception as e:
            self.logger.error(f"Failed to normalize features: {e}")
            return X