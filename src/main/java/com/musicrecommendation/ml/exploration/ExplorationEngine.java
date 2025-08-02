package com.musicrecommendation.ml.exploration;

import com.musicrecommendation.ml.TrackRecommendation;
import com.musicrecommendation.model.Track;
import com.musicrecommendation.model.User;
import org.apache.commons.math3.distribution.BetaDistribution;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Engine for implementing exploration algorithms to help users discover
 * new music outside their comfort zone and break overspecialization.
 */
@Component
public class ExplorationEngine {
    
    private static final Logger logger = LoggerFactory.getLogger(ExplorationEngine.class);
    
    // Exploration parameters
    private static final double DEFAULT_EPSILON = 0.2;
    private static final double DEFAULT_ALPHA = 1.0;
    private static final double DEFAULT_BETA = 1.0;
    
    /**
     * Calculate exploration score for a track based on user preferences
     */
    public double calculateExplorationScore(Track track, User user) {
        double score = 0.0;
        
        // Base exploration score from track properties
        score += calculateBaseExplorationScore(track);
        
        // User preference alignment
        score += calculateUserExplorationAlignment(track, user);
        
        // Novelty factor
        score += calculateNoveltyFactor(track, user);
        
        // Diversity factor
        score += calculateDiversityFactor(track, user);
        
        return Math.min(1.0, score);
    }
    
    /**
     * Apply exploration to a list of recommendations
     */
    public List<TrackRecommendation> applyExploration(List<TrackRecommendation> recommendations, User user) {
        if (recommendations.isEmpty()) {
            return recommendations;
        }
        
        logger.debug("Applying exploration for user: {}", user.getDisplayName());
        
        // Apply epsilon-greedy exploration
        recommendations = applyEpsilonGreedyExploration(recommendations, user.getExplorationLevel());
        
        // Apply Thompson sampling for uncertainty-based exploration
        recommendations = applyThompsonSampling(recommendations, user);
        
        // Apply contextual exploration based on user's current context
        recommendations = applyContextualExploration(recommendations, user);
        
        return recommendations;
    }
    
    /**
     * Apply epsilon-greedy exploration strategy
     */
    private List<TrackRecommendation> applyEpsilonGreedyExploration(List<TrackRecommendation> recommendations, 
                                                                   Double userExplorationLevel) {
        double epsilon = userExplorationLevel != null ? userExplorationLevel : DEFAULT_EPSILON;
        
        // With probability epsilon, select random recommendations
        if (Math.random() < epsilon) {
            logger.debug("Applying epsilon-greedy exploration with epsilon: {}", epsilon);
            
            // Shuffle recommendations to introduce randomness
            List<TrackRecommendation> shuffled = new ArrayList<>(recommendations);
            Collections.shuffle(shuffled);
            
            // Boost scores for some random tracks
            for (int i = 0; i < Math.min(5, shuffled.size()); i++) {
                TrackRecommendation rec = shuffled.get(i);
                rec.setScore(rec.getScore() * (1.0 + Math.random() * 0.3));
                rec.setExplanation("Exploration pick - discovering new music");
            }
        }
        
        return recommendations;
    }
    
    /**
     * Apply Thompson sampling for uncertainty-based exploration
     */
    private List<TrackRecommendation> applyThompsonSampling(List<TrackRecommendation> recommendations, User user) {
        logger.debug("Applying Thompson sampling exploration");
        
        for (TrackRecommendation rec : recommendations) {
            // Create beta distribution based on track properties
            double alpha = DEFAULT_ALPHA;
            double beta = DEFAULT_BETA;
            
            // Adjust based on track popularity (less popular = more uncertainty)
            if (rec.getTrack().getSpotifyPopularity() != null) {
                double popularity = rec.getTrack().getSpotifyPopularity() / 100.0;
                alpha += (1.0 - popularity) * 2.0; // More uncertainty for less popular tracks
                beta += popularity * 2.0; // Less uncertainty for popular tracks
            }
            
            // Adjust based on novelty
            if (rec.getTrack().getNoveltyScore() != null) {
                alpha += rec.getTrack().getNoveltyScore() * 1.5;
            }
            
            // Sample from beta distribution
            BetaDistribution betaDist = new BetaDistribution(alpha, beta);
            double sample = betaDist.sample();
            
            // Apply exploration bonus
            double explorationBonus = sample * 0.4;
            rec.setScore(rec.getScore() + explorationBonus);
            
            if (explorationBonus > 0.2) {
                rec.setExplanation("Thompson sampling - exploring uncertain preferences");
            }
        }
        
        return recommendations;
    }
    
