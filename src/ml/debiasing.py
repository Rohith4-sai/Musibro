import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Set
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from collections import defaultdict, Counter
import logging
from datetime import datetime, timedelta

class PopularityDebiaser:
    """Removes popularity bias from recommendations"""
    
    def __init__(self, debiasing_strength: float = 0.5):
        self.debiasing_strength = debiasing_strength  # 0 = no debiasing, 1 = full debiasing
        self.popularity_stats = {}
        self.logger = logging.getLogger(__name__)
    
    def fit(self, tracks_df: pd.DataFrame, popularity_col: str = 'popularity'):
        """Learn popularity distribution for debiasing"""
        try:
            self.popularity_stats = {
                'mean': tracks_df[popularity_col].mean(),
                'std': tracks_df[popularity_col].std(),
                'min': tracks_df[popularity_col].min(),
                'max': tracks_df[popularity_col].max(),
                'percentiles': {
                    25: tracks_df[popularity_col].quantile(0.25),
                    50: tracks_df[popularity_col].quantile(0.50),
                    75: tracks_df[popularity_col].quantile(0.75),
                    90: tracks_df[popularity_col].quantile(0.90)
                }
            }
            return self
        except Exception as e:
            self.logger.error(f"Failed to fit popularity debiaser: {e}")
            return self
    
    def debias_scores(self, recommendations: List[Dict], track_metadata: Dict[str, Dict]) -> List[Dict]:
        """Apply popularity debiasing to recommendation scores"""
        try:
            debiased_recommendations = []
            
            for rec in recommendations:
                item_id = rec['item_id']
                original_score = rec['score']
                
                # Get track popularity
                track_info = track_metadata.get(item_id, {})
                popularity = track_info.get('popularity', self.popularity_stats['mean'])
                
                # Calculate popularity penalty
                popularity_penalty = self._calculate_popularity_penalty(popularity)
                
                # Apply debiasing
                debiased_score = original_score * (1 - self.debiasing_strength * popularity_penalty)
                
                debiased_rec = rec.copy()
                debiased_rec['score'] = debiased_score
                debiased_rec['original_score'] = original_score
                debiased_rec['popularity_penalty'] = popularity_penalty
                
                debiased_recommendations.append(debiased_rec)
            
            # Re-sort by debiased scores
            debiased_recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            return debiased_recommendations
        except Exception as e:
            self.logger.error(f"Failed to debias scores: {e}")
            return recommendations
    
    def _calculate_popularity_penalty(self, popularity: float) -> float:
        """Calculate penalty based on popularity"""
        try:
            # Normalize popularity to 0-1 scale
            pop_range = self.popularity_stats['max'] - self.popularity_stats['min']
            if pop_range > 0:
                normalized_pop = (popularity - self.popularity_stats['min']) / pop_range
            else:
                normalized_pop = 0.5
            
            # Higher popularity = higher penalty
            # Use sigmoid function for smooth penalty curve
            penalty = 1 / (1 + np.exp(-10 * (normalized_pop - 0.5)))
            
            return penalty
        except Exception as e:
            self.logger.error(f"Failed to calculate popularity penalty: {e}")
            return 0.0
    
    def get_popularity_distribution_stats(self) -> Dict:
        """Get popularity distribution statistics"""
        return self.popularity_stats.copy()

