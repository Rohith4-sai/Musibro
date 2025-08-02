import os
import streamlit as st
from typing import Dict, Any, Optional
import json
from pathlib import Path
import logging

class Config:
    """Configuration management for the music recommendation app"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables and defaults"""
        # Spotify API Configuration
        self.SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '')
        self.SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '')
        self.SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8501/callback')
        
        # App Configuration
        self.APP_NAME = os.getenv('APP_NAME', 'Advanced Music Recommendation System')
        self.APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
        self.DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        
        # ML Model Configuration
        self.MODEL_CACHE_DIR = os.getenv('MODEL_CACHE_DIR', 'models')
        self.DATA_CACHE_DIR = os.getenv('DATA_CACHE_DIR', 'data')
        self.MAX_CACHE_SIZE_MB = int(os.getenv('MAX_CACHE_SIZE_MB', '500'))
        
        # Recommendation System Configuration
        self.DEFAULT_RECOMMENDATION_COUNT = int(os.getenv('DEFAULT_RECOMMENDATION_COUNT', '10'))
        self.MAX_RECOMMENDATION_COUNT = int(os.getenv('MAX_RECOMMENDATION_COUNT', '50'))
        self.DEFAULT_DIVERSITY_WEIGHT = float(os.getenv('DEFAULT_DIVERSITY_WEIGHT', '0.3'))
        self.DEFAULT_NOVELTY_WEIGHT = float(os.getenv('DEFAULT_NOVELTY_WEIGHT', '0.4'))
        self.DEFAULT_EXPLORATION_RATE = float(os.getenv('DEFAULT_EXPLORATION_RATE', '0.2'))
        
        # Audio Feature Weights
        self.AUDIO_FEATURE_WEIGHTS = {
            'danceability': float(os.getenv('WEIGHT_DANCEABILITY', '0.2')),
            'energy': float(os.getenv('WEIGHT_ENERGY', '0.2')),
            'valence': float(os.getenv('WEIGHT_VALENCE', '0.15')),
            'acousticness': float(os.getenv('WEIGHT_ACOUSTICNESS', '0.1')),
            'instrumentalness': float(os.getenv('WEIGHT_INSTRUMENTALNESS', '0.1')),
            'liveness': float(os.getenv('WEIGHT_LIVENESS', '0.05')),
            'speechiness': float(os.getenv('WEIGHT_SPEECHINESS', '0.05')),
            'tempo': float(os.getenv('WEIGHT_TEMPO', '0.15'))
        }
        
        # Bias Reduction Configuration
        self.POPULARITY_BIAS_THRESHOLD = float(os.getenv('POPULARITY_BIAS_THRESHOLD', '0.7'))
        self.DIVERSITY_INJECTION_RATE = float(os.getenv('DIVERSITY_INJECTION_RATE', '0.3'))
        self.FAIRNESS_CONSTRAINT_WEIGHT = float(os.getenv('FAIRNESS_CONSTRAINT_WEIGHT', '0.2'))
        
        # UI Configuration
        self.THEME_COLOR = os.getenv('THEME_COLOR', '#667eea')
        self.ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', '20'))
        self.ENABLE_ANIMATIONS = os.getenv('ENABLE_ANIMATIONS', 'True').lower() == 'true'
        
        # Performance Configuration
        self.CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', '3600'))  # 1 hour
        self.API_RATE_LIMIT_PER_MINUTE = int(os.getenv('API_RATE_LIMIT_PER_MINUTE', '100'))
        self.BATCH_SIZE = int(os.getenv('BATCH_SIZE', '50'))
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'music_app.log')
        
        # Feature Flags
        self.ENABLE_EXPERIMENTAL_FEATURES = os.getenv('ENABLE_EXPERIMENTAL_FEATURES', 'True').lower() == 'true'
        self.ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'True').lower() == 'true'
        self.ENABLE_FEEDBACK_COLLECTION = os.getenv('ENABLE_FEEDBACK_COLLECTION', 'True').lower() == 'true'
        
        # Validate configuration (Spotify credentials optional during startup)
        self._validate_config(require_spotify_credentials=False)
    
    def _validate_config(self, require_spotify_credentials=False):
        """Validate configuration values"""
        errors = []
        
        # Check required Spotify credentials only if explicitly required
        if require_spotify_credentials:
            if not self.SPOTIFY_CLIENT_ID:
                errors.append("SPOTIFY_CLIENT_ID is required")
            
            if not self.SPOTIFY_CLIENT_SECRET:
                errors.append("SPOTIFY_CLIENT_SECRET is required")
        else:
            # Just log a warning if credentials are missing
            if not self.SPOTIFY_CLIENT_ID or not self.SPOTIFY_CLIENT_SECRET:
                self.logger.warning("Spotify credentials not configured. Some features may be limited.")
        
        # Validate numeric ranges
        if not (0 <= self.DEFAULT_DIVERSITY_WEIGHT <= 1):
            errors.append("DEFAULT_DIVERSITY_WEIGHT must be between 0 and 1")
        
        if not (0 <= self.DEFAULT_NOVELTY_WEIGHT <= 1):
            errors.append("DEFAULT_NOVELTY_WEIGHT must be between 0 and 1")
        
        if not (0 <= self.DEFAULT_EXPLORATION_RATE <= 1):
            errors.append("DEFAULT_EXPLORATION_RATE must be between 0 and 1")
        
        # Validate audio feature weights sum to 1
        weight_sum = sum(self.AUDIO_FEATURE_WEIGHTS.values())
        if abs(weight_sum - 1.0) > 0.01:  # Allow small floating point errors
            self.logger.warning(f"Audio feature weights sum to {weight_sum}, normalizing to 1.0")
            # Normalize weights
            for feature in self.AUDIO_FEATURE_WEIGHTS:
                self.AUDIO_FEATURE_WEIGHTS[feature] /= weight_sum
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            self.logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_spotify_config(self) -> Dict[str, str]:
        """Get Spotify API configuration"""
        return {
            'client_id': self.SPOTIFY_CLIENT_ID,
            'client_secret': self.SPOTIFY_CLIENT_SECRET,
            'redirect_uri': self.SPOTIFY_REDIRECT_URI
        }
    
    def validate_spotify_credentials(self) -> bool:
        """Validate that Spotify credentials are properly configured"""
        try:
            self._validate_config(require_spotify_credentials=True)
            return True
        except ValueError:
            return False
    
    def get_ml_config(self) -> Dict[str, Any]:
        """Get ML model configuration"""
        return {
            'model_cache_dir': self.MODEL_CACHE_DIR,
            'data_cache_dir': self.DATA_CACHE_DIR,
            'max_cache_size_mb': self.MAX_CACHE_SIZE_MB,
            'audio_feature_weights': self.AUDIO_FEATURE_WEIGHTS,
            'batch_size': self.BATCH_SIZE
        }
    
    def get_recommendation_config(self) -> Dict[str, Any]:
        """Get recommendation system configuration"""
        return {
            'default_count': self.DEFAULT_RECOMMENDATION_COUNT,
            'max_count': self.MAX_RECOMMENDATION_COUNT,
            'diversity_weight': self.DEFAULT_DIVERSITY_WEIGHT,
            'novelty_weight': self.DEFAULT_NOVELTY_WEIGHT,
            'exploration_rate': self.DEFAULT_EXPLORATION_RATE,
            'popularity_bias_threshold': self.POPULARITY_BIAS_THRESHOLD,
            'diversity_injection_rate': self.DIVERSITY_INJECTION_RATE,
            'fairness_constraint_weight': self.FAIRNESS_CONSTRAINT_WEIGHT
        }
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration"""
        return {
            'theme_color': self.THEME_COLOR,
            'items_per_page': self.ITEMS_PER_PAGE,
            'enable_animations': self.ENABLE_ANIMATIONS,
            'app_name': self.APP_NAME,
            'app_version': self.APP_VERSION
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return {
            'cache_ttl_seconds': self.CACHE_TTL_SECONDS,
            'api_rate_limit_per_minute': self.API_RATE_LIMIT_PER_MINUTE,
            'batch_size': self.BATCH_SIZE
        }
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags"""
        return {
            'experimental_features': self.ENABLE_EXPERIMENTAL_FEATURES,
            'analytics': self.ENABLE_ANALYTICS,
            'feedback_collection': self.ENABLE_FEEDBACK_COLLECTION,
            'debug_mode': self.DEBUG_MODE
        }
    
    def update_user_preferences(self, preferences: Dict[str, Any]):
        """Update user-specific preferences in session state"""
        if 'user_preferences' not in st.session_state:
            st.session_state['user_preferences'] = {}
        
        st.session_state['user_preferences'].update(preferences)
        self.logger.info(f"Updated user preferences: {list(preferences.keys())}")
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get user-specific preference with fallback to default config"""
        user_prefs = st.session_state.get('user_preferences', {})
        
        if key in user_prefs:
            return user_prefs[key]
        
        # Fallback to default config values
        config_mapping = {
            'diversity_weight': self.DEFAULT_DIVERSITY_WEIGHT,
            'novelty_weight': self.DEFAULT_NOVELTY_WEIGHT,
            'exploration_rate': self.DEFAULT_EXPLORATION_RATE,
            'recommendation_count': self.DEFAULT_RECOMMENDATION_COUNT,
            'theme_color': self.THEME_COLOR,
            'items_per_page': self.ITEMS_PER_PAGE
        }
        
        return config_mapping.get(key, default)
    
    def save_user_preferences_to_file(self, filepath: Optional[str] = None):
        """Save user preferences to a JSON file"""
        if filepath is None:
            filepath = os.path.join(self.DATA_CACHE_DIR, 'user_preferences.json')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        user_prefs = st.session_state.get('user_preferences', {})
        
        try:
            with open(filepath, 'w') as f:
                json.dump(user_prefs, f, indent=2)
            self.logger.info(f"Saved user preferences to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save user preferences: {e}")
    
    def load_user_preferences_from_file(self, filepath: Optional[str] = None):
        """Load user preferences from a JSON file"""
        if filepath is None:
            filepath = os.path.join(self.DATA_CACHE_DIR, 'user_preferences.json')
        
        if not os.path.exists(filepath):
            self.logger.info(f"No user preferences file found at {filepath}")
            return
        
        try:
            with open(filepath, 'r') as f:
                user_prefs = json.load(f)
            
            st.session_state['user_preferences'] = user_prefs
            self.logger.info(f"Loaded user preferences from {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to load user preferences: {e}")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.LOG_FILE) if os.path.dirname(self.LOG_FILE) else 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.LOG_FILE),
                logging.StreamHandler()  # Also log to console
            ]
        )
        
        # Set specific logger levels
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        
        self.logger.info(f"Logging configured - Level: {self.LOG_LEVEL}, File: {self.LOG_FILE}")
    
    def create_directories(self):
        """Create necessary directories for the application"""
        directories = [
            self.MODEL_CACHE_DIR,
            self.DATA_CACHE_DIR,
            'logs'
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                self.logger.debug(f"Created/verified directory: {directory}")
            except Exception as e:
                self.logger.error(f"Failed to create directory {directory}: {e}")
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get caching configuration"""
        return {
            'ttl_seconds': self.CACHE_TTL_SECONDS,
            'max_size_mb': self.MAX_CACHE_SIZE_MB,
            'model_cache_dir': self.MODEL_CACHE_DIR,
            'data_cache_dir': self.DATA_CACHE_DIR
        }
    
    def is_development_mode(self) -> bool:
        """Check if running in development mode"""
        return self.DEBUG_MODE or os.getenv('STREAMLIT_ENV') == 'development'
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information for debugging"""
        return {
            'app_name': self.APP_NAME,
            'app_version': self.APP_VERSION,
            'debug_mode': self.DEBUG_MODE,
            'python_version': os.sys.version,
            'streamlit_version': st.__version__,
            'config_source': 'environment_variables',
            'feature_flags': self.get_feature_flags()
        }

# Global configuration instance
config = Config()

# Convenience functions
def get_config() -> Config:
    """Get the global configuration instance"""
    return config

def setup_app_environment():
    """Setup the application environment"""
    config.setup_logging()
    config.create_directories()
    config.load_user_preferences_from_file()
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    logger.info(f"Environment: {'Development' if config.is_development_mode() else 'Production'}")
    logger.debug(f"Configuration: {config.get_environment_info()}")

def validate_spotify_credentials() -> bool:
    """Validate that Spotify credentials are configured"""
    spotify_config = config.get_spotify_config()
    return bool(spotify_config['client_id'] and spotify_config['client_secret'])