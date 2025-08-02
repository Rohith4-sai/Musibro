import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Set
from collections import Counter, defaultdict
from sklearn.metrics import precision_score, recall_score, f1_score, ndcg_score
from sklearn.metrics.pairwise import cosine_similarity
import logging
from datetime import datetime, timedelta
import math

class RecommendationEvaluator:
    """Comprehensive evaluation of recommendation systems with bias-aware metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.evaluation_history = []
    
    def evaluate_recommendations(self, recommendations: List[Dict], ground_truth: List[Dict],
                               track_metadata: Dict[str, Dict], user_profile: Dict = None) -> Dict:
        """Comprehensive evaluation of recommendations"""
        try:
            evaluation_results = {}
            
            # Traditional accuracy metrics
            accuracy_metrics = self._calculate_accuracy_metrics(recommendations, ground_truth)
            evaluation_results['accuracy'] = accuracy_metrics
            
            # Diversity metrics
            diversity_metrics = self._calculate_diversity_metrics(recommendations, track_metadata)
            evaluation_results['diversity'] = diversity_metrics
            
            # Novelty metrics
            novelty_metrics = self._calculate_novelty_metrics(recommendations, track_metadata)
            evaluation_results['novelty'] = novelty_metrics
            
            # Coverage metrics
            coverage_metrics = self._calculate_coverage_metrics(recommendations, track_metadata)
            evaluation_results['coverage'] = coverage_metrics
            
            # Bias metrics
            bias_metrics = self._calculate_bias_metrics(recommendations, track_metadata)
            evaluation_results['bias'] = bias_metrics
            
            # Serendipity metrics
            if user_profile:
                serendipity_metrics = self._calculate_serendipity_metrics(
                    recommendations, track_metadata, user_profile
                )
                evaluation_results['serendipity'] = serendipity_metrics
            
            # Overall quality score
            overall_score = self._calculate_overall_quality_score(evaluation_results)
            evaluation_results['overall_quality'] = overall_score
            
            # Store evaluation
            evaluation_results['timestamp'] = datetime.now().isoformat()
            self.evaluation_history.append(evaluation_results)
            
            return evaluation_results
        except Exception as e:
            self.logger.error(f"Failed to evaluate recommendations: {e}")
            return {}
    
    def _calculate_accuracy_metrics(self, recommendations: List[Dict], ground_truth: List[Dict]) -> Dict:
        """Calculate traditional accuracy metrics"""
        try:
            if not ground_truth:
                return {'precision': 0, 'recall': 0, 'f1': 0, 'ndcg': 0}
            
            # Convert to sets for easier comparison
            recommended_ids = {rec['item_id'] for rec in recommendations}
            ground_truth_ids = {gt['item_id'] for gt in ground_truth}
            
            # Calculate precision and recall
            true_positives = len(recommended_ids & ground_truth_ids)
            precision = true_positives / len(recommended_ids) if recommended_ids else 0
            recall = true_positives / len(ground_truth_ids) if ground_truth_ids else 0
            
            # F1 score
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            # NDCG calculation (simplified)
            ndcg = self._calculate_ndcg(recommendations, ground_truth)
            
            return {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'ndcg': ndcg,
                'true_positives': true_positives,
                'recommended_count': len(recommended_ids),
                'ground_truth_count': len(ground_truth_ids)
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate accuracy metrics: {e}")
            return {}
    
    def _calculate_ndcg(self, recommendations: List[Dict], ground_truth: List[Dict], k: int = 10) -> float:
        """Calculate Normalized Discounted Cumulative Gain"""
        try:
            # Create relevance scores
            ground_truth_ids = {gt['item_id']: gt.get('rating', 1) for gt in ground_truth}
            
            # Calculate DCG
            dcg = 0.0
            for i, rec in enumerate(recommendations[:k]):
                relevance = ground_truth_ids.get(rec['item_id'], 0)
                if relevance > 0:
                    dcg += relevance / math.log2(i + 2)  # i+2 because log2(1) = 0
            
            # Calculate IDCG (Ideal DCG)
            ideal_relevances = sorted(ground_truth_ids.values(), reverse=True)[:k]
            idcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(ideal_relevances))
            
            # NDCG
            ndcg = dcg / idcg if idcg > 0 else 0
            
            return ndcg
        except Exception as e:
            self.logger.error(f"Failed to calculate NDCG: {e}")
            return 0.0
    
    def _calculate_diversity_metrics(self, recommendations: List[Dict], track_metadata: Dict[str, Dict]) -> Dict:
        """Calculate diversity metrics"""
        try:
            # Intra-list diversity (ILD)
            ild = self._calculate_intra_list_diversity(recommendations, track_metadata)
            
            # Genre diversity
            genre_diversity = self._calculate_genre_diversity(recommendations, track_metadata)
            
            # Artist diversity
            artist_diversity = self._calculate_artist_diversity(recommendations, track_metadata)
            
            # Popularity diversity
            popularity_diversity = self._calculate_popularity_diversity(recommendations, track_metadata)
            
            # Temporal diversity
            temporal_diversity = self._calculate_temporal_diversity(recommendations, track_metadata)
            
            return {
                'intra_list_diversity': ild,
                'genre_diversity': genre_diversity,
                'artist_diversity': artist_diversity,
                'popularity_diversity': popularity_diversity,
                'temporal_diversity': temporal_diversity
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate diversity metrics: {e}")
            return {}
    
    def _calculate_intra_list_diversity(self, recommendations: List[Dict], track_metadata: Dict[str, Dict]) -> float:
        """Calculate intra-list diversity using audio features"""
        try:
            audio_features = ['danceability', 'energy', 'valence', 'acousticness', 'instrumentalness']
            
            # Extract feature vectors
            feature_vectors = []
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                vector = [track_info.get(feature, 0.5) for feature in audio_features]
                feature_vectors.append(vector)
            
            if len(feature_vectors) < 2:
                return 0.0
            
            # Calculate pairwise similarities
            similarities = []
            for i in range(len(feature_vectors)):
                for j in range(i + 1, len(feature_vectors)):
                    similarity = cosine_similarity([feature_vectors[i]], [feature_vectors[j]])[0][0]
                    similarities.append(similarity)
            
            # Diversity is 1 - average similarity
            avg_similarity = np.mean(similarities) if similarities else 0
            diversity = 1 - avg_similarity
            
            return diversity
        except Exception as e:
            self.logger.error(f"Failed to calculate intra-list diversity: {e}")
            return 0.0
    
    def _calculate_genre_diversity(self, recommendations: List[Dict], track_metadata: Dict[str, Dict]) -> Dict:
        """Calculate genre diversity metrics"""
        try:
            all_genres = set()
            genre_counts = Counter()
            
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                genres = track_info.get('genres', [])
                all_genres.update(genres)
                genre_counts.update(genres)
            
            # Number of unique genres
            unique_genres = len(all_genres)
            
            # Genre entropy (Shannon entropy)
            total_genre_mentions = sum(genre_counts.values())
            if total_genre_mentions > 0:
                genre_entropy = -sum(
                    (count / total_genre_mentions) * math.log2(count / total_genre_mentions)
                    for count in genre_counts.values()
                )
            else:
                genre_entropy = 0
            
            # Genre balance (how evenly distributed genres are)
            if unique_genres > 1:
                max_entropy = math.log2(unique_genres)
                genre_balance = genre_entropy / max_entropy
            else:
                genre_balance = 0
            
            return {
                'unique_genres': unique_genres,
                'genre_entropy': genre_entropy,
                'genre_balance': genre_balance,
                'genre_distribution': dict(genre_counts)
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate genre diversity: {e}")
            return {}
    
    def _calculate_artist_diversity(self, recommendations: List[Dict], track_metadata: Dict[str, Dict]) -> Dict:
        """Calculate artist diversity metrics"""
        try:
            artists = []
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                artist = track_info.get('artist', 'Unknown')
                artists.append(artist)
            
            unique_artists = len(set(artists))
            total_tracks = len(artists)
            
            # Artist diversity ratio
            artist_diversity_ratio = unique_artists / total_tracks if total_tracks > 0 else 0
            
            # Artist concentration (Gini coefficient)
            artist_counts = Counter(artists)
            gini_coefficient = self._calculate_gini_coefficient(list(artist_counts.values()))
            
            return {
                'unique_artists': unique_artists,
                'total_tracks': total_tracks,
                'artist_diversity_ratio': artist_diversity_ratio,
                'artist_concentration_gini': gini_coefficient
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate artist diversity: {e}")
            return {}
    
    def _calculate_popularity_diversity(self, recommendations: List[Dict], track_metadata: Dict[str, Dict]) -> Dict:
        """Calculate popularity diversity metrics"""
        try:
            popularities = []
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                popularity = track_info.get('popularity', 0)
                popularities.append(popularity)
            
            if not popularities:
                return {}
            
            # Basic statistics
            mean_popularity = np.mean(popularities)
            std_popularity = np.std(popularities)
            min_popularity = np.min(popularities)
            max_popularity = np.max(popularities)
            
            # Popularity range
            popularity_range = max_popularity - min_popularity
            
            # Coefficient of variation
            cv = std_popularity / mean_popularity if mean_popularity > 0 else 0
            
            # Niche ratio (tracks with popularity < 30)
            niche_count = sum(1 for p in popularities if p < 30)
            niche_ratio = niche_count / len(popularities)
            
            # Mainstream ratio (tracks with popularity > 70)
            mainstream_count = sum(1 for p in popularities if p > 70)
            mainstream_ratio = mainstream_count / len(popularities)
            
            return {
                'mean_popularity': mean_popularity,
                'std_popularity': std_popularity,
                'min_popularity': min_popularity,
                'max_popularity': max_popularity,
                'popularity_range': popularity_range,
                'coefficient_of_variation': cv,
                'niche_ratio': niche_ratio,
                'mainstream_ratio': mainstream_ratio
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate popularity diversity: {e}")
            return {}
    
    def _calculate_temporal_diversity(self, recommendations: List[Dict], track_metadata: Dict[str, Dict]) -> Dict:
        """Calculate temporal diversity metrics"""
        try:
            release_years = []
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                release_date = track_info.get('release_date')
                if release_date:
                    try:
                        if isinstance(release_date, str):
                            year = pd.to_datetime(release_date).year
                        else:
                            year = release_date.year
                        release_years.append(year)
                    except:
                        continue
            
            if not release_years:
                return {}
            
            # Basic statistics
            mean_year = np.mean(release_years)
            std_year = np.std(release_years)
            min_year = np.min(release_years)
            max_year = np.max(release_years)
            
            # Year range
            year_range = max_year - min_year
            
            # Recent music ratio (last 3 years)
            current_year = datetime.now().year
            recent_count = sum(1 for year in release_years if year >= current_year - 3)
            recent_ratio = recent_count / len(release_years)
            
            # Vintage music ratio (older than 10 years)
            vintage_count = sum(1 for year in release_years if year < current_year - 10)
            vintage_ratio = vintage_count / len(release_years)
            
            return {
                'mean_release_year': mean_year,
                'std_release_year': std_year,
                'min_release_year': min_year,
                'max_release_year': max_year,
                'year_range': year_range,
                'recent_music_ratio': recent_ratio,
                'vintage_music_ratio': vintage_ratio
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate temporal diversity: {e}")
            return {}
    
    def _calculate_novelty_metrics(self, recommendations: List[Dict], track_metadata: Dict[str, Dict]) -> Dict:
        """Calculate novelty metrics"""
        try:
            # Artist novelty (how many new artists)
            artists = set()
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                artist = track_info.get('artist')
                if artist:
                    artists.add(artist)
            
            # Track novelty based on popularity
            novelty_scores = []
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                popularity = track_info.get('popularity', 0)
                # Novelty is inverse of popularity
                novelty = (100 - popularity) / 100
                novelty_scores.append(novelty)
            
            avg_novelty = np.mean(novelty_scores) if novelty_scores else 0
            
            # Release date novelty
            current_year = datetime.now().year
            release_novelty_scores = []
            
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                release_date = track_info.get('release_date')
                if release_date:
                    try:
                        if isinstance(release_date, str):
                            year = pd.to_datetime(release_date).year
                        else:
                            year = release_date.year
                        
                        # More recent = more novel
                        years_old = current_year - year
                        novelty = max(0, 1 - years_old / 50)  # Normalize by 50 years
                        release_novelty_scores.append(novelty)
                    except:
                        release_novelty_scores.append(0.5)  # Default novelty
            
            avg_release_novelty = np.mean(release_novelty_scores) if release_novelty_scores else 0
            
            return {
                'unique_artists': len(artists),
                'avg_popularity_novelty': avg_novelty,
                'avg_release_novelty': avg_release_novelty,
                'combined_novelty': (avg_novelty + avg_release_novelty) / 2
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate novelty metrics: {e}")
            return {}
    
    def _calculate_coverage_metrics(self, recommendations: List[Dict], track_metadata: Dict[str, Dict]) -> Dict:
        """Calculate coverage metrics"""
        try:
            # Genre coverage
            all_possible_genres = set()
            recommended_genres = set()
            
            for track_info in track_metadata.values():
                genres = track_info.get('genres', [])
                all_possible_genres.update(genres)
            
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                genres = track_info.get('genres', [])
                recommended_genres.update(genres)
            
            genre_coverage = len(recommended_genres) / len(all_possible_genres) if all_possible_genres else 0
            
            # Popularity tier coverage
            popularity_tiers = {'niche': 0, 'emerging': 0, 'popular': 0, 'mainstream': 0}
            
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                popularity = track_info.get('popularity', 0)
                
                if popularity < 30:
                    popularity_tiers['niche'] += 1
                elif popularity < 60:
                    popularity_tiers['emerging'] += 1
                elif popularity < 80:
                    popularity_tiers['popular'] += 1
                else:
                    popularity_tiers['mainstream'] += 1
            
            # Normalize by total recommendations
            total_recs = len(recommendations)
            if total_recs > 0:
                for tier in popularity_tiers:
                    popularity_tiers[tier] /= total_recs
            
            return {
                'genre_coverage': genre_coverage,
                'covered_genres': len(recommended_genres),
                'total_possible_genres': len(all_possible_genres),
                'popularity_tier_coverage': popularity_tiers
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate coverage metrics: {e}")
            return {}
    
    def _calculate_bias_metrics(self, recommendations: List[Dict], track_metadata: Dict[str, Dict]) -> Dict:
        """Calculate bias-related metrics"""
        try:
            # Popularity bias
            popularities = []
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                popularity = track_info.get('popularity', 0)
                popularities.append(popularity)
            
            avg_popularity = np.mean(popularities) if popularities else 0
            
            # Popularity bias score (higher = more biased toward popular items)
            popularity_bias = avg_popularity / 100
            
            # Artist concentration bias (Gini coefficient)
            artists = []
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                artist = track_info.get('artist', 'Unknown')
                artists.append(artist)
            
            artist_counts = Counter(artists)
            artist_gini = self._calculate_gini_coefficient(list(artist_counts.values()))
            
            # Genre concentration bias
            all_genres = []
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                genres = track_info.get('genres', [])
                all_genres.extend(genres)
            
            genre_counts = Counter(all_genres)
            genre_gini = self._calculate_gini_coefficient(list(genre_counts.values()))
            
            return {
                'popularity_bias': popularity_bias,
                'artist_concentration_bias': artist_gini,
                'genre_concentration_bias': genre_gini,
                'overall_bias_score': (popularity_bias + artist_gini + genre_gini) / 3
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate bias metrics: {e}")
            return {}
    
    def _calculate_serendipity_metrics(self, recommendations: List[Dict], track_metadata: Dict[str, Dict],
                                     user_profile: Dict) -> Dict:
        """Calculate serendipity metrics"""
        try:
            # Serendipity = unexpectedness + relevance
            serendipity_scores = []
            
            user_genres = set(user_profile.get('preferred_genres', {}).keys())
            user_avg_popularity = user_profile.get('avg_popularity', 50)
            
            for rec in recommendations:
                track_info = track_metadata.get(rec['item_id'], {})
                
                # Unexpectedness based on genre difference
                track_genres = set(track_info.get('genres', []))
                genre_overlap = len(user_genres & track_genres) / len(user_genres | track_genres) if (user_genres | track_genres) else 0
                genre_unexpectedness = 1 - genre_overlap
                
                # Unexpectedness based on popularity difference
                track_popularity = track_info.get('popularity', 0)
                popularity_diff = abs(track_popularity - user_avg_popularity) / 100
                
                # Combined unexpectedness
                unexpectedness = (genre_unexpectedness + popularity_diff) / 2
                
                # Relevance (simplified - in practice would use more sophisticated measures)
                # For now, assume relevance is inversely related to unexpectedness
                relevance = 1 - unexpectedness * 0.5
                
                # Serendipity score
                serendipity = unexpectedness * relevance
                serendipity_scores.append(serendipity)
            
            avg_serendipity = np.mean(serendipity_scores) if serendipity_scores else 0
            
            return {
                'avg_serendipity': avg_serendipity,
                'serendipity_scores': serendipity_scores
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate serendipity metrics: {e}")
            return {}
    
    def _calculate_gini_coefficient(self, values: List[float]) -> float:
        """Calculate Gini coefficient for measuring inequality"""
        try:
            if not values or len(values) == 1:
                return 0.0
            
            # Sort values
            sorted_values = sorted(values)
            n = len(sorted_values)
            
            # Calculate Gini coefficient
            cumsum = np.cumsum(sorted_values)
            gini = (n + 1 - 2 * sum((n + 1 - i) * y for i, y in enumerate(sorted_values))) / (n * sum(sorted_values))
            
            return gini
        except Exception as e:
            self.logger.error(f"Failed to calculate Gini coefficient: {e}")
            return 0.0
    
    def _calculate_overall_quality_score(self, evaluation_results: Dict) -> Dict:
        """Calculate overall quality score combining multiple metrics"""
        try:
            # Define weights for different aspects
            weights = {
                'accuracy': 0.3,
                'diversity': 0.25,
                'novelty': 0.2,
                'coverage': 0.15,
                'bias_penalty': 0.1
            }
            
            # Extract key metrics
            accuracy_score = evaluation_results.get('accuracy', {}).get('f1', 0)
            diversity_score = evaluation_results.get('diversity', {}).get('intra_list_diversity', 0)
            novelty_score = evaluation_results.get('novelty', {}).get('combined_novelty', 0)
            coverage_score = evaluation_results.get('coverage', {}).get('genre_coverage', 0)
            bias_score = evaluation_results.get('bias', {}).get('overall_bias_score', 0)
            
            # Calculate weighted score
            quality_score = (
                accuracy_score * weights['accuracy'] +
                diversity_score * weights['diversity'] +
                novelty_score * weights['novelty'] +
                coverage_score * weights['coverage'] -
                bias_score * weights['bias_penalty']  # Bias is a penalty
            )
            
            # Normalize to 0-1 range
            quality_score = max(0, min(1, quality_score))
            
            return {
                'overall_score': quality_score,
                'component_scores': {
                    'accuracy': accuracy_score,
                    'diversity': diversity_score,
                    'novelty': novelty_score,
                    'coverage': coverage_score,
                    'bias_penalty': bias_score
                },
                'weights': weights
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate overall quality score: {e}")
            return {}
    
    def get_evaluation_summary(self, n_recent: int = 10) -> Dict:
        """Get summary of recent evaluations"""
        try:
            if not self.evaluation_history:
                return {}
            
            recent_evaluations = self.evaluation_history[-n_recent:]
            
            # Calculate trends
            quality_scores = [eval_result.get('overall_quality', {}).get('overall_score', 0) 
                            for eval_result in recent_evaluations]
            
            diversity_scores = [eval_result.get('diversity', {}).get('intra_list_diversity', 0) 
                              for eval_result in recent_evaluations]
            
            novelty_scores = [eval_result.get('novelty', {}).get('combined_novelty', 0) 
                            for eval_result in recent_evaluations]
            
            bias_scores = [eval_result.get('bias', {}).get('overall_bias_score', 0) 
                         for eval_result in recent_evaluations]
            
            summary = {
                'evaluation_count': len(recent_evaluations),
                'avg_quality_score': np.mean(quality_scores) if quality_scores else 0,
                'quality_trend': np.polyfit(range(len(quality_scores)), quality_scores, 1)[0] if len(quality_scores) > 1 else 0,
                'avg_diversity_score': np.mean(diversity_scores) if diversity_scores else 0,
                'avg_novelty_score': np.mean(novelty_scores) if novelty_scores else 0,
                'avg_bias_score': np.mean(bias_scores) if bias_scores else 0,
                'latest_evaluation': recent_evaluations[-1] if recent_evaluations else {}
            }
            
            return summary
        except Exception as e:
            self.logger.error(f"Failed to get evaluation summary: {e}")
            return {}