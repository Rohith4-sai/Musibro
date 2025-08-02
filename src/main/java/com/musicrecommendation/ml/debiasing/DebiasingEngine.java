package com.musicrecommendation.ml.debiasing;

import com.musicrecommendation.ml.TrackRecommendation;
import com.musicrecommendation.model.Track;
import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Engine for applying debiasing techniques to reduce popularity bias
 * and ensure diversity in music recommendations.
 */
@Component
public class DebiasingEngine {
    
    private static final Logger logger = LoggerFactory.getLogger(DebiasingEngine.class);
    
    /**
     * Apply popularity normalization to reduce bias towards popular tracks
     */
    public List<TrackRecommendation> applyPopularityNormalization(List<TrackRecommendation> recommendations, double weight) {
        if (recommendations.isEmpty()) {
            return recommendations;
        }
        
        logger.debug("Applying popularity normalization with weight: {}", weight);
        
        // Calculate popularity statistics
        DescriptiveStatistics popularityStats = new DescriptiveStatistics();
        recommendations.stream()
                .map(rec -> rec.getTrack().getSpotifyPopularity())
                .filter(Objects::nonNull)
                .forEach(popularityStats::addValue);
        
        if (popularityStats.getN() == 0) {
            return recommendations;
        }
        
        double meanPopularity = popularityStats.getMean();
        double stdPopularity = popularityStats.getStandardDeviation();
        
        // Apply normalization to each recommendation
        for (TrackRecommendation rec : recommendations) {
            Track track = rec.getTrack();
            if (track.getSpotifyPopularity() != null) {
                // Calculate normalized popularity score (lower popularity = higher score)
                double normalizedPopularity = 1.0 - ((track.getSpotifyPopularity() - meanPopularity) / (stdPopularity + 1e-8));
                normalizedPopularity = Math.max(0.0, Math.min(1.0, normalizedPopularity));
                
                // Apply weight and update bias score
                double biasScore = normalizedPopularity * weight;
                rec.setPopularityBiasScore(biasScore);
                
                // Adjust overall score
                rec.setScore(rec.getScore() * (1.0 - weight) + biasScore * weight);
            }
        }
        
        return recommendations;
    }
    
    /**
     * Apply diversity injection to ensure variety in recommendations
     */
    public List<TrackRecommendation> applyDiversityInjection(List<TrackRecommendation> recommendations, double targetDiversity) {
        if (recommendations.isEmpty()) {
            return recommendations;
        }
        
        logger.debug("Applying diversity injection with target diversity: {}", targetDiversity);
        
        // Group tracks by artist and genre
        Map<String, List<TrackRecommendation>> artistGroups = recommendations.stream()
                .collect(Collectors.groupingBy(rec -> rec.getTrack().getArtist()));
        
        Map<String, List<TrackRecommendation>> genreGroups = recommendations.stream()
                .filter(rec -> rec.getTrack().getGenre() != null)
                .collect(Collectors.groupingBy(rec -> rec.getTrack().getGenre()));
        
        // Calculate diversity scores
        for (TrackRecommendation rec : recommendations) {
            double diversityScore = calculateDiversityScore(rec, artistGroups, genreGroups, recommendations.size());
            rec.setDiversityScore(diversityScore);
            
            // Boost score for diverse tracks
            rec.setScore(rec.getScore() + diversityScore * targetDiversity);
        }
        
        return recommendations;
    }
    
    /**
     * Apply fairness constraints to ensure balanced representation
     */
    public List<TrackRecommendation> applyFairnessConstraints(List<TrackRecommendation> recommendations, 
                                                             double artistBalanceThreshold) {
        if (recommendations.isEmpty()) {
            return recommendations;
        }
        
        logger.debug("Applying fairness constraints with threshold: {}", artistBalanceThreshold);
        
        // Count artist occurrences
        Map<String, Long> artistCounts = recommendations.stream()
                .collect(Collectors.groupingBy(rec -> rec.getTrack().getArtist(), Collectors.counting()));
        
        // Calculate ideal distribution
        int totalTracks = recommendations.size();
        double idealPerArtist = (double) totalTracks / artistCounts.size();
        
        // Apply fairness adjustments
        for (TrackRecommendation rec : recommendations) {
            String artist = rec.getTrack().getArtist();
            long artistCount = artistCounts.get(artist);
            
            // Penalize over-represented artists
            if (artistCount > idealPerArtist * (1 + artistBalanceThreshold)) {
                double penalty = (artistCount - idealPerArtist) / idealPerArtist;
                rec.setScore(rec.getScore() * (1.0 - penalty * 0.3));
            }
            
            // Boost under-represented artists
            if (artistCount < idealPerArtist * (1 - artistBalanceThreshold)) {
                double boost = (idealPerArtist - artistCount) / idealPerArtist;
                rec.setScore(rec.getScore() * (1.0 + boost * 0.2));
            }
        }
        
        return recommendations;
    }
    
