package com.musicrecommendation.ml;

import com.musicrecommendation.model.*;
import com.musicrecommendation.ml.debiasing.DebiasingEngine;
import com.musicrecommendation.ml.exploration.ExplorationEngine;
import com.musicrecommendation.ml.context.ContextEngine;
import org.apache.commons.math3.linear.*;
import org.apache.commons.math3.stat.correlation.PearsonsCorrelation;
import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Hybrid recommendation system that combines multiple approaches:
 * - Collaborative filtering (user-based and item-based)
 * - Content-based filtering using audio features
 * - Debiasing mechanisms to reduce popularity bias
 * - Exploration algorithms to break overspecialization
 * - Context-aware personalization
 */
@Component
public class HybridRecommendationSystem {
    
    private static final Logger logger = LoggerFactory.getLogger(HybridRecommendationSystem.class);
    
    @Autowired
    private DebiasingEngine debiasingEngine;
    
    @Autowired
    private ExplorationEngine explorationEngine;
    
    @Autowired
    private ContextEngine contextEngine;
    
    // Configuration parameters
    private static final double COLLABORATIVE_WEIGHT = 0.4;
    private static final double CONTENT_WEIGHT = 0.6;
    private static final double DEBIASING_WEIGHT = 0.3;
    private static final double EXPLORATION_WEIGHT = 0.2;
    private static final int MAX_RECOMMENDATIONS = 50;
    private static final double SIMILARITY_THRESHOLD = 0.7;
    
    /**
     * Generate comprehensive recommendations for a user
     */
    public List<TrackRecommendation> generateRecommendations(User user, List<Track> candidateTracks, 
                                                           RecommendationType type) {
        logger.info("Generating {} recommendations for user: {}", type, user.getDisplayName());
        
        // Get user interactions and preferences
        List<UserTrackInteraction> userInteractions = user.getTrackInteractions();
        Set<String> userLikedTrackIds = user.getLikedTracks().stream()
                .map(Track::getSpotifyId)
                .collect(Collectors.toSet());
        
        // Filter out tracks the user has already interacted with
        List<Track> filteredCandidates = candidateTracks.stream()
                .filter(track -> !userLikedTrackIds.contains(track.getSpotifyId()))
                .collect(Collectors.toList());
        
        // Generate different types of recommendations
        List<TrackRecommendation> recommendations = new ArrayList<>();
        
        switch (type) {
            case FOR_YOU -> recommendations = generateForYouRecommendations(user, filteredCandidates, userInteractions);
            case NEW_NICHE -> recommendations = generateNewNicheRecommendations(user, filteredCandidates);
            case EXPERIMENTAL -> recommendations = generateExperimentalRecommendations(user, filteredCandidates);
            default -> recommendations = generateHybridRecommendations(user, filteredCandidates, userInteractions);
        }
        
        // Apply final ranking and diversity optimization
        recommendations = applyFinalRanking(recommendations, user);
        
        logger.info("Generated {} recommendations for user: {}", recommendations.size(), user.getDisplayName());
        return recommendations;
    }
    
    /**
     * Generate "For You" recommendations - personalized favorites with some discovery
     */
    private List<TrackRecommendation> generateForYouRecommendations(User user, List<Track> candidates, 
                                                                   List<UserTrackInteraction> interactions) {
        List<TrackRecommendation> recommendations = new ArrayList<>();
        
        // Collaborative filtering component
        List<TrackRecommendation> collaborativeRecs = collaborativeFiltering(user, candidates, interactions);
        
        // Content-based filtering component
        List<TrackRecommendation> contentRecs = contentBasedFiltering(user, candidates);
        
        // Combine with weights
        Map<String, TrackRecommendation> combinedRecs = new HashMap<>();
        
        // Add collaborative recommendations
        for (TrackRecommendation rec : collaborativeRecs) {
            combinedRecs.put(rec.getTrack().getSpotifyId(), rec);
        }
        
        // Add content-based recommendations with weighted scores
        for (TrackRecommendation rec : contentRecs) {
            TrackRecommendation existing = combinedRecs.get(rec.getTrack().getSpotifyId());
            if (existing != null) {
                existing.setScore(existing.getScore() * COLLABORATIVE_WEIGHT + rec.getScore() * CONTENT_WEIGHT);
            } else {
                rec.setScore(rec.getScore() * CONTENT_WEIGHT);
                combinedRecs.put(rec.getTrack().getSpotifyId(), rec);
            }
        }
        
        recommendations.addAll(combinedRecs.values());
        
        // Apply light debiasing for "For You" section
        recommendations = debiasingEngine.applyPopularityNormalization(recommendations, 0.2);
        
        return recommendations.stream()
                .sorted(Comparator.comparing(TrackRecommendation::getScore).reversed())
                .limit(MAX_RECOMMENDATIONS)
                .collect(Collectors.toList());
    }
    
