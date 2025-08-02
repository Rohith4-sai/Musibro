import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, LabelEncoder
import logging
import pickle
import os
from datetime import datetime

class NeuralCollaborativeFiltering:
    """Neural Collaborative Filtering using scikit-learn MLPRegressor"""
    
    def __init__(self, num_users: int, num_items: int, embedding_dim: int = 50, 
                 hidden_dims: List[int] = [128, 64, 32]):
        self.num_users = num_users
        self.num_items = num_items
        self.embedding_dim = embedding_dim
        self.hidden_dims = hidden_dims
        self.model = None
        self.user_encoder = LabelEncoder()
        self.item_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)
    
    def build_model(self):
        """Build the neural collaborative filtering model using MLPRegressor"""
        try:
            # Use MLPRegressor as a lightweight alternative to TensorFlow
            hidden_layer_sizes = tuple(self.hidden_dims)
            self.model = MLPRegressor(
                hidden_layer_sizes=hidden_layer_sizes,
                activation='relu',
                solver='adam',
                alpha=0.001,  # L2 regularization
                batch_size='auto',
                learning_rate='adaptive',
                learning_rate_init=0.001,
                max_iter=200,
                shuffle=True,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1,
                n_iter_no_change=10,
                verbose=False
            )
            
            return self.model
        except Exception as e:
            self.logger.error(f"Failed to build NCF model: {e}")
            return None
    
    def train(self, user_ids: np.ndarray, item_ids: np.ndarray, ratings: np.ndarray,
              validation_split: float = 0.2, epochs: int = 50, batch_size: int = 256):
        """Train the NCF model"""
        try:
            if self.model is None:
                self.build_model()
            
            # Encode user and item IDs
            user_ids_encoded = self.user_encoder.fit_transform(user_ids)
            item_ids_encoded = self.item_encoder.fit_transform(item_ids)
            
            # Create feature matrix
            X = np.column_stack([user_ids_encoded, item_ids_encoded])
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, ratings)
            
            return {"loss": self.model.loss_, "n_iter": self.model.n_iter_}
        except Exception as e:
            self.logger.error(f"Failed to train NCF model: {e}")
            return None
    
    def predict(self, user_ids: np.ndarray, item_ids: np.ndarray) -> np.ndarray:
        """Predict ratings for user-item pairs"""
        try:
            if self.model is None:
                raise ValueError("Model not trained")
            
            # Encode user and item IDs
            user_ids_encoded = self.user_encoder.transform(user_ids)
            item_ids_encoded = self.item_encoder.transform(item_ids)
            
            # Create feature matrix
            X = np.column_stack([user_ids_encoded, item_ids_encoded])
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Predict
            predictions = self.model.predict(X_scaled)
            return predictions
        except Exception as e:
            self.logger.error(f"Failed to predict with NCF model: {e}")
            return np.array([])