    /**
     * Apply contextual exploration based on user's current context
     */
    private List<TrackRecommendation> applyContextualExploration(List<TrackRecommendation> recommendations, User user) {
        logger.debug("Applying contextual exploration");
        
        // Get user's current context
        User.Mood currentMood = user.getCurrentMood();
        User.Activity currentActivity = user.getCurrentActivity();
        User.TimeOfDay timeOfDay = user.getTimeOfDay();
        
        for (TrackRecommendation rec : recommendations) {
            double contextualBonus = 0.0;
            
            // Mood-based exploration
            contextualBonus += calculateMoodExplorationBonus(rec.getTrack(), currentMood);
            
            // Activity-based exploration
            contextualBonus += calculateActivityExplorationBonus(rec.getTrack(), currentActivity);
            
            // Time-based exploration
            contextualBonus += calculateTimeExplorationBonus(rec.getTrack(), timeOfDay);
            
            // Apply bonus
            rec.setScore(rec.getScore() + contextualBonus);
            
            if (contextualBonus > 0.1) {
                rec.setExplanation("Contextual exploration - matching your current situation");
            }
        }
        
        return recommendations;
    }
    
    /**
     * Calculate base exploration score from track properties
     */
    private double calculateBaseExplorationScore(Track track) {
        double score = 0.0;
        
        // Novelty score
        if (track.getNoveltyScore() != null) {
            score += track.getNoveltyScore() * 0.4;
        }
        
        // Popularity penalty (less popular = more exploration)
        if (track.getSpotifyPopularity() != null) {
            score += (100 - track.getSpotifyPopularity()) / 100.0 * 0.3;
        }
        
        // Independent artist bonus
        if (track.getIsIndependent() != null && track.getIsIndependent()) {
            score += 0.2;
        }
        
        // Diversity score
        if (track.getDiversityScore() != null) {
            score += track.getDiversityScore() * 0.3;
        }
        
        return score;
    }
    
    /**
     * Calculate user exploration alignment
     */
    private double calculateUserExplorationAlignment(Track track, User user) {
        double score = 0.0;
        
        // User's exploration preference
        if (user.getExplorationLevel() != null) {
            score += user.getExplorationLevel() * 0.3;
        }
        
        // User's novelty preference
        if (user.getNoveltyPreference() != null) {
            score += user.getNoveltyPreference() * 0.3;
        }
        
        // User's diversity preference
        if (user.getDiversityPreference() != null) {
            score += user.getDiversityPreference() * 0.2;
        }
        
        return score;
    }
    
    /**
     * Calculate novelty factor
     */
    private double calculateNoveltyFactor(Track track, User user) {
        double score = 0.0;
        
        // Track novelty
        if (track.getNoveltyScore() != null) {
            score += track.getNoveltyScore() * 0.4;
        }
        
        // Artist novelty (new artist to user)
        Set<String> userPreferredArtists = user.getPreferredArtists();
        if (!userPreferredArtists.contains(track.getArtist().toLowerCase())) {
            score += 0.3;
        }
        
        // Genre novelty (new genre to user)
        Set<String> userPreferredGenres = user.getPreferredGenres();
        if (track.getGenre() != null && !userPreferredGenres.contains(track.getGenre().toLowerCase())) {
            score += 0.3;
        }
        
        return score;
    }
    
    /**
     * Calculate diversity factor
     */
    private double calculateDiversityFactor(Track track, User user) {
        double score = 0.0;
        
        // Track diversity score
        if (track.getDiversityScore() != null) {
            score += track.getDiversityScore() * 0.4;
        }
        
        // Independent artist bonus
        if (track.getIsIndependent() != null && track.getIsIndependent()) {
            score += 0.3;
        }
        
        // Less popular artist bonus
        if (track.getArtistPopularity() != null && track.getArtistPopularity() < 50) {
            score += 0.3;
        }
        
        return score;
    }
    
    /**
     * Calculate mood-based exploration bonus
     */
    private double calculateMoodExplorationBonus(Track track, User.Mood mood) {
        double bonus = 0.0;
        
        // Audio features that match mood
        switch (mood) {
            case HAPPY -> {
                if (track.getValence() != null && track.getValence() > 0.7) {
                    bonus += 0.2;
                }
                if (track.getEnergy() != null && track.getEnergy() > 0.6) {
                    bonus += 0.1;
                }
            }
            case SAD -> {
                if (track.getValence() != null && track.getValence() < 0.4) {
                    bonus += 0.2;
                }
                if (track.getAcousticness() != null && track.getAcousticness() > 0.6) {
                    bonus += 0.1;
                }
            }
            case ENERGETIC -> {
                if (track.getEnergy() != null && track.getEnergy() > 0.8) {
                    bonus += 0.2;
                }
                if (track.getTempo() != null && track.getTempo() > 120) {
                    bonus += 0.1;
                }
            }
            case CALM -> {
                if (track.getEnergy() != null && track.getEnergy() < 0.4) {
                    bonus += 0.2;
                }
                if (track.getAcousticness() != null && track.getAcousticness() > 0.7) {
                    bonus += 0.1;
                }
            }
            case FOCUSED -> {
                if (track.getInstrumentalness() != null && track.getInstrumentalness() > 0.5) {
                    bonus += 0.2;
                }
                if (track.getSpeechiness() != null && track.getSpeechiness() < 0.1) {
                    bonus += 0.1;
                }
            }
            case PARTY -> {
                if (track.getDanceability() != null && track.getDanceability() > 0.7) {
                    bonus += 0.2;
                }
                if (track.getEnergy() != null && track.getEnergy() > 0.7) {
                    bonus += 0.1;
                }
            }
            case ROMANTIC -> {
                if (track.getValence() != null && track.getValence() > 0.5 && track.getValence() < 0.8) {
                    bonus += 0.2;
                }
                if (track.getAcousticness() != null && track.getAcousticness() > 0.5) {
                    bonus += 0.1;
                }
            }
        }
        
        return bonus;
    }
    
