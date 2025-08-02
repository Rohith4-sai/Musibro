package com.musicrecommendation.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.*;

/**
 * Entity representing a user with their preferences, listening history,
 * and context information for personalized music recommendations.
 */
@Entity
@Table(name = "users")
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "spotify_user_id", unique = true)
    private String spotifyUserId;
    
    @Column(name = "display_name")
    private String displayName;
    
    @Column(name = "email")
    private String email;
    
    @Column(name = "profile_image_url")
    private String profileImageUrl;
    
    // User Preferences
    @Column(name = "exploration_level")
    private Double explorationLevel = 0.3; // 0.0 to 1.0
    
    @Column(name = "diversity_preference")
    private Double diversityPreference = 0.5; // 0.0 to 1.0
    
    @Column(name = "novelty_preference")
    private Double noveltyPreference = 0.4; // 0.0 to 1.0
    
    @ElementCollection
    @CollectionTable(name = "user_preferred_genres", 
                    joinColumns = @JoinColumn(name = "user_id"))
    @Column(name = "genre")
    private Set<String> preferredGenres = new HashSet<>();
    
    @ElementCollection
    @CollectionTable(name = "user_preferred_artists", 
                    joinColumns = @JoinColumn(name = "user_id"))
    @Column(name = "artist")
    private Set<String> preferredArtists = new HashSet<>();
    
    // Context Information
    @Column(name = "current_mood")
    @Enumerated(EnumType.STRING)
    private Mood currentMood = Mood.NEUTRAL;
    
    @Column(name = "current_activity")
    @Enumerated(EnumType.STRING)
    private Activity currentActivity = Activity.GENERAL;
    
    @Column(name = "time_of_day")
    @Enumerated(EnumType.STRING)
    private TimeOfDay timeOfDay = TimeOfDay.DAY;
    
    // Listening History
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<UserTrackInteraction> trackInteractions = new ArrayList<>();
    
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<UserPlaylist> playlists = new ArrayList<>();
    
    // Analytics
    @Column(name = "total_listening_time_ms")
    private Long totalListeningTimeMs = 0L;
    
    @Column(name = "tracks_discovered")
    private Integer tracksDiscovered = 0;
    
    @Column(name = "new_artists_discovered")
    private Integer newArtistsDiscovered = 0;
    
    @Column(name = "diversity_score")
    private Double diversityScore = 0.0;
    
    @Column(name = "exploration_score")
    private Double explorationScore = 0.0;
    
    // Metadata
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @Column(name = "last_active")
    private LocalDateTime lastActive;
    
    // Enums for context
    public enum Mood {
        HAPPY, SAD, ENERGETIC, CALM, FOCUSED, PARTY, ROMANTIC, NEUTRAL
    }
    
    public enum Activity {
        WORKING, EXERCISING, STUDYING, RELAXING, COMMUTING, SOCIALIZING, GENERAL
    }
    
    public enum TimeOfDay {
        MORNING, DAY, EVENING, NIGHT
    }
    
    // Constructors
    public User() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.lastActive = LocalDateTime.now();
    }
    
    public User(String spotifyUserId, String displayName) {
        this();
        this.spotifyUserId = spotifyUserId;
        this.displayName = displayName;
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getSpotifyUserId() {
        return spotifyUserId;
    }
    
    public void setSpotifyUserId(String spotifyUserId) {
        this.spotifyUserId = spotifyUserId;
    }
    
    public String getDisplayName() {
        return displayName;
    }
    
    public void setDisplayName(String displayName) {
        this.displayName = displayName;
    }
    
    public String getEmail() {
        return email;
    }
    
    public void setEmail(String email) {
        this.email = email;
    }
    
    public String getProfileImageUrl() {
        return profileImageUrl;
    }
    
    public void setProfileImageUrl(String profileImageUrl) {
        this.profileImageUrl = profileImageUrl;
    }
    
    public Double getExplorationLevel() {
        return explorationLevel;
    }
    
    public void setExplorationLevel(Double explorationLevel) {
        this.explorationLevel = Math.max(0.0, Math.min(1.0, explorationLevel));
    }
    
    public Double getDiversityPreference() {
        return diversityPreference;
    }
    
    public void setDiversityPreference(Double diversityPreference) {
        this.diversityPreference = Math.max(0.0, Math.min(1.0, diversityPreference));
    }
    
    public Double getNoveltyPreference() {
        return noveltyPreference;
    }
    
    public void setNoveltyPreference(Double noveltyPreference) {
        this.noveltyPreference = Math.max(0.0, Math.min(1.0, noveltyPreference));
    }
    
    public Set<String> getPreferredGenres() {
        return preferredGenres;
    }
    
    public void setPreferredGenres(Set<String> preferredGenres) {
        this.preferredGenres = preferredGenres;
    }
    
    public Set<String> getPreferredArtists() {
        return preferredArtists;
    }
    
    public void setPreferredArtists(Set<String> preferredArtists) {
        this.preferredArtists = preferredArtists;
    }
    
    public Mood getCurrentMood() {
        return currentMood;
    }
    
    public void setCurrentMood(Mood currentMood) {
        this.currentMood = currentMood;
    }
    
    public Activity getCurrentActivity() {
        return currentActivity;
    }
    
    public void setCurrentActivity(Activity currentActivity) {
        this.currentActivity = currentActivity;
    }
    
    public TimeOfDay getTimeOfDay() {
        return timeOfDay;
    }
    
    public void setTimeOfDay(TimeOfDay timeOfDay) {
        this.timeOfDay = timeOfDay;
    }
    
    public List<UserTrackInteraction> getTrackInteractions() {
        return trackInteractions;
    }
    
    public void setTrackInteractions(List<UserTrackInteraction> trackInteractions) {
        this.trackInteractions = trackInteractions;
    }
    
    public List<UserPlaylist> getPlaylists() {
        return playlists;
    }
    
    public void setPlaylists(List<UserPlaylist> playlists) {
        this.playlists = playlists;
    }
    
    public Long getTotalListeningTimeMs() {
        return totalListeningTimeMs;
    }
    
    public void setTotalListeningTimeMs(Long totalListeningTimeMs) {
        this.totalListeningTimeMs = totalListeningTimeMs;
    }
    
    public Integer getTracksDiscovered() {
        return tracksDiscovered;
    }
    
    public void setTracksDiscovered(Integer tracksDiscovered) {
        this.tracksDiscovered = tracksDiscovered;
    }
    
    public Integer getNewArtistsDiscovered() {
        return newArtistsDiscovered;
    }
    
    public void setNewArtistsDiscovered(Integer newArtistsDiscovered) {
        this.newArtistsDiscovered = newArtistsDiscovered;
    }
    
    public Double getDiversityScore() {
        return diversityScore;
    }
    
    public void setDiversityScore(Double diversityScore) {
        this.diversityScore = Math.max(0.0, Math.min(1.0, diversityScore));
    }
    
    public Double getExplorationScore() {
        return explorationScore;
    }
    
    public void setExplorationScore(Double explorationScore) {
        this.explorationScore = Math.max(0.0, Math.min(1.0, explorationScore));
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
    
    public LocalDateTime getLastActive() {
        return lastActive;
    }
    
    public void setLastActive(LocalDateTime lastActive) {
        this.lastActive = lastActive;
    }
    
    // Utility Methods
    @PreUpdate
    public void preUpdate() {
        this.updatedAt = LocalDateTime.now();
        this.lastActive = LocalDateTime.now();
    }
    
    /**
     * Add a genre to user preferences
     */
    public void addPreferredGenre(String genre) {
        this.preferredGenres.add(genre.toLowerCase());
    }
    
    /**
     * Add an artist to user preferences
     */
    public void addPreferredArtist(String artist) {
        this.preferredArtists.add(artist.toLowerCase());
    }
    
    /**
     * Get liked tracks from interactions
     */
    public List<Track> getLikedTracks() {
        return trackInteractions.stream()
                .filter(interaction -> interaction.getRating() >= 4)
                .map(UserTrackInteraction::getTrack)
                .toList();
    }
    
    /**
     * Get disliked tracks from interactions
     */
    public List<Track> getDislikedTracks() {
        return trackInteractions.stream()
                .filter(interaction -> interaction.getRating() <= 2)
                .map(UserTrackInteraction::getTrack)
                .toList();
    }
    
    /**
     * Get recently played tracks
     */
    public List<Track> getRecentlyPlayedTracks(int limit) {
        return trackInteractions.stream()
                .sorted(Comparator.comparing(UserTrackInteraction::getLastPlayedAt).reversed())
                .limit(limit)
                .map(UserTrackInteraction::getTrack)
                .toList();
    }
    
    /**
     * Calculate user's overall preference profile
     */
    public Map<String, Double> getPreferenceProfile() {
        Map<String, Double> profile = new HashMap<>();
        
        // Context weights
        profile.put("mood_" + currentMood.name().toLowerCase(), 1.0);
        profile.put("activity_" + currentActivity.name().toLowerCase(), 1.0);
        profile.put("time_" + timeOfDay.name().toLowerCase(), 1.0);
        
        // User preferences
        profile.put("exploration", explorationLevel);
        profile.put("diversity", diversityPreference);
        profile.put("novelty", noveltyPreference);
        
        return profile;
    }
    
    /**
     * Update user statistics after discovering new content
     */
    public void recordDiscovery(Track track, boolean isNewArtist) {
        this.tracksDiscovered++;
        if (isNewArtist) {
            this.newArtistsDiscovered++;
        }
        this.lastActive = LocalDateTime.now();
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return Objects.equals(spotifyUserId, user.spotifyUserId);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(spotifyUserId);
    }
    
    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", spotifyUserId='" + spotifyUserId + '\'' +
                ", displayName='" + displayName + '\'' +
                ", explorationLevel=" + explorationLevel +
                ", diversityPreference=" + diversityPreference +
                ", noveltyPreference=" + noveltyPreference +
                ", currentMood=" + currentMood +
                ", currentActivity=" + currentActivity +
                ", tracksDiscovered=" + tracksDiscovered +
                ", newArtistsDiscovered=" + newArtistsDiscovered +
                '}';
    }
} 