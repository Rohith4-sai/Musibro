import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import json
import hashlib
import time
from datetime import datetime, timedelta
import re
import logging
from functools import wraps
import base64
from io import BytesIO
import requests
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px

class CacheManager:
    """Manage caching for API calls and computations"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self.logger = logging.getLogger(__name__)
    
    def get_cache_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def is_cache_valid(self, timestamp: float) -> bool:
        """Check if cached data is still valid"""
        return time.time() - timestamp < self.ttl_seconds
    
    def cache_data(self, key: str, data: Any) -> None:
        """Cache data with timestamp"""
        if 'cache' not in st.session_state:
            st.session_state['cache'] = {}
        
        st.session_state['cache'][key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Retrieve cached data if valid"""
        cache = st.session_state.get('cache', {})
        
        if key in cache:
            cached_item = cache[key]
            if self.is_cache_valid(cached_item['timestamp']):
                return cached_item['data']
            else:
                # Remove expired cache
                del cache[key]
        
        return None
    
    def clear_cache(self, pattern: Optional[str] = None) -> None:
        """Clear cache entries, optionally matching a pattern"""
        if 'cache' not in st.session_state:
            return
        
        if pattern is None:
            st.session_state['cache'] = {}
            self.logger.info("Cleared all cache")
        else:
            cache = st.session_state['cache']
            keys_to_remove = [key for key in cache.keys() if pattern in key]
            
            for key in keys_to_remove:
                del cache[key]
            
            self.logger.info(f"Cleared {len(keys_to_remove)} cache entries matching '{pattern}'")