    /**
     * Generate "New & Niche" recommendations - focus on discovery and diversity
     */
    private List<TrackRecommendation> generateNewNicheRecommendations(User user, List<Track> candidates) {
        List<TrackRecommendation> recommendations = new ArrayList<>();
        
        // Filter for new and niche tracks
        List<Track> nicheCandidates = candidates.stream()
                .filter(track -> track.getNoveltyScore() != null && track.getNoveltyScore() > 0.6)
                .filter(track -> track.getSpotifyPopularity() != null && track.getSpotifyPopularity() < 50)
                .filter(track -> track.getIsIndependent() != null && track.getIsIndependent())
                .collect(Collectors.toList());
        
        // Content-based filtering with novelty bias
        for (Track track : nicheCandidates) {
            double score = calculateNoveltyScore(track, user);
            recommendations.add(new TrackRecommendation(track, score, RecommendationType.NEW_NICHE));
        }
        
        // Apply strong debiasing
        recommendations = debiasingEngine.applyPopularityNormalization(recommendations, 0.8);
        recommendations = debiasingEngine.applyDiversityInjection(recommendations, 0.6);
        
        return recommendations.stream()
                .sorted(Comparator.comparing(TrackRecommendation::getScore).reversed())
                .limit(MAX_RECOMMENDATIONS)
                .collect(Collectors.toList());
    }
    
    /**
     * Generate "Experimental" recommendations - break user's comfort zone
     */
    private List<TrackRecommendation> generateExperimentalRecommendations(User user, List<Track> candidates) {
        List<TrackRecommendation> recommendations = new ArrayList<>();
        
        // Get user's typical preferences
        Set<String> userPreferredGenres = user.getPreferredGenres();
        Set<String> userPreferredArtists = user.getPreferredArtists();
        
        // Find tracks that are different from user's preferences
        List<Track> experimentalCandidates = candidates.stream()
                .filter(track -> {
                    // Different genre
                    boolean differentGenre = track.getGenre() == null || 
                            !userPreferredGenres.contains(track.getGenre().toLowerCase());
                    
                    // Different artist
                    boolean differentArtist = !userPreferredArtists.contains(track.getArtist().toLowerCase());
                    
                    // High novelty
                    boolean highNovelty = track.getNoveltyScore() != null && track.getNoveltyScore() > 0.7;
                    
                    return differentGenre || differentArtist || highNovelty;
                })
                .collect(Collectors.toList());
        
        // Apply exploration algorithms
        for (Track track : experimentalCandidates) {
            double explorationScore = explorationEngine.calculateExplorationScore(track, user);
            recommendations.add(new TrackRecommendation(track, explorationScore, RecommendationType.EXPERIMENTAL));
        }
        
        // Apply maximum debiasing and diversity
        recommendations = debiasingEngine.applyPopularityNormalization(recommendations, 1.0);
        recommendations = debiasingEngine.applyDiversityInjection(recommendations, 0.8);
        
        return recommendations.stream()
                .sorted(Comparator.comparing(TrackRecommendation::getScore).reversed())
                .limit(MAX_RECOMMENDATIONS)
                .collect(Collectors.toList());
    }
    
