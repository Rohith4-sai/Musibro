package com.musicrecommendation.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.Objects;

/**
 * Entity representing user interactions with tracks.
 * This includes ratings, play counts, and timestamps for building
 * collaborative filtering models and tracking user behavior.
 */
@Entity
@Table(name = "user_track_interactions")
public class UserTrackInteraction {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "track_id", nullable = false)
    private Track track;
    
    // Interaction Data
    @Column(name = "rating")
    private Integer rating; // 1-5 scale, null if not rated
    
    @Column(name = "play_count")
    private Integer playCount = 0;
    
    @Column(name = "skip_count")
    private Integer skipCount = 0;
    
    @Column(name = "like_status")
    @Enumerated(EnumType.STRING)
    private LikeStatus likeStatus = LikeStatus.NEUTRAL;
    
    @Column(name = "completion_rate")
    private Double completionRate = 0.0; // 0.0 to 1.0
    
    // Context Information
    @Column(name = "context_mood")
    @Enumerated(EnumType.STRING)
    private User.Mood contextMood;
    
    @Column(name = "context_activity")
    @Enumerated(EnumType.STRING)
    private User.Activity contextActivity;
    
    @Column(name = "context_time_of_day")
    @Enumerated(EnumType.STRING)
    private User.TimeOfDay contextTimeOfDay;
    
    // Timestamps
    @Column(name = "first_played_at")
    private LocalDateTime firstPlayedAt;
    
    @Column(name = "last_played_at")
    private LocalDateTime lastPlayedAt;
    
    @Column(name = "rated_at")
    private LocalDateTime ratedAt;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Enums
    public enum LikeStatus {
        LIKED, DISLIKED, NEUTRAL
    }
    
    // Constructors
    public UserTrackInteraction() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
    
    public UserTrackInteraction(User user, Track track) {
        this();
        this.user = user;
        this.track = track;
        this.firstPlayedAt = LocalDateTime.now();
        this.lastPlayedAt = LocalDateTime.now();
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public User getUser() {
        return user;
    }
    
    public void setUser(User user) {
        this.user = user;
    }
    
    public Track getTrack() {
        return track;
    }
    
    public void setTrack(Track track) {
        this.track = track;
    }
    
    public Integer getRating() {
        return rating;
    }
    
    public void setRating(Integer rating) {
        this.rating = rating;
        if (rating != null) {
            this.ratedAt = LocalDateTime.now();
        }
    }
    
    public Integer getPlayCount() {
        return playCount;
    }
    
    public void setPlayCount(Integer playCount) {
        this.playCount = playCount;
    }
    
    public Integer getSkipCount() {
        return skipCount;
    }
    
    public void setSkipCount(Integer skipCount) {
        this.skipCount = skipCount;
    }
    
    public LikeStatus getLikeStatus() {
        return likeStatus;
    }
    
    public void setLikeStatus(LikeStatus likeStatus) {
        this.likeStatus = likeStatus;
    }
    
    public Double getCompletionRate() {
        return completionRate;
    }
    
    public void setCompletionRate(Double completionRate) {
        this.completionRate = Math.max(0.0, Math.min(1.0, completionRate));
    }
    
    public User.Mood getContextMood() {
        return contextMood;
    }
    
    public void setContextMood(User.Mood contextMood) {
        this.contextMood = contextMood;
    }
    
    public User.Activity getContextActivity() {
        return contextActivity;
    }
    
    public void setContextActivity(User.Activity contextActivity) {
        this.contextActivity = contextActivity;
    }
    
    public User.TimeOfDay getContextTimeOfDay() {
        return contextTimeOfDay;
    }
    
    public void setContextTimeOfDay(User.TimeOfDay contextTimeOfDay) {
        this.contextTimeOfDay = contextTimeOfDay;
    }
    
    public LocalDateTime getFirstPlayedAt() {
        return firstPlayedAt;
    }
    
    public void setFirstPlayedAt(LocalDateTime firstPlayedAt) {
        this.firstPlayedAt = firstPlayedAt;
    }
    
    public LocalDateTime getLastPlayedAt() {
        return lastPlayedAt;
    }
    
    public void setLastPlayedAt(LocalDateTime lastPlayedAt) {
        this.lastPlayedAt = lastPlayedAt;
    }
    
    public LocalDateTime getRatedAt() {
        return ratedAt;
    }
    
    public void setRatedAt(LocalDateTime ratedAt) {
        this.ratedAt = ratedAt;
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    
    // Utility Methods
    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
    
    /**
     * Record a play event
     */
    public void recordPlay() {
        this.playCount++;
        this.lastPlayedAt = LocalDateTime.now();
        if (this.firstPlayedAt == null) {
            this.firstPlayedAt = LocalDateTime.now();
        }
    }
    
    /**
     * Record a skip event
     */
    public void recordSkip() {
        this.skipCount++;
        this.lastPlayedAt = LocalDateTime.now();
    }
    
    /**
     * Calculate implicit rating based on behavior
     */
    public double getImplicitRating() {
        double rating = 0.0;
        
        // Base rating from play count
        if (playCount > 0) {
            rating += Math.min(playCount * 0.5, 3.0); // Max 3 points from plays
        }
        
        // Penalty for skips
        if (skipCount > 0) {
            rating -= Math.min(skipCount * 0.3, 2.0); // Max 2 point penalty
        }
        
        // Bonus for completion rate
        if (completionRate > 0.8) {
            rating += 1.0;
        } else if (completionRate > 0.5) {
            rating += 0.5;
        }
        
        // Like status bonus/penalty
        switch (likeStatus) {
            case LIKED -> rating += 2.0;
            case DISLIKED -> rating -= 2.0;
        }
        
        return Math.max(0.0, Math.min(5.0, rating));
    }
    
    /**
     * Get the effective rating (explicit or implicit)
     */
    public double getEffectiveRating() {
        return rating != null ? rating : getImplicitRating();
    }
    
    /**
     * Check if this interaction indicates positive preference
     */
    public boolean isPositive() {
        return getEffectiveRating() >= 3.5;
    }
    
    /**
     * Check if this interaction indicates negative preference
     */
    public boolean isNegative() {
        return getEffectiveRating() <= 2.0;
    }
    
    /**
     * Get interaction weight for collaborative filtering
     */
    public double getInteractionWeight() {
        double weight = 1.0;
        
        // Recency weight (more recent interactions have higher weight)
        if (lastPlayedAt != null) {
            long daysSinceLastPlay = java.time.Duration.between(lastPlayedAt, LocalDateTime.now()).toDays();
            weight *= Math.exp(-daysSinceLastPlay / 30.0); // Decay over 30 days
        }
        
        // Frequency weight
        weight *= Math.log(playCount + 1);
        
        // Rating weight
        weight *= (getEffectiveRating() / 5.0);
        
        return weight;
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        UserTrackInteraction that = (UserTrackInteraction) o;
        return Objects.equals(user, that.user) && Objects.equals(track, that.track);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(user, track);
    }
    
    @Override
    public String toString() {
        return "UserTrackInteraction{" +
                "id=" + id +
                ", userId=" + (user != null ? user.getId() : null) +
                ", trackId=" + (track != null ? track.getSpotifyId() : null) +
                ", rating=" + rating +
                ", playCount=" + playCount +
                ", skipCount=" + skipCount +
                ", likeStatus=" + likeStatus +
                ", effectiveRating=" + getEffectiveRating() +
                '}';
    }
} 