    /**
     * Apply adversarial debiasing to make recommendations more robust
     */
    public List<TrackRecommendation> applyAdversarialDebiasing(List<TrackRecommendation> recommendations) {
        if (recommendations.isEmpty()) {
            return recommendations;
        }
        
        logger.debug("Applying adversarial debiasing");
        
        // Identify potential bias patterns
        List<String> biasPatterns = identifyBiasPatterns(recommendations);
        
        // Apply counter-measures
        for (TrackRecommendation rec : recommendations) {
            double adversarialScore = calculateAdversarialScore(rec, biasPatterns);
            rec.setScore(rec.getScore() + adversarialScore);
        }
        
        return recommendations;
    }
    
    /**
     * Calculate diversity score for a track
     */
    private double calculateDiversityScore(TrackRecommendation rec, 
                                         Map<String, List<TrackRecommendation>> artistGroups,
                                         Map<String, List<TrackRecommendation>> genreGroups,
                                         int totalTracks) {
        Track track = rec.getTrack();
        double diversityScore = 0.0;
        
        // Artist diversity (fewer tracks from same artist = higher diversity)
        String artist = track.getArtist();
        if (artistGroups.containsKey(artist)) {
            int artistCount = artistGroups.get(artist).size();
            double artistDiversity = 1.0 - ((double) artistCount / totalTracks);
            diversityScore += artistDiversity * 0.6;
        }
        
        // Genre diversity
        String genre = track.getGenre();
        if (genre != null && genreGroups.containsKey(genre)) {
            int genreCount = genreGroups.get(genre).size();
            double genreDiversity = 1.0 - ((double) genreCount / totalTracks);
            diversityScore += genreDiversity * 0.4;
        }
        
        // Independent artist bonus
        if (track.getIsIndependent() != null && track.getIsIndependent()) {
            diversityScore += 0.2;
        }
        
        // Novelty bonus
        if (track.getNoveltyScore() != null) {
            diversityScore += track.getNoveltyScore() * 0.3;
        }
        
        return Math.min(1.0, diversityScore);
    }
    
    /**
     * Identify potential bias patterns in recommendations
     */
    private List<String> identifyBiasPatterns(List<TrackRecommendation> recommendations) {
        List<String> patterns = new ArrayList<>();
        
        // Check for popularity bias
        double avgPopularity = recommendations.stream()
                .mapToDouble(rec -> rec.getTrack().getSpotifyPopularity() != null ? 
                        rec.getTrack().getSpotifyPopularity() : 0.0)
                .average()
                .orElse(0.0);
        
        if (avgPopularity > 70) {
            patterns.add("HIGH_POPULARITY_BIAS");
        }
        
        // Check for artist concentration
        Map<String, Long> artistCounts = recommendations.stream()
                .collect(Collectors.groupingBy(rec -> rec.getTrack().getArtist(), Collectors.counting()));
        
        long maxArtistCount = artistCounts.values().stream().mapToLong(Long::longValue).max().orElse(0);
        if (maxArtistCount > recommendations.size() * 0.3) {
            patterns.add("ARTIST_CONCENTRATION_BIAS");
        }
        
        // Check for genre concentration
        Map<String, Long> genreCounts = recommendations.stream()
                .filter(rec -> rec.getTrack().getGenre() != null)
                .collect(Collectors.groupingBy(rec -> rec.getTrack().getGenre(), Collectors.counting()));
        
        if (!genreCounts.isEmpty()) {
            long maxGenreCount = genreCounts.values().stream().mapToLong(Long::longValue).max().orElse(0);
            if (maxGenreCount > recommendations.size() * 0.5) {
                patterns.add("GENRE_CONCENTRATION_BIAS");
            }
        }
        
        return patterns;
    }
    