    /**
     * Generate hybrid recommendations combining all approaches
     */
    private List<TrackRecommendation> generateHybridRecommendations(User user, List<Track> candidates, 
                                                                   List<UserTrackInteraction> interactions) {
        List<TrackRecommendation> recommendations = new ArrayList<>();
        
        // Collaborative filtering
        List<TrackRecommendation> collaborativeRecs = collaborativeFiltering(user, candidates, interactions);
        
        // Content-based filtering
        List<TrackRecommendation> contentRecs = contentBasedFiltering(user, candidates);
        
        // Combine all approaches
        Map<String, TrackRecommendation> combinedRecs = new HashMap<>();
        
        // Add collaborative recommendations
        for (TrackRecommendation rec : collaborativeRecs) {
            combinedRecs.put(rec.getTrack().getSpotifyId(), rec);
        }
        
        // Add content-based recommendations
        for (TrackRecommendation rec : contentRecs) {
            TrackRecommendation existing = combinedRecs.get(rec.getTrack().getSpotifyId());
            if (existing != null) {
                existing.setScore(existing.getScore() * COLLABORATIVE_WEIGHT + rec.getScore() * CONTENT_WEIGHT);
            } else {
                rec.setScore(rec.getScore() * CONTENT_WEIGHT);
                combinedRecs.put(rec.getTrack().getSpotifyId(), rec);
            }
        }
        
        recommendations.addAll(combinedRecs.values());
        
        // Apply debiasing
        recommendations = debiasingEngine.applyPopularityNormalization(recommendations, DEBIASING_WEIGHT);
        recommendations = debiasingEngine.applyDiversityInjection(recommendations, 0.4);
        
        return recommendations.stream()
                .sorted(Comparator.comparing(TrackRecommendation::getScore).reversed())
                .limit(MAX_RECOMMENDATIONS)
                .collect(Collectors.toList());
    }
    
    /**
     * Collaborative filtering using user-based approach
     */
    private List<TrackRecommendation> collaborativeFiltering(User user, List<Track> candidates, 
                                                            List<UserTrackInteraction> interactions) {
        List<TrackRecommendation> recommendations = new ArrayList<>();
        
        if (interactions.isEmpty()) {
            return recommendations;
        }
        
        // Build user-item matrix
        Map<String, Map<String, Double>> userItemMatrix = buildUserItemMatrix(interactions);
        
        // Find similar users
        List<String> similarUsers = findSimilarUsers(user.getSpotifyUserId(), userItemMatrix);
        
        // Generate recommendations based on similar users
        for (Track candidate : candidates) {
            double score = calculateCollaborativeScore(candidate.getSpotifyId(), similarUsers, userItemMatrix);
            if (score > 0) {
                recommendations.add(new TrackRecommendation(candidate, score, RecommendationType.FOR_YOU));
            }
        }
        
        return recommendations;
    }
    
    /**
     * Content-based filtering using audio features
     */
    private List<TrackRecommendation> contentBasedFiltering(User user, List<Track> candidates) {
        List<TrackRecommendation> recommendations = new ArrayList<>();
        
        // Get user's preferred tracks for feature extraction
        List<Track> userLikedTracks = user.getLikedTracks();
        
        if (userLikedTracks.isEmpty()) {
            return recommendations;
        }
        
        // Calculate user's feature profile
        double[] userProfile = calculateUserFeatureProfile(userLikedTracks);
        
        // Calculate similarity for each candidate
        for (Track candidate : candidates) {
            double[] candidateFeatures = candidate.getFeatureVector();
            double similarity = calculateCosineSimilarity(userProfile, candidateFeatures);
            
            if (similarity > SIMILARITY_THRESHOLD) {
                recommendations.add(new TrackRecommendation(candidate, similarity, RecommendationType.FOR_YOU));
            }
        }
        
        return recommendations;
    }
    
    /**
     * Calculate novelty score for a track
     */
    private double calculateNoveltyScore(Track track, User user) {
        double score = 0.0;
        
        // Base novelty from track
        if (track.getNoveltyScore() != null) {
            score += track.getNoveltyScore();
        }
        
        // Popularity penalty (less popular = more novel)
        if (track.getSpotifyPopularity() != null) {
            score += (100 - track.getSpotifyPopularity()) / 100.0;
        }
        
        // Independent artist bonus
        if (track.getIsIndependent() != null && track.getIsIndependent()) {
            score += 0.3;
        }
        
        // User preference alignment
        if (user.getNoveltyPreference() != null) {
            score *= user.getNoveltyPreference();
        }
        
        return Math.min(1.0, score);
    }
    
    /**
     * Build user-item matrix from interactions
     */
    private Map<String, Map<String, Double>> buildUserItemMatrix(List<UserTrackInteraction> interactions) {
        Map<String, Map<String, Double>> matrix = new HashMap<>();
        
        for (UserTrackInteraction interaction : interactions) {
            String userId = interaction.getUser().getSpotifyUserId();
            String trackId = interaction.getTrack().getSpotifyId();
            double rating = interaction.getEffectiveRating();
            
            matrix.computeIfAbsent(userId, k -> new HashMap<>()).put(trackId, rating);
        }
        
        return matrix;
    }
    