class ContentBasedFiltering:
    """Content-based filtering using audio features"""
    
    def __init__(self, similarity_metric: str = 'cosine'):
        self.similarity_metric = similarity_metric
        self.item_features = None
        self.similarity_matrix = None
        self.item_ids = None
        self.logger = logging.getLogger(__name__)
    
    def fit(self, item_features: pd.DataFrame, item_id_col: str = 'id'):
        """Fit the content-based model"""
        try:
            self.item_features = item_features.copy()
            self.item_ids = item_features[item_id_col].values
            
            # Select numeric features for similarity calculation
            numeric_features = item_features.select_dtypes(include=[np.number])
            feature_matrix = numeric_features.values
            
            # Calculate similarity matrix
            if self.similarity_metric == 'cosine':
                self.similarity_matrix = cosine_similarity(feature_matrix)
            else:
                # Euclidean distance converted to similarity
                from sklearn.metrics.pairwise import euclidean_distances
                distances = euclidean_distances(feature_matrix)
                self.similarity_matrix = 1 / (1 + distances)
            
            return self
        except Exception as e:
            self.logger.error(f"Failed to fit content-based model: {e}")
            return self
    
    def get_similar_items(self, item_id: str, n_recommendations: int = 10) -> List[Tuple[str, float]]:
        """Get similar items based on content features"""
        try:
            if self.similarity_matrix is None:
                raise ValueError("Model not fitted")
            
            # Find item index
            item_idx = np.where(self.item_ids == item_id)[0]
            if len(item_idx) == 0:
                return []
            
            item_idx = item_idx[0]
            
            # Get similarity scores
            similarities = self.similarity_matrix[item_idx]
            
            # Get top similar items (excluding the item itself)
            similar_indices = np.argsort(similarities)[::-1][1:n_recommendations+1]
            
            recommendations = []
            for idx in similar_indices:
                similar_item_id = self.item_ids[idx]
                similarity_score = similarities[idx]
                recommendations.append((similar_item_id, similarity_score))
            
            return recommendations
        except Exception as e:
            self.logger.error(f"Failed to get similar items: {e}")
            return []
    
    def recommend_for_user(self, user_liked_items: List[str], n_recommendations: int = 10) -> List[Tuple[str, float]]:
        """Recommend items based on user's liked items"""
        try:
            if not user_liked_items:
                return []
            
            # Get similarities for all liked items
            all_recommendations = {}
            
            for item_id in user_liked_items:
                similar_items = self.get_similar_items(item_id, n_recommendations * 2)
                
                for similar_item_id, similarity in similar_items:
                    if similar_item_id not in user_liked_items:  # Don't recommend already liked items
                        if similar_item_id in all_recommendations:
                            all_recommendations[similar_item_id] += similarity
                        else:
                            all_recommendations[similar_item_id] = similarity
            
            # Sort by aggregated similarity score
            sorted_recommendations = sorted(
                all_recommendations.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return sorted_recommendations[:n_recommendations]
        except Exception as e:
            self.logger.error(f"Failed to recommend for user: {e}")
            return []

class HybridRecommendationSystem:
    """Hybrid recommendation system combining multiple approaches"""
    
    def __init__(self, weights: Dict[str, float] = None):
        if weights is None:
            weights = {
                'collaborative': 0.4,
                'content': 0.3,
                'popularity': 0.1,
                'diversity': 0.2
            }
        
        self.weights = weights
        self.ncf_model = None
        self.content_model = ContentBasedFiltering()
        self.popularity_model = PopularityBasedRecommender()
        self.diversity_injector = None
        self.user_encoder = {}
        self.item_encoder = {}
        self.logger = logging.getLogger(__name__)
    
    def fit(self, interactions_df: pd.DataFrame, item_features_df: pd.DataFrame,
            user_col: str = 'user_id', item_col: str = 'item_id', rating_col: str = 'rating'):
        """Fit all models in the hybrid system"""
        try:
            # Encode users and items
            unique_users = interactions_df[user_col].unique()
            unique_items = interactions_df[item_col].unique()
            
            self.user_encoder = {user: idx for idx, user in enumerate(unique_users)}
            self.item_encoder = {item: idx for idx, item in enumerate(unique_items)}
            
            # Prepare data for NCF
            user_ids = interactions_df[user_col].map(self.user_encoder).values
            item_ids = interactions_df[item_col].map(self.item_encoder).values
            ratings = interactions_df[rating_col].values
            
            # Train NCF model
            self.ncf_model = NeuralCollaborativeFiltering(
                num_users=len(unique_users),
                num_items=len(unique_items)
            )
            self.ncf_model.train(user_ids, item_ids, ratings)
            
            # Fit content-based model
            self.content_model.fit(item_features_df)
            
            # Fit popularity model
            self.popularity_model.fit(interactions_df, item_col, rating_col)
            
            return self
        except Exception as e:
            self.logger.error(f"Failed to fit hybrid model: {e}")
            return self
    
    def recommend(self, user_id: str, user_liked_items: List[str], 
                 n_recommendations: int = 20, diversity_boost: float = 0.0) -> List[Dict]:
        """Generate hybrid recommendations"""
        try:
            all_scores = {}
            
            # Collaborative filtering scores
            if self.ncf_model and user_id in self.user_encoder:
                cf_scores = self._get_collaborative_scores(user_id, n_recommendations * 2)
                for item_id, score in cf_scores:
                    all_scores[item_id] = all_scores.get(item_id, 0) + score * self.weights['collaborative']
            
            # Content-based scores
            cb_scores = self.content_model.recommend_for_user(user_liked_items, n_recommendations * 2)
            for item_id, score in cb_scores:
                all_scores[item_id] = all_scores.get(item_id, 0) + score * self.weights['content']
            
            # Popularity scores
            pop_scores = self.popularity_model.get_popular_items(n_recommendations * 2)
            for item_id, score in pop_scores:
                all_scores[item_id] = all_scores.get(item_id, 0) + score * self.weights['popularity']
            
            # Apply diversity boost if requested
            if diversity_boost > 0 and self.diversity_injector:
                diversity_scores = self.diversity_injector.calculate_diversity_scores(list(all_scores.keys()))
                for item_id, div_score in diversity_scores.items():
                    if item_id in all_scores:
                        all_scores[item_id] += div_score * diversity_boost
            
            # Sort and return top recommendations
            sorted_recommendations = sorted(
                all_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            recommendations = []
            for item_id, score in sorted_recommendations[:n_recommendations]:
                recommendations.append({
                    'item_id': item_id,
                    'score': score,
                    'timestamp': datetime.now().isoformat()
                })
            
            return recommendations
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    def _get_collaborative_scores(self, user_id: str, n_items: int) -> List[Tuple[str, float]]:
        """Get collaborative filtering scores"""
        try:
            if user_id not in self.user_encoder:
                return []
            
            user_idx = self.user_encoder[user_id]
            
            # Get all items
            item_indices = list(range(len(self.item_encoder)))
            user_indices = [user_idx] * len(item_indices)
            
            # Predict ratings
            predictions = self.ncf_model.predict(
                np.array(user_indices),
                np.array(item_indices)
            )
            
            # Convert back to item IDs and sort
            item_scores = []
            reverse_item_encoder = {idx: item for item, idx in self.item_encoder.items()}
            
            for idx, score in enumerate(predictions):
                item_id = reverse_item_encoder[idx]
                item_scores.append((item_id, score))
            
            # Sort by score and return top items
            item_scores.sort(key=lambda x: x[1], reverse=True)
            return item_scores[:n_items]
        except Exception as e:
            self.logger.error(f"Failed to get collaborative scores: {e}")
            return []
    
    def save_model(self, filepath: str):
        """Save the hybrid model"""
        try:
            model_data = {
                'weights': self.weights,
                'user_encoder': self.user_encoder,
                'item_encoder': self.item_encoder,
                'content_model': self.content_model,
                'popularity_model': self.popularity_model
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            # Save NCF model separately
            if self.ncf_model and self.ncf_model.model:
                ncf_path = filepath.replace('.pkl', '_ncf.h5')
                self.ncf_model.model.save(ncf_path)
            
            self.logger.info(f"Model saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
    
    def load_model(self, filepath: str):
        """Load the hybrid model"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.weights = model_data['weights']
            self.user_encoder = model_data['user_encoder']
            self.item_encoder = model_data['item_encoder']
            self.content_model = model_data['content_model']
            self.popularity_model = model_data['popularity_model']
            
            # Load NCF model
            ncf_path = filepath.replace('.pkl', '_ncf.h5')
            if os.path.exists(ncf_path):
                self.ncf_model = NeuralCollaborativeFiltering(
                    num_users=len(self.user_encoder),
                    num_items=len(self.item_encoder)
                )
                self.ncf_model.model = keras.models.load_model(ncf_path)
            
            self.logger.info(f"Model loaded from {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")

class PopularityBasedRecommender:
    """Simple popularity-based recommender"""
    
    def __init__(self):
        self.item_popularity = {}
        self.logger = logging.getLogger(__name__)
    
    def fit(self, interactions_df: pd.DataFrame, item_col: str = 'item_id', rating_col: str = 'rating'):
        """Fit popularity model"""
        try:
            # Calculate popularity scores (average rating * number of interactions)
            popularity_stats = interactions_df.groupby(item_col)[rating_col].agg(['mean', 'count'])
            
            # Normalize popularity scores
            max_count = popularity_stats['count'].max()
            popularity_stats['popularity_score'] = (
                popularity_stats['mean'] * np.log1p(popularity_stats['count']) / np.log1p(max_count)
            )
            
            self.item_popularity = popularity_stats['popularity_score'].to_dict()
            return self
        except Exception as e:
            self.logger.error(f"Failed to fit popularity model: {e}")
            return self
    
    def get_popular_items(self, n_items: int = 20) -> List[Tuple[str, float]]:
        """Get most popular items"""
        try:
            sorted_items = sorted(
                self.item_popularity.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return sorted_items[:n_items]
        except Exception as e:
            self.logger.error(f"Failed to get popular items: {e}")
            return []

class ExplorationStrategy:
    """Exploration strategies for recommendation diversity"""
    
    def __init__(self, strategy: str = 'epsilon_greedy', epsilon: float = 0.1):
        self.strategy = strategy
        self.epsilon = epsilon
        self.logger = logging.getLogger(__name__)
    
    def apply_exploration(self, recommendations: List[Dict], candidate_pool: List[Dict]) -> List[Dict]:
        """Apply exploration strategy to recommendations"""
        try:
            if self.strategy == 'epsilon_greedy':
                return self._epsilon_greedy_exploration(recommendations, candidate_pool)
            elif self.strategy == 'thompson_sampling':
                return self._thompson_sampling_exploration(recommendations, candidate_pool)
            else:
                return recommendations
        except Exception as e:
            self.logger.error(f"Failed to apply exploration: {e}")
            return recommendations
    
    def _epsilon_greedy_exploration(self, recommendations: List[Dict], candidate_pool: List[Dict]) -> List[Dict]:
        """Epsilon-greedy exploration"""
        n_explore = int(len(recommendations) * self.epsilon)
        n_exploit = len(recommendations) - n_explore
        
        # Keep top recommendations (exploitation)
        final_recommendations = recommendations[:n_exploit]
        
        # Add random items from candidate pool (exploration)
        if candidate_pool and n_explore > 0:
            recommended_ids = {rec['item_id'] for rec in recommendations}
            exploration_candidates = [
                item for item in candidate_pool 
                if item['item_id'] not in recommended_ids
            ]
            
            if exploration_candidates:
                exploration_items = np.random.choice(
                    exploration_candidates,
                    size=min(n_explore, len(exploration_candidates)),
                    replace=False
                )
                final_recommendations.extend(exploration_items)
        
        return final_recommendations
    
    def _thompson_sampling_exploration(self, recommendations: List[Dict], candidate_pool: List[Dict]) -> List[Dict]:
        """Thompson sampling exploration (simplified version)"""
        # For simplicity, this implements a basic version
        # In practice, this would use Beta distributions based on historical performance
        
        # Add uncertainty to scores
        for rec in recommendations:
            uncertainty = np.random.normal(0, 0.1)  # Add noise
            rec['exploration_score'] = rec['score'] + uncertainty
        
        # Re-sort by exploration score
        recommendations.sort(key=lambda x: x['exploration_score'], reverse=True)
        
        return recommendations