    /**
     * Calculate adversarial score to counter bias patterns
     */
    private double calculateAdversarialScore(TrackRecommendation rec, List<String> biasPatterns) {
        double score = 0.0;
        Track track = rec.getTrack();
        
        for (String pattern : biasPatterns) {
            switch (pattern) {
                case "HIGH_POPULARITY_BIAS" -> {
                    // Boost less popular tracks
                    if (track.getSpotifyPopularity() != null && track.getSpotifyPopularity() < 50) {
                        score += 0.3;
                    }
                }
                case "ARTIST_CONCENTRATION_BIAS" -> {
                    // Boost tracks from less represented artists
                    score += 0.2;
                }
                case "GENRE_CONCENTRATION_BIAS" -> {
                    // Boost tracks from less represented genres
                    score += 0.2;
                }
            }
        }
        
        return score;
    }
    
    /**
     * Apply comprehensive debiasing combining all techniques
     */
    public List<TrackRecommendation> applyComprehensiveDebiasing(List<TrackRecommendation> recommendations, 
                                                                 double popularityWeight,
                                                                 double diversityWeight,
                                                                 double fairnessThreshold) {
        logger.info("Applying comprehensive debiasing to {} recommendations", recommendations.size());
        
        // Apply popularity normalization
        recommendations = applyPopularityNormalization(recommendations, popularityWeight);
        
        // Apply diversity injection
        recommendations = applyDiversityInjection(recommendations, diversityWeight);
        
        // Apply fairness constraints
        recommendations = applyFairnessConstraints(recommendations, fairnessThreshold);
        
        // Apply adversarial debiasing
        recommendations = applyAdversarialDebiasing(recommendations);
        
        // Final sorting by adjusted scores
        recommendations.sort(Comparator.comparing(TrackRecommendation::getScore).reversed());
        
        logger.info("Comprehensive debiasing completed");
        return recommendations;
    }
    
    /**
     * Calculate overall bias metrics for a set of recommendations
     */
    public Map<String, Double> calculateBiasMetrics(List<TrackRecommendation> recommendations) {
        Map<String, Double> metrics = new HashMap<>();
        
        if (recommendations.isEmpty()) {
            return metrics;
        }
        
        // Popularity bias metric
        double avgPopularity = recommendations.stream()
                .mapToDouble(rec -> rec.getTrack().getSpotifyPopularity() != null ? 
                        rec.getTrack().getSpotifyPopularity() : 0.0)
                .average()
                .orElse(0.0);
        metrics.put("popularity_bias", avgPopularity / 100.0);
        
        // Diversity metric
        Set<String> uniqueArtists = recommendations.stream()
                .map(rec -> rec.getTrack().getArtist())
                .collect(Collectors.toSet());
        double artistDiversity = (double) uniqueArtists.size() / recommendations.size();
        metrics.put("artist_diversity", artistDiversity);
        
        // Genre diversity metric
        Set<String> uniqueGenres = recommendations.stream()
                .map(rec -> rec.getTrack().getGenre())
                .filter(Objects::nonNull)
                .collect(Collectors.toSet());
        double genreDiversity = uniqueGenres.isEmpty() ? 0.0 : 
                (double) uniqueGenres.size() / recommendations.size();
        metrics.put("genre_diversity", genreDiversity);
        
        // Independent artist ratio
        long independentCount = recommendations.stream()
                .filter(rec -> rec.getTrack().getIsIndependent() != null && rec.getTrack().getIsIndependent())
                .count();
        double independentRatio = (double) independentCount / recommendations.size();
        metrics.put("independent_ratio", independentRatio);
        
        // Overall bias score (lower is better)
        double overallBias = (1.0 - artistDiversity) * 0.4 + 
                           (1.0 - genreDiversity) * 0.3 + 
                           (avgPopularity / 100.0) * 0.3;
        metrics.put("overall_bias_score", overallBias);
        
        return metrics;
    }
} 