    /**
     * Calculate activity-based exploration bonus
     */
    private double calculateActivityExplorationBonus(Track track, User.Activity activity) {
        double bonus = 0.0;
        
        switch (activity) {
            case WORKING -> {
                if (track.getInstrumentalness() != null && track.getInstrumentalness() > 0.6) {
                    bonus += 0.2;
                }
                if (track.getSpeechiness() != null && track.getSpeechiness() < 0.1) {
                    bonus += 0.1;
                }
            }
            case EXERCISING -> {
                if (track.getEnergy() != null && track.getEnergy() > 0.8) {
                    bonus += 0.2;
                }
                if (track.getTempo() != null && track.getTempo() > 120) {
                    bonus += 0.1;
                }
            }
            case STUDYING -> {
                if (track.getInstrumentalness() != null && track.getInstrumentalness() > 0.7) {
                    bonus += 0.2;
                }
                if (track.getLoudness() != null && track.getLoudness() < -10) {
                    bonus += 0.1;
                }
            }
            case RELAXING -> {
                if (track.getEnergy() != null && track.getEnergy() < 0.3) {
                    bonus += 0.2;
                }
                if (track.getAcousticness() != null && track.getAcousticness() > 0.8) {
                    bonus += 0.1;
                }
            }
            case COMMUTING -> {
                if (track.getEnergy() != null && track.getEnergy() > 0.5) {
                    bonus += 0.2;
                }
                if (track.getDanceability() != null && track.getDanceability() > 0.6) {
                    bonus += 0.1;
                }
            }
            case SOCIALIZING -> {
                if (track.getDanceability() != null && track.getDanceability() > 0.7) {
                    bonus += 0.2;
                }
                if (track.getValence() != null && track.getValence() > 0.6) {
                    bonus += 0.1;
                }
            }
        }
        
        return bonus;
    }
    
    /**
     * Calculate time-based exploration bonus
     */
    private double calculateTimeExplorationBonus(Track track, User.TimeOfDay timeOfDay) {
        double bonus = 0.0;
        
        switch (timeOfDay) {
            case MORNING -> {
                if (track.getEnergy() != null && track.getEnergy() > 0.6) {
                    bonus += 0.2;
                }
                if (track.getValence() != null && track.getValence() > 0.6) {
                    bonus += 0.1;
                }
            }
            case DAY -> {
                // Neutral time, smaller bonus
                bonus += 0.1;
            }
            case EVENING -> {
                if (track.getValence() != null && track.getValence() > 0.5) {
                    bonus += 0.2;
                }
                if (track.getDanceability() != null && track.getDanceability() > 0.6) {
                    bonus += 0.1;
                }
            }
            case NIGHT -> {
                if (track.getEnergy() != null && track.getEnergy() < 0.5) {
                    bonus += 0.2;
                }
                if (track.getAcousticness() != null && track.getAcousticness() > 0.6) {
                    bonus += 0.1;
                }
            }
        }
        
        return bonus;
    }
    
    /**
     * Get exploration statistics for a set of recommendations
     */
    public Map<String, Double> getExplorationStats(List<TrackRecommendation> recommendations) {
        Map<String, Double> stats = new HashMap<>();
        
        if (recommendations.isEmpty()) {
            return stats;
        }
        
        // Average exploration score
        double avgExplorationScore = recommendations.stream()
                .mapToDouble(rec -> calculateExplorationScore(rec.getTrack(), null))
                .average()
                .orElse(0.0);
        stats.put("avg_exploration_score", avgExplorationScore);
        
        // Novelty ratio
        long novelTracks = recommendations.stream()
                .filter(rec -> rec.getTrack().getNoveltyScore() != null && rec.getTrack().getNoveltyScore() > 0.7)
                .count();
        double noveltyRatio = (double) novelTracks / recommendations.size();
        stats.put("novelty_ratio", noveltyRatio);
        
        // Independent artist ratio
        long independentTracks = recommendations.stream()
                .filter(rec -> rec.getTrack().getIsIndependent() != null && rec.getTrack().getIsIndependent())
                .count();
        double independentRatio = (double) independentTracks / recommendations.size();
        stats.put("independent_ratio", independentRatio);
        
        // Low popularity ratio
        long lowPopularityTracks = recommendations.stream()
                .filter(rec -> rec.getTrack().getSpotifyPopularity() != null && rec.getTrack().getSpotifyPopularity() < 50)
                .count();
        double lowPopularityRatio = (double) lowPopularityTracks / recommendations.size();
        stats.put("low_popularity_ratio", lowPopularityRatio);
        
        return stats;
    }
} 