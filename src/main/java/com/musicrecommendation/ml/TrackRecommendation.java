package com.musicrecommendation.ml;

import com.musicrecommendation.model.Track;
import java.util.Objects;

/**
 * Represents a track recommendation with its score and metadata.
 * This class is used throughout the recommendation system to
 * track recommendation scores and types.
 */
public class TrackRecommendation {
    
    private final Track track;
    private double score;
    private final HybridRecommendationSystem.RecommendationType type;
    private String explanation;
    private double diversityScore;
    private double noveltyScore;
    private double popularityBiasScore;
    
    public TrackRecommendation(Track track, double score, HybridRecommendationSystem.RecommendationType type) {
        this.track = track;
        this.score = score;
        this.type = type;
        this.explanation = "";
    }
    
    public TrackRecommendation(Track track, double score, HybridRecommendationSystem.RecommendationType type, String explanation) {
        this.track = track;
        this.score = score;
        this.type = type;
        this.explanation = explanation;
    }
    
    // Getters and Setters
    public Track getTrack() {
        return track;
    }
    
    public double getScore() {
        return score;
    }
    
    public void setScore(double score) {
        this.score = score;
    }
    
    public HybridRecommendationSystem.RecommendationType getType() {
        return type;
    }
    
    public String getExplanation() {
        return explanation;
    }
    
    public void setExplanation(String explanation) {
        this.explanation = explanation;
    }
    
    public double getDiversityScore() {
        return diversityScore;
    }
    
    public void setDiversityScore(double diversityScore) {
        this.diversityScore = diversityScore;
    }
    
    public double getNoveltyScore() {
        return noveltyScore;
    }
    
    public void setNoveltyScore(double noveltyScore) {
        this.noveltyScore = noveltyScore;
    }
    
    public double getPopularityBiasScore() {
        return popularityBiasScore;
    }
    
    public void setPopularityBiasScore(double popularityBiasScore) {
        this.popularityBiasScore = popularityBiasScore;
    }
    
    /**
     * Get the overall recommendation score including all factors
     */
    public double getOverallScore() {
        return score + diversityScore + noveltyScore + popularityBiasScore;
    }
    
    /**
     * Get a human-readable explanation of why this track was recommended
     */
    public String getDetailedExplanation() {
        StringBuilder sb = new StringBuilder();
        
        if (!explanation.isEmpty()) {
            sb.append(explanation);
        }
        
        if (diversityScore > 0.5) {
            sb.append(" High diversity score. ");
        }
        
        if (noveltyScore > 0.7) {
            sb.append(" Novel discovery. ");
        }
        
        if (popularityBiasScore > 0.6) {
            sb.append(" Bias-resistant selection. ");
        }
        
        return sb.toString().trim();
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        TrackRecommendation that = (TrackRecommendation) o;
        return Objects.equals(track, that.track);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(track);
    }
    
    @Override
    public String toString() {
        return "TrackRecommendation{" +
                "track=" + track.getName() + " by " + track.getArtist() +
                ", score=" + score +
                ", type=" + type +
                ", overallScore=" + getOverallScore() +
                '}';
    }
} 