def cached_function(ttl_seconds: int = 3600):
    """Decorator to cache function results"""
    cache_manager = CacheManager(ttl_seconds)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}_{cache_manager.get_cache_key(*args, **kwargs)}"
            
            # Try to get cached result
            cached_result = cache_manager.get_cached_data(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.cache_data(cache_key, result)
            
            return result
        
        return wrapper
    return decorator

class DataProcessor:
    """Utility functions for data processing"""
    
    @staticmethod
    def normalize_audio_features(features: Dict[str, float]) -> Dict[str, float]:
        """Normalize audio features to 0-1 range"""
        normalized = {}
        
        # Features already in 0-1 range
        direct_features = ['danceability', 'energy', 'speechiness', 'acousticness', 
                          'instrumentalness', 'liveness', 'valence']
        
        for feature in direct_features:
            if feature in features:
                normalized[feature] = max(0, min(1, features[feature]))
        
        # Tempo normalization (typical range: 60-200 BPM)
        if 'tempo' in features:
            tempo = features['tempo']
            normalized['tempo'] = max(0, min(1, (tempo - 60) / 140))
        
        # Loudness normalization (typical range: -60 to 0 dB)
        if 'loudness' in features:
            loudness = features['loudness']
            normalized['loudness'] = max(0, min(1, (loudness + 60) / 60))
        
        # Duration normalization (typical range: 30s to 10min)
        if 'duration_ms' in features:
            duration_s = features['duration_ms'] / 1000
            normalized['duration'] = max(0, min(1, (duration_s - 30) / 570))
        
        return normalized
    
    @staticmethod
    def calculate_audio_similarity(features1: Dict[str, float], features2: Dict[str, float], 
                                 weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate similarity between two audio feature vectors"""
        if weights is None:
            weights = {
                'danceability': 0.2, 'energy': 0.2, 'valence': 0.15,
                'acousticness': 0.1, 'instrumentalness': 0.1,
                'tempo': 0.15, 'loudness': 0.1
            }
        
        # Normalize features
        norm_features1 = DataProcessor.normalize_audio_features(features1)
        norm_features2 = DataProcessor.normalize_audio_features(features2)
        
        # Calculate weighted similarity
        similarity = 0.0
        total_weight = 0.0
        
        for feature, weight in weights.items():
            if feature in norm_features1 and feature in norm_features2:
                diff = abs(norm_features1[feature] - norm_features2[feature])
                similarity += (1 - diff) * weight
                total_weight += weight
        
        return similarity / total_weight if total_weight > 0 else 0.0
    
    @staticmethod
    def extract_genres_from_text(text: str) -> List[str]:
        """Extract genre keywords from text"""
        genre_keywords = [
            'pop', 'rock', 'hip-hop', 'rap', 'electronic', 'dance', 'edm',
            'indie', 'alternative', 'jazz', 'blues', 'classical', 'country',
            'folk', 'r&b', 'soul', 'funk', 'reggae', 'metal', 'punk',
            'ambient', 'techno', 'house', 'dubstep', 'trap', 'lo-fi'
        ]
        
        text_lower = text.lower()
        found_genres = []
        
        for genre in genre_keywords:
            if genre in text_lower:
                found_genres.append(genre)
        
        return found_genres
    
    @staticmethod
    def calculate_diversity_score(items: List[Dict], feature_key: str = 'genres') -> float:
        """Calculate diversity score for a list of items"""
        if not items:
            return 0.0
        
        # Collect all unique values
        all_values = set()
        for item in items:
            values = item.get(feature_key, [])
            if isinstance(values, list):
                all_values.update(values)
            else:
                all_values.add(values)
        
        # Diversity is the ratio of unique values to total possible
        max_possible_diversity = len(items)
        actual_diversity = len(all_values)
        
        return min(1.0, actual_diversity / max_possible_diversity)
    
    @staticmethod
    def calculate_novelty_score(items: List[Dict], popularity_key: str = 'popularity') -> float:
        """Calculate novelty score based on popularity"""
        if not items:
            return 0.0
        
        popularities = []
        for item in items:
            pop = item.get(popularity_key, 50)  # Default to medium popularity
            popularities.append(pop)
        
        # Novelty is inverse of average popularity
        avg_popularity = np.mean(popularities)
        novelty = (100 - avg_popularity) / 100
        
        return max(0.0, min(1.0, novelty))

class UIHelpers:
    """Helper functions for UI components"""
    
    @staticmethod
    def create_gradient_background(color1: str, color2: str, direction: str = "135deg") -> str:
        """Create CSS gradient background"""
        return f"background: linear-gradient({direction}, {color1}, {color2});"
    
    @staticmethod
    def format_duration(duration_ms: int) -> str:
        """Format duration from milliseconds to human readable"""
        if duration_ms == 0:
            return "0:00"
        
        total_seconds = duration_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    @staticmethod
    def create_star_rating(rating: float, max_rating: int = 5) -> str:
        """Create star rating HTML"""
        full_stars = int(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = max_rating - full_stars - half_star
        
        stars_html = "⭐" * full_stars
        if half_star:
            stars_html += "⭐"  # Could use half-star emoji if available
        stars_html += "☆" * empty_stars
        
        return stars_html
    
    @staticmethod
    def create_progress_bar(value: float, max_value: float = 1.0, 
                          color: str = "#667eea", height: str = "10px") -> str:
        """Create HTML progress bar"""
        percentage = (value / max_value) * 100
        
        return f"""
        <div style="
            width: 100%;
            background-color: #e0e0e0;
            border-radius: 5px;
            height: {height};
        ">
            <div style="
                width: {percentage}%;
                background-color: {color};
                height: 100%;
                border-radius: 5px;
                transition: width 0.3s ease;
            "></div>
        </div>
        """
    
    @staticmethod
    def create_metric_card(title: str, value: str, delta: Optional[str] = None, 
                          color: str = "#667eea") -> str:
        """Create a metric card HTML"""
        delta_html = ""
        if delta:
            delta_color = "green" if delta.startswith("+") else "red" if delta.startswith("-") else "gray"
            delta_html = f'<div style="color: {delta_color}; font-size: 14px;">{delta}</div>'
        
        return f"""
        <div style="
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid {color};
            margin: 10px 0;
        ">
            <div style="color: #666; font-size: 14px; margin-bottom: 5px;">{title}</div>
            <div style="font-size: 24px; font-weight: bold; color: #333;">{value}</div>
            {delta_html}
        </div>
        """
    
    @staticmethod
    def create_audio_visualizer(audio_features: Dict[str, float]) -> go.Figure:
        """Create audio features radar chart"""
        features = ['danceability', 'energy', 'valence', 'acousticness', 
                   'instrumentalness', 'speechiness']
        
        values = [audio_features.get(feature, 0) for feature in features]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=[f.title() for f in features],
            fill='toself',
            name='Audio Features',
            line_color='rgb(102, 126, 234)',
            fillcolor='rgba(102, 126, 234, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickmode='linear',
                    tick0=0,
                    dtick=0.2
                )
            ),
            showlegend=False,
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig

class ValidationHelpers:
    """Helper functions for data validation"""
    
    @staticmethod
    def validate_audio_features(features: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate audio features dictionary"""
        errors = []
        required_features = ['danceability', 'energy', 'valence']
        
        # Check required features
        for feature in required_features:
            if feature not in features:
                errors.append(f"Missing required feature: {feature}")
            elif not isinstance(features[feature], (int, float)):
                errors.append(f"Feature {feature} must be numeric")
            elif not (0 <= features[feature] <= 1):
                errors.append(f"Feature {feature} must be between 0 and 1")
        
        # Check optional features
        optional_features = ['acousticness', 'instrumentalness', 'liveness', 'speechiness']
        for feature in optional_features:
            if feature in features:
                if not isinstance(features[feature], (int, float)):
                    errors.append(f"Feature {feature} must be numeric")
                elif not (0 <= features[feature] <= 1):
                    errors.append(f"Feature {feature} must be between 0 and 1")
        
        # Check tempo
        if 'tempo' in features:
            if not isinstance(features['tempo'], (int, float)):
                errors.append("Tempo must be numeric")
            elif not (0 <= features['tempo'] <= 300):
                errors.append("Tempo must be between 0 and 300 BPM")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_track_data(track: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate track data dictionary"""
        errors = []
        required_fields = ['id', 'name', 'artist']
        
        # Check required fields
        for field in required_fields:
            if field not in track:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(track[field], str) or not track[field].strip():
                errors.append(f"Field {field} must be a non-empty string")
        
        # Check optional numeric fields
        numeric_fields = ['popularity', 'duration_ms']
        for field in numeric_fields:
            if field in track:
                if not isinstance(track[field], (int, float)):
                    errors.append(f"Field {field} must be numeric")
                elif field == 'popularity' and not (0 <= track[field] <= 100):
                    errors.append("Popularity must be between 0 and 100")
                elif field == 'duration_ms' and track[field] < 0:
                    errors.append("Duration must be non-negative")
        
        # Validate audio features if present
        if 'audio_features' in track:
            features_valid, feature_errors = ValidationHelpers.validate_audio_features(track['audio_features'])
            if not features_valid:
                errors.extend(feature_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_user_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input text"""
        if not isinstance(text, str):
            return ""
        
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\']', '', text)
        
        # Limit length
        sanitized = sanitized[:max_length]
        
        # Strip whitespace
        sanitized = sanitized.strip()
        
        return sanitized

class PerformanceHelpers:
    """Helper functions for performance optimization"""
    
    @staticmethod
    def batch_process(items: List[Any], batch_size: int = 50, 
                     process_func: callable = None) -> List[Any]:
        """Process items in batches to avoid memory issues"""
        if process_func is None:
            return items
        
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = process_func(batch)
            results.extend(batch_results)
        
        return results
    
    @staticmethod
    def measure_execution_time(func: callable) -> callable:
        """Decorator to measure function execution time"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            logger = logging.getLogger(__name__)
            logger.debug(f"Function {func.__name__} executed in {execution_time:.3f} seconds")
            
            return result
        return wrapper
    
    @staticmethod
    def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Optimize pandas DataFrame memory usage"""
        # Convert object columns to category if they have few unique values
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique values
                df[col] = df[col].astype('category')
        
        # Downcast numeric columns
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        return df

class ErrorHandlers:
    """Error handling utilities"""
    
    @staticmethod
    def safe_execute(func: callable, default_return: Any = None, 
                    log_errors: bool = True) -> Any:
        """Safely execute a function with error handling"""
        try:
            return func()
        except Exception as e:
            if log_errors:
                logger = logging.getLogger(__name__)
                logger.error(f"Error in {func.__name__ if hasattr(func, '__name__') else 'function'}: {e}")
            return default_return
    
    @staticmethod
    def create_error_message(error: Exception, context: str = "") -> str:
        """Create user-friendly error message"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Common error translations
        if "ConnectionError" in error_type:
            return "Unable to connect to the service. Please check your internet connection."
        elif "TimeoutError" in error_type:
            return "The request timed out. Please try again."
        elif "AuthenticationError" in error_type or "401" in error_msg:
            return "Authentication failed. Please check your credentials."
        elif "RateLimitError" in error_type or "429" in error_msg:
            return "Too many requests. Please wait a moment and try again."
        else:
            return f"An error occurred{' ' + context if context else ''}: {error_msg}"

# Convenience functions
def show_loading_spinner(text: str = "Loading..."):
    """Show loading spinner with text"""
    return st.spinner(text)

def show_success_message(message: str, icon: str = "✅"):
    """Show success message"""
    st.success(f"{icon} {message}")

def show_error_message(message: str, icon: str = "❌"):
    """Show error message"""
    st.error(f"{icon} {message}")

def show_info_message(message: str, icon: str = "ℹ️"):
    """Show info message"""
    st.info(f"{icon} {message}")

def show_warning_message(message: str, icon: str = "⚠️"):
    """Show warning message"""
    st.warning(f"{icon} {message}")

def format_number(number: Union[int, float], precision: int = 2) -> str:
    """Format number for display"""
    if isinstance(number, int):
        return f"{number:,}"
    else:
        return f"{number:,.{precision}f}"

def get_time_ago(timestamp: datetime) -> str:
    """Get human-readable time ago string"""
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def create_download_link(data: Any, filename: str, link_text: str = "Download") -> str:
    """Create download link for data"""
    if isinstance(data, pd.DataFrame):
        csv = data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    elif isinstance(data, dict):
        json_str = json.dumps(data, indent=2)
        b64 = base64.b64encode(json_str.encode()).decode()
        href = f'<a href="data:file/json;base64,{b64}" download="{filename}">{link_text}</a>'
    else:
        # Assume it's already a string
        b64 = base64.b64encode(str(data).encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{link_text}</a>'
    
    return href