    /**
     * Find similar users using Pearson correlation
     */
    private List<String> findSimilarUsers(String targetUserId, Map<String, Map<String, Double>> userItemMatrix) {
        List<String> similarUsers = new ArrayList<>();
        Map<String, Double> targetUserRatings = userItemMatrix.get(targetUserId);
        
        if (targetUserRatings == null) {
            return similarUsers;
        }
        
        for (Map.Entry<String, Map<String, Double>> entry : userItemMatrix.entrySet()) {
            String userId = entry.getKey();
            if (userId.equals(targetUserId)) {
                continue;
            }
            
            Map<String, Double> userRatings = entry.getValue();
            double correlation = calculatePearsonCorrelation(targetUserRatings, userRatings);
            
            if (correlation > SIMILARITY_THRESHOLD) {
                similarUsers.add(userId);
            }
        }
        
        return similarUsers;
    }
    
    /**
     * Calculate collaborative filtering score
     */
    private double calculateCollaborativeScore(String trackId, List<String> similarUsers, 
                                             Map<String, Map<String, Double>> userItemMatrix) {
        double totalScore = 0.0;
        int count = 0;
        
        for (String userId : similarUsers) {
            Map<String, Double> userRatings = userItemMatrix.get(userId);
            if (userRatings != null && userRatings.containsKey(trackId)) {
                totalScore += userRatings.get(trackId);
                count++;
            }
        }
        
        return count > 0 ? totalScore / count : 0.0;
    }
    
    /**
     * Calculate user's feature profile from liked tracks
     */
    private double[] calculateUserFeatureProfile(List<Track> likedTracks) {
        if (likedTracks.isEmpty()) {
            return new double[9]; // Default feature vector
        }
        
        double[] profile = new double[9];
        
        for (Track track : likedTracks) {
            double[] features = track.getFeatureVector();
            for (int i = 0; i < features.length; i++) {
                profile[i] += features[i];
            }
        }
        
        // Normalize by number of tracks
        for (int i = 0; i < profile.length; i++) {
            profile[i] /= likedTracks.size();
        }
        
        return profile;
    }
    
    /**
     * Calculate cosine similarity between two feature vectors
     */
    private double calculateCosineSimilarity(double[] vector1, double[] vector2) {
        double dotProduct = 0.0;
        double norm1 = 0.0;
        double norm2 = 0.0;
        
        for (int i = 0; i < vector1.length; i++) {
            dotProduct += vector1[i] * vector2[i];
            norm1 += vector1[i] * vector1[i];
            norm2 += vector2[i] * vector2[i];
        }
        
        if (norm1 == 0 || norm2 == 0) {
            return 0.0;
        }
        
        return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
    }
    
    /**
     * Calculate Pearson correlation between two rating vectors
     */
    private double calculatePearsonCorrelation(Map<String, Double> ratings1, Map<String, Double> ratings2) {
        // Find common items
        Set<String> commonItems = new HashSet<>(ratings1.keySet());
        commonItems.retainAll(ratings2.keySet());
        
        if (commonItems.size() < 2) {
            return 0.0;
        }
        
        // Extract common ratings
        double[] values1 = new double[commonItems.size()];
        double[] values2 = new double[commonItems.size()];
        
        int i = 0;
        for (String item : commonItems) {
            values1[i] = ratings1.get(item);
            values2[i] = ratings2.get(item);
            i++;
        }
        
        // Calculate correlation
        PearsonsCorrelation correlation = new PearsonsCorrelation();
        return correlation.correlation(values1, values2);
    }
    
    /**
     * Apply final ranking and optimization
     */
    private List<TrackRecommendation> applyFinalRanking(List<TrackRecommendation> recommendations, User user) {
        // Apply context weights
        recommendations = contextEngine.applyContextWeights(recommendations, user);
        
        // Apply exploration if needed
        if (user.getExplorationLevel() > 0.5) {
            recommendations = explorationEngine.applyExploration(recommendations, user);
        }
        
        // Final sorting
        return recommendations.stream()
                .sorted(Comparator.comparing(TrackRecommendation::getScore).reversed())
                .limit(MAX_RECOMMENDATIONS)
                .collect(Collectors.toList());
    }
    
    /**
     * Recommendation types
     */
    public enum RecommendationType {
        FOR_YOU, NEW_NICHE, EXPERIMENTAL, HYBRID
    }
} 