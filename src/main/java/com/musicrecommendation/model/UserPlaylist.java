package com.musicrecommendation.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.*;

/**
 * Entity representing user playlists and system-generated recommendation playlists.
 * This includes both user-created playlists and automatically generated
 * recommendation collections.
 */
@Entity
@Table(name = "user_playlists")
public class UserPlaylist {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    @Column(name = "name", nullable = false)
    private String name;
    
    @Column(name = "description")
    private String description;
    
    @Column(name = "playlist_type")
    @Enumerated(EnumType.STRING)
    private PlaylistType playlistType = PlaylistType.USER_CREATED;
    
    @Column(name = "is_public")
    private Boolean isPublic = false;
    
    @Column(name = "is_collaborative")
    private Boolean isCollaborative = false;
    
    // Recommendation-specific fields
    @Column(name = "recommendation_category")
    @Enumerated(EnumType.STRING)
    private RecommendationCategory recommendationCategory;
    
    @Column(name = "diversity_score")
    private Double diversityScore;
    
    @Column(name = "novelty_score")
    private Double noveltyScore;
    
    @Column(name = "exploration_level")
    private Double explorationLevel;
    
    // Track associations
    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "playlist_tracks",
        joinColumns = @JoinColumn(name = "playlist_id"),
        inverseJoinColumns = @JoinColumn(name = "track_id")
    )
    @OrderColumn(name = "track_order")
    private List<Track> tracks = new ArrayList<>();
    
    // Metadata
    @Column(name = "total_duration_ms")
    private Long totalDurationMs = 0L;
    
    @Column(name = "track_count")
    private Integer trackCount = 0;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @Column(name = "last_modified")
    private LocalDateTime lastModified;
    
    // Enums
    public enum PlaylistType {
        USER_CREATED,           // User manually created
        SYSTEM_RECOMMENDATION,  // System-generated recommendation
        DISCOVERY_PLAYLIST,     // Discovery-focused playlist
        MOOD_BASED,            // Mood-based recommendation
        ACTIVITY_BASED         // Activity-based recommendation
    }
    
    public enum RecommendationCategory {
        FOR_YOU,           // Personalized recommendations
        NEW_NICHE,         // New and niche artists
        EXPERIMENTAL,      // Experimental recommendations
        MOOD_HAPPY,        // Happy mood
        MOOD_SAD,          // Sad mood
        MOOD_ENERGETIC,    // Energetic mood
        MOOD_CALM,         // Calm mood
        ACTIVITY_WORKOUT,  // Workout music
        ACTIVITY_STUDY,    // Study music
        ACTIVITY_RELAX     // Relaxation music
    }
    
    // Constructors
    public UserPlaylist() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.lastModified = LocalDateTime.now();
    }
    
    public UserPlaylist(User user, String name) {
        this();
        this.user = user;
        this.name = name;
    }
    
    public UserPlaylist(User user, String name, PlaylistType playlistType) {
        this(user, name);
        this.playlistType = playlistType;
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
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public PlaylistType getPlaylistType() {
        return playlistType;
    }
    
    public void setPlaylistType(PlaylistType playlistType) {
        this.playlistType = playlistType;
    }
    
    public Boolean getIsPublic() {
        return isPublic;
    }
    
    public void setIsPublic(Boolean isPublic) {
        this.isPublic = isPublic;
    }
    
    public Boolean getIsCollaborative() {
        return isCollaborative;
    }
    
    public void setIsCollaborative(Boolean isCollaborative) {
        this.isCollaborative = isCollaborative;
    }
    
    public RecommendationCategory getRecommendationCategory() {
        return recommendationCategory;
    }
    
    public void setRecommendationCategory(RecommendationCategory recommendationCategory) {
        this.recommendationCategory = recommendationCategory;
    }
    
    public Double getDiversityScore() {
        return diversityScore;
    }
    
    public void setDiversityScore(Double diversityScore) {
        this.diversityScore = diversityScore;
    }
    
    public Double getNoveltyScore() {
        return noveltyScore;
    }
    
    public void setNoveltyScore(Double noveltyScore) {
        this.noveltyScore = noveltyScore;
    }
    
    public Double getExplorationLevel() {
        return explorationLevel;
    }
    
    public void setExplorationLevel(Double explorationLevel) {
        this.explorationLevel = explorationLevel;
    }
    
    public List<Track> getTracks() {
        return tracks;
    }
    
    public void setTracks(List<Track> tracks) {
        this.tracks = tracks;
        updateTrackCount();
        updateTotalDuration();
    }
    
    public Long getTotalDurationMs() {
        return totalDurationMs;
    }
    
    public void setTotalDurationMs(Long totalDurationMs) {
        this.totalDurationMs = totalDurationMs;
    }
    
    public Integer getTrackCount() {
        return trackCount;
    }
    
    public void setTrackCount(Integer trackCount) {
        this.trackCount = trackCount;
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
    
    public LocalDateTime getLastModified() {
        return lastModified;
    }
    
    public void setLastModified(LocalDateTime lastModified) {
        this.lastModified = lastModified;
    }
    
    // Utility Methods
    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
        this.lastModified = LocalDateTime.now();
    }
    
    /**
     * Add a track to the playlist
     */
    public void addTrack(Track track) {
        if (!tracks.contains(track)) {
            tracks.add(track);
            updateTrackCount();
            updateTotalDuration();
        }
    }
    
    /**
     * Remove a track from the playlist
     */
    public void removeTrack(Track track) {
        if (tracks.remove(track)) {
            updateTrackCount();
            updateTotalDuration();
        }
    }
    
    /**
     * Add multiple tracks to the playlist
     */
    public void addTracks(List<Track> newTracks) {
        for (Track track : newTracks) {
            if (!tracks.contains(track)) {
                tracks.add(track);
            }
        }
        updateTrackCount();
        updateTotalDuration();
    }
    
    /**
     * Clear all tracks from the playlist
     */
    public void clearTracks() {
        tracks.clear();
        updateTrackCount();
        updateTotalDuration();
    }
    
    /**
     * Update track count
     */
    private void updateTrackCount() {
        this.trackCount = tracks.size();
    }
    
    /**
     * Update total duration
     */
    private void updateTotalDuration() {
        this.totalDurationMs = tracks.stream()
                .mapToLong(track -> track.getDurationMs() != null ? track.getDurationMs() : 0L)
                .sum();
    }
    
    /**
     * Calculate playlist diversity score
     */
    public double calculateDiversityScore() {
        if (tracks.isEmpty()) {
            return 0.0;
        }
        
        // Count unique artists
        Set<String> artists = tracks.stream()
                .map(Track::getArtist)
                .collect(HashSet::new, HashSet::add, HashSet::addAll);
        
        // Count unique genres
        Set<String> genres = tracks.stream()
                .map(Track::getGenre)
                .filter(Objects::nonNull)
                .collect(HashSet::new, HashSet::add, HashSet::addAll);
        
        // Calculate diversity as ratio of unique items to total items
        double artistDiversity = (double) artists.size() / tracks.size();
        double genreDiversity = genres.isEmpty() ? 0.0 : (double) genres.size() / tracks.size();
        
        return (artistDiversity + genreDiversity) / 2.0;
    }
    
    /**
     * Calculate playlist novelty score
     */
    public double calculateNoveltyScore() {
        if (tracks.isEmpty()) {
            return 0.0;
        }
        
        return tracks.stream()
                .mapToDouble(track -> track.getNoveltyScore() != null ? track.getNoveltyScore() : 0.0)
                .average()
                .orElse(0.0);
    }
    
    /**
     * Check if this is a system-generated recommendation playlist
     */
    public boolean isSystemRecommendation() {
        return playlistType == PlaylistType.SYSTEM_RECOMMENDATION ||
               playlistType == PlaylistType.DISCOVERY_PLAYLIST ||
               playlistType == PlaylistType.MOOD_BASED ||
               playlistType == PlaylistType.ACTIVITY_BASED;
    }
    
    /**
     * Get playlist duration in a readable format
     */
    public String getFormattedDuration() {
        if (totalDurationMs == null || totalDurationMs == 0) {
            return "0:00";
        }
        
        long totalSeconds = totalDurationMs / 1000;
        long hours = totalSeconds / 3600;
        long minutes = (totalSeconds % 3600) / 60;
        long seconds = totalSeconds % 60;
        
        if (hours > 0) {
            return String.format("%d:%02d:%02d", hours, minutes, seconds);
        } else {
            return String.format("%d:%02d", minutes, seconds);
        }
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        UserPlaylist that = (UserPlaylist) o;
        return Objects.equals(id, that.id);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
    
    @Override
    public String toString() {
        return "UserPlaylist{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", playlistType=" + playlistType +
                ", recommendationCategory=" + recommendationCategory +
                ", trackCount=" + trackCount +
                ", diversityScore=" + diversityScore +
                ", noveltyScore=" + noveltyScore +
                '}';
    }
} 