class FairnessConstraintEnforcer:
    """Ensures fair representation across different artist groups"""
    
    def __init__(self, min_niche_ratio: float = 0.3, min_diverse_genres: int = 3):
        self.min_niche_ratio = min_niche_ratio  # Minimum ratio of niche artists
        self.min_diverse_genres = min_diverse_genres  # Minimum number of different genres
        self.artist_stats = {}
        self.genre_stats = {}
        self.logger = logging.getLogger(__name__)
    
    def fit(self, tracks_df: pd.DataFrame, artist_metadata: Dict[str, Dict]):
        """Learn artist and genre distributions"""
        try:
            # Analyze artist popularity distribution
            artist_popularity = {}
            artist_genres = {}
            
            for _, track in tracks_df.iterrows():
                artist_id = track.get('artist_id')
                if artist_id and artist_id in artist_metadata:
                    artist_info = artist_metadata[artist_id]
                    artist_popularity[artist_id] = artist_info.get('popularity', 0)
                    artist_genres[artist_id] = artist_info.get('genres', [])
            
            # Categorize artists by popularity
            self.artist_stats = {
                'niche': [aid for aid, pop in artist_popularity.items() if pop < 30],
                'emerging': [aid for aid, pop in artist_popularity.items() if 30 <= pop < 60],
                'established': [aid for aid, pop in artist_popularity.items() if 60 <= pop < 80],
                'mainstream': [aid for aid, pop in artist_popularity.items() if pop >= 80]
            }
            
            # Analyze genre distribution
            all_genres = []
            for genres in artist_genres.values():
                all_genres.extend(genres)
            
            self.genre_stats = {
                'genre_counts': Counter(all_genres),
                'total_genres': len(set(all_genres)),
                'artist_genres': artist_genres
            }
            
            return self
        except Exception as e:
            self.logger.error(f"Failed to fit fairness enforcer: {e}")
            return self
    
    def enforce_fairness(self, recommendations: List[Dict], track_metadata: Dict[str, Dict],
                        artist_metadata: Dict[str, Dict]) -> List[Dict]:
        """Enforce fairness constraints on recommendations"""
        try:
            # Analyze current recommendations
            current_artists = []
            current_genres = set()
            
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                artist_id = track_info.get('artist_id')
                
                if artist_id:
                    current_artists.append(artist_id)
                    artist_info = artist_metadata.get(artist_id, {})
                    current_genres.update(artist_info.get('genres', []))
            
            # Check fairness violations
            violations = self._check_fairness_violations(current_artists, current_genres)
            
            if violations:
                # Apply corrections
                corrected_recommendations = self._apply_fairness_corrections(
                    recommendations, violations, track_metadata, artist_metadata
                )
                return corrected_recommendations
            
            return recommendations
        except Exception as e:
            self.logger.error(f"Failed to enforce fairness: {e}")
            return recommendations
    
    def _check_fairness_violations(self, current_artists: List[str], current_genres: Set[str]) -> Dict:
        """Check for fairness violations"""
        violations = {}
        
        # Check niche artist representation
        niche_artists = set(current_artists) & set(self.artist_stats.get('niche', []))
        niche_ratio = len(niche_artists) / len(current_artists) if current_artists else 0
        
        if niche_ratio < self.min_niche_ratio:
            violations['insufficient_niche'] = {
                'current_ratio': niche_ratio,
                'required_ratio': self.min_niche_ratio,
                'deficit': self.min_niche_ratio - niche_ratio
            }
        
        # Check genre diversity
        if len(current_genres) < self.min_diverse_genres:
            violations['insufficient_genre_diversity'] = {
                'current_genres': len(current_genres),
                'required_genres': self.min_diverse_genres,
                'deficit': self.min_diverse_genres - len(current_genres)
            }
        
        return violations
    
    def _apply_fairness_corrections(self, recommendations: List[Dict], violations: Dict,
                                   track_metadata: Dict[str, Dict], artist_metadata: Dict[str, Dict]) -> List[Dict]:
        """Apply corrections to address fairness violations"""
        try:
            corrected_recommendations = recommendations.copy()
            
            # Handle insufficient niche representation
            if 'insufficient_niche' in violations:
                deficit = violations['insufficient_niche']['deficit']
                items_to_replace = int(len(recommendations) * deficit)
                
                # Find mainstream items to replace
                mainstream_indices = []
                for i, rec in enumerate(corrected_recommendations):
                    track_info = track_metadata.get(rec['item_id'], {})
                    artist_id = track_info.get('artist_id')
                    if artist_id in self.artist_stats.get('mainstream', []):
                        mainstream_indices.append(i)
                
                # Replace with niche items (this would require a candidate pool in practice)
                # For now, we'll mark items for replacement
                for i in mainstream_indices[:items_to_replace]:
                    corrected_recommendations[i]['needs_niche_replacement'] = True
            
            # Handle insufficient genre diversity
            if 'insufficient_genre_diversity' in violations:
                # Similar logic for genre diversity
                pass
            
            return corrected_recommendations
        except Exception as e:
            self.logger.error(f"Failed to apply fairness corrections: {e}")
            return recommendations
    
    def get_fairness_metrics(self, recommendations: List[Dict], track_metadata: Dict[str, Dict],
                           artist_metadata: Dict[str, Dict]) -> Dict:
        """Calculate fairness metrics for recommendations"""
        try:
            metrics = {}
            
            # Artist diversity metrics
            artists = []
            genres = set()
            popularity_scores = []
            
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                artist_id = track_info.get('artist_id')
                
                if artist_id:
                    artists.append(artist_id)
                    artist_info = artist_metadata.get(artist_id, {})
                    genres.update(artist_info.get('genres', []))
                    popularity_scores.append(artist_info.get('popularity', 0))
            
            # Calculate metrics
            unique_artists = len(set(artists))
            artist_diversity = unique_artists / len(artists) if artists else 0
            
            niche_artists = len([a for a in artists if a in self.artist_stats.get('niche', [])])
            niche_ratio = niche_artists / len(artists) if artists else 0
            
            metrics = {
                'artist_diversity': artist_diversity,
                'unique_artists': unique_artists,
                'total_recommendations': len(recommendations),
                'genre_diversity': len(genres),
                'niche_artist_ratio': niche_ratio,
                'avg_artist_popularity': np.mean(popularity_scores) if popularity_scores else 0,
                'popularity_std': np.std(popularity_scores) if popularity_scores else 0
            }
            
            return metrics
        except Exception as e:
            self.logger.error(f"Failed to calculate fairness metrics: {e}")
            return {}

class DiversityInjector:
    """Injects diversity into recommendations to break filter bubbles"""
    
    def __init__(self, diversity_strength: float = 0.3, novelty_weight: float = 0.4):
        self.diversity_strength = diversity_strength
        self.novelty_weight = novelty_weight
        self.user_profiles = {}
        self.global_stats = {}
        self.logger = logging.getLogger(__name__)
    
    def fit(self, user_interactions: Dict[str, List[Dict]], track_metadata: Dict[str, Dict]):
        """Learn user profiles and global statistics for diversity injection"""
        try:
            # Build user profiles
            for user_id, interactions in user_interactions.items():
                self.user_profiles[user_id] = self._build_user_profile(interactions, track_metadata)
            
            # Calculate global statistics
            all_tracks = list(track_metadata.values())
            self.global_stats = {
                'avg_popularity': np.mean([t.get('popularity', 0) for t in all_tracks]),
                'popularity_std': np.std([t.get('popularity', 0) for t in all_tracks]),
                'genre_distribution': self._calculate_genre_distribution(all_tracks)
            }
            
            return self
        except Exception as e:
            self.logger.error(f"Failed to fit diversity injector: {e}")
            return self
    
    def inject_diversity(self, user_id: str, recommendations: List[Dict], 
                        candidate_pool: List[Dict], track_metadata: Dict[str, Dict]) -> List[Dict]:
        """Inject diversity into recommendations"""
        try:
            if user_id not in self.user_profiles:
                return recommendations
            
            user_profile = self.user_profiles[user_id]
            
            # Calculate diversity scores for candidates
            diversity_candidates = []
            recommended_ids = {rec['item_id'] for rec in recommendations}
            
            for candidate in candidate_pool:
                if candidate['item_id'] not in recommended_ids:
                    diversity_score = self._calculate_diversity_score(
                        candidate, user_profile, track_metadata
                    )
                    candidate_with_diversity = candidate.copy()
                    candidate_with_diversity['diversity_score'] = diversity_score
                    diversity_candidates.append(candidate_with_diversity)
            
            # Sort candidates by diversity score
            diversity_candidates.sort(key=lambda x: x['diversity_score'], reverse=True)
            
            # Replace some recommendations with diverse candidates
            n_replacements = int(len(recommendations) * self.diversity_strength)
            
            # Replace lowest-scoring recommendations with highest-diversity candidates
            recommendations.sort(key=lambda x: x['score'])
            
            diverse_recommendations = recommendations[n_replacements:]
            diverse_recommendations.extend(diversity_candidates[:n_replacements])
            
            # Re-sort by combined score
            for rec in diverse_recommendations:
                if 'diversity_score' in rec:
                    rec['combined_score'] = rec['score'] + rec['diversity_score'] * self.diversity_strength
                else:
                    rec['combined_score'] = rec['score']
            
            diverse_recommendations.sort(key=lambda x: x['combined_score'], reverse=True)
            
            return diverse_recommendations
        except Exception as e:
            self.logger.error(f"Failed to inject diversity: {e}")
            return recommendations
    
    def _build_user_profile(self, interactions: List[Dict], track_metadata: Dict[str, Dict]) -> Dict:
        """Build user profile from interactions"""
        try:
            genres = []
            popularity_scores = []
            audio_features = defaultdict(list)
            
            for interaction in interactions:
                track_id = interaction.get('item_id')
                track_info = track_metadata.get(track_id, {})
                
                # Collect genres
                track_genres = track_info.get('genres', [])
                genres.extend(track_genres)
                
                # Collect popularity
                popularity = track_info.get('popularity', 0)
                popularity_scores.append(popularity)
                
                # Collect audio features
                for feature in ['danceability', 'energy', 'valence', 'acousticness']:
                    if feature in track_info:
                        audio_features[feature].append(track_info[feature])
            
            # Build profile
            profile = {
                'preferred_genres': Counter(genres),
                'avg_popularity': np.mean(popularity_scores) if popularity_scores else 0,
                'popularity_variance': np.var(popularity_scores) if popularity_scores else 0,
                'audio_preferences': {
                    feature: {
                        'mean': np.mean(values),
                        'std': np.std(values)
                    } for feature, values in audio_features.items() if values
                }
            }
            
            return profile
        except Exception as e:
            self.logger.error(f"Failed to build user profile: {e}")
            return {}
    
    def _calculate_diversity_score(self, candidate: Dict, user_profile: Dict, 
                                  track_metadata: Dict[str, Dict]) -> float:
        """Calculate diversity score for a candidate track"""
        try:
            track_info = track_metadata.get(candidate['item_id'], {})
            diversity_score = 0.0
            
            # Genre diversity
            track_genres = set(track_info.get('genres', []))
            user_genres = set(user_profile.get('preferred_genres', {}).keys())
            
            if track_genres and user_genres:
                genre_overlap = len(track_genres & user_genres) / len(track_genres | user_genres)
                genre_diversity = 1 - genre_overlap  # Higher score for less overlap
                diversity_score += genre_diversity * 0.4
            
            # Popularity diversity
            track_popularity = track_info.get('popularity', 0)
            user_avg_popularity = user_profile.get('avg_popularity', 0)
            
            popularity_diff = abs(track_popularity - user_avg_popularity) / 100
            diversity_score += popularity_diff * 0.3
            
            # Audio feature diversity
            audio_diversity = 0.0
            audio_count = 0
            
            for feature in ['danceability', 'energy', 'valence', 'acousticness']:
                if feature in track_info and feature in user_profile.get('audio_preferences', {}):
                    track_value = track_info[feature]
                    user_mean = user_profile['audio_preferences'][feature]['mean']
                    
                    feature_diff = abs(track_value - user_mean)
                    audio_diversity += feature_diff
                    audio_count += 1
            
            if audio_count > 0:
                audio_diversity /= audio_count
                diversity_score += audio_diversity * 0.3
            
            return diversity_score
        except Exception as e:
            self.logger.error(f"Failed to calculate diversity score: {e}")
            return 0.0
    
    def _calculate_genre_distribution(self, tracks: List[Dict]) -> Dict:
        """Calculate global genre distribution"""
        try:
            all_genres = []
            for track in tracks:
                genres = track.get('genres', [])
                all_genres.extend(genres)
            
            genre_counts = Counter(all_genres)
            total_genres = sum(genre_counts.values())
            
            genre_distribution = {
                genre: count / total_genres
                for genre, count in genre_counts.items()
            }
            
            return genre_distribution
        except Exception as e:
            self.logger.error(f"Failed to calculate genre distribution: {e}")
            return {}
    
    def calculate_diversity_scores(self, item_ids: List[str]) -> Dict[str, float]:
        """Calculate diversity scores for a list of items"""
        try:
            # This is a simplified version - in practice would use more sophisticated metrics
            diversity_scores = {}
            
            for item_id in item_ids:
                # Simple diversity score based on item ID hash (for demo)
                # In practice, this would use actual track features
                hash_value = hash(item_id) % 1000
                diversity_score = hash_value / 1000.0
                diversity_scores[item_id] = diversity_score
            
            return diversity_scores
        except Exception as e:
            self.logger.error(f"Failed to calculate diversity scores: {e}")
            return {}

class AdversarialDebiaser:
    """Adversarial training approach for bias reduction"""
    
    def __init__(self, lambda_fairness: float = 0.1):
        self.lambda_fairness = lambda_fairness
        self.bias_detector = None
        self.logger = logging.getLogger(__name__)
    
    def train_bias_detector(self, recommendations_history: List[Dict], 
                           protected_attributes: List[str]):
        """Train a bias detector using adversarial approach"""
        try:
            # This is a simplified implementation
            # In practice, would use more sophisticated adversarial training
            
            # For now, we'll use a simple classifier to detect bias patterns
            from sklearn.ensemble import RandomForestClassifier
            
            # Prepare training data (simplified)
            X = []
            y = []
            
            for rec_session in recommendations_history:
                # Extract features from recommendation session
                session_features = self._extract_session_features(rec_session)
                X.append(session_features)
                
                # Label as biased if it violates fairness constraints
                is_biased = self._detect_bias_in_session(rec_session, protected_attributes)
                y.append(1 if is_biased else 0)
            
            # Train bias detector
            self.bias_detector = RandomForestClassifier(n_estimators=100, random_state=42)
            self.bias_detector.fit(X, y)
            
            return self
        except Exception as e:
            self.logger.error(f"Failed to train bias detector: {e}")
            return self
    
    def _extract_session_features(self, rec_session: Dict) -> List[float]:
        """Extract features from a recommendation session"""
        try:
            # Extract various bias-related features
            features = []
            
            recommendations = rec_session.get('recommendations', [])
            
            # Popularity distribution features
            popularities = [rec.get('popularity', 0) for rec in recommendations]
            features.extend([
                np.mean(popularities),
                np.std(popularities),
                np.min(popularities),
                np.max(popularities)
            ])
            
            # Genre diversity features
            all_genres = set()
            for rec in recommendations:
                genres = rec.get('genres', [])
                all_genres.update(genres)
            
            features.append(len(all_genres))  # Genre diversity
            
            # Artist diversity features
            unique_artists = len(set(rec.get('artist_id') for rec in recommendations))
            features.append(unique_artists / len(recommendations) if recommendations else 0)
            
            return features
        except Exception as e:
            self.logger.error(f"Failed to extract session features: {e}")
            return [0.0] * 6  # Return default features
    
    def _detect_bias_in_session(self, rec_session: Dict, protected_attributes: List[str]) -> bool:
        """Detect if a recommendation session exhibits bias"""
        try:
            recommendations = rec_session.get('recommendations', [])
            
            # Check for popularity bias
            popularities = [rec.get('popularity', 0) for rec in recommendations]
            avg_popularity = np.mean(popularities) if popularities else 0
            
            if avg_popularity > 75:  # Too mainstream
                return True
            
            # Check for lack of diversity
            unique_artists = len(set(rec.get('artist_id') for rec in recommendations))
            artist_diversity = unique_artists / len(recommendations) if recommendations else 0
            
            if artist_diversity < 0.7:  # Too little artist diversity
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Failed to detect bias in session: {e}")
            return False
    
    def apply_adversarial_debiasing(self, recommendations: List[Dict]) -> List[Dict]:
        """Apply adversarial debiasing to recommendations"""
        try:
            if self.bias_detector is None:
                return recommendations
            
            # Create session representation
            session = {'recommendations': recommendations}
            session_features = [self._extract_session_features(session)]
            
            # Predict bias probability
            bias_probability = self.bias_detector.predict_proba(session_features)[0][1]
            
            # If high bias probability, apply corrections
            if bias_probability > 0.7:
                # Apply bias reduction techniques
                corrected_recommendations = self._apply_bias_corrections(recommendations)
                return corrected_recommendations
            
            return recommendations
        except Exception as e:
            self.logger.error(f"Failed to apply adversarial debiasing: {e}")
            return recommendations
    
    def _apply_bias_corrections(self, recommendations: List[Dict]) -> List[Dict]:
        """Apply bias corrections to recommendations"""
        try:
            # Sort by popularity and replace some high-popularity items
            recommendations.sort(key=lambda x: x.get('popularity', 0), reverse=True)
            
            # Replace top 30% most popular items with lower-popularity alternatives
            n_replace = int(len(recommendations) * 0.3)
            
            # Mark items for replacement (in practice, would use candidate pool)
            for i in range(n_replace):
                recommendations[i]['needs_bias_correction'] = True
                # Reduce score to deprioritize
                recommendations[i]['score'] *= 0.7
            
            # Re-sort by adjusted scores
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            return recommendations
        except Exception as e:
            self.logger.error(f"Failed to apply bias corrections: {e}")
            return recommendations