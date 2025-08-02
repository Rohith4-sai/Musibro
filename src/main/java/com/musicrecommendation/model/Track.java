package com.musicrecommendation.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.Objects;

/**
 * Entity representing a music track with comprehensive metadata and audio features.
 * This model supports bias-resistant recommendation algorithms by including
 * popularity metrics, diversity indicators, and novelty scores.
 */
@Entity
@Table(name = "tracks")
public class Track {
    
    @Id
    @Column(name = "spotify_id")
    private String spotifyId;
    
    @Column(nullable = false)
    private String name;
    
    @Column(nullable = false)
    private String artist;
    
    @Column
    private String album;
    
    @Column
    private String genre;
    
    // Audio Features (0.0 to 1.0 scale)
    @Column(name = "acousticness")
    private Double acousticness;
    
    @Column(name = "danceability")
    private Double danceability;
    
    @Column(name = "energy")
    private Double energy;
    
    @Column(name = "instrumentalness")
    private Double instrumentalness;
    
    @Column(name = "key")
    private Integer key;
    
    @Column(name = "liveness")
    private Double liveness;
    
    @Column(name = "loudness")
    private Double loudness;
    
    @Column(name = "mode")
    private Integer mode;
    
    @Column(name = "speechiness")
    private Double speechiness;
    
    @Column(name = "tempo")
    private Double tempo;
    
    @Column(name = "time_signature")
    private Integer timeSignature;
    
    @Column(name = "valence")
    private Double valence;
    
    // Popularity and Bias Metrics
    @Column(name = "spotify_popularity")
    private Integer spotifyPopularity;
    
    @Column(name = "popularity_bias_score")
    private Double popularityBiasScore;
    
    @Column(name = "novelty_score")
    private Double noveltyScore;
    
    @Column(name = "diversity_score")
    private Double diversityScore;
    
    @Column(name = "artist_popularity")
    private Integer artistPopularity;
    
    @Column(name = "is_independent")
    private Boolean isIndependent;
    
    // Metadata
    @Column(name = "duration_ms")
    private Long durationMs;
    
    @Column(name = "preview_url")
    private String previewUrl;
    
    @Column(name = "external_url")
    private String externalUrl;
    
    @Column(name = "image_url")
    private String imageUrl;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Constructors
    public Track() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }
    
    public Track(String spotifyId, String name, String artist) {
        this();
        this.spotifyId = spotifyId;
        this.name = name;
        this.artist = artist;
    }
    
    // Getters and Setters
    public String getSpotifyId() {
        return spotifyId;
    }
    
    public void setSpotifyId(String spotifyId) {
        this.spotifyId = spotifyId;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getArtist() {
        return artist;
    }
    
    public void setArtist(String artist) {
        this.artist = artist;
    }
    
    public String getAlbum() {
        return album;
    }
    
    public void setAlbum(String album) {
        this.album = album;
    }
    
    public String getGenre() {
        return genre;
    }
    
    public void setGenre(String genre) {
        this.genre = genre;
    }
    
    public Double getAcousticness() {
        return acousticness;
    }
    
    public void setAcousticness(Double acousticness) {
        this.acousticness = acousticness;
    }
    
    public Double getDanceability() {
        return danceability;
    }
    
    public void setDanceability(Double danceability) {
        this.danceability = danceability;
    }
    
    public Double getEnergy() {
        return energy;
    }
    
    public void setEnergy(Double energy) {
        this.energy = energy;
    }
    
    public Double getInstrumentalness() {
        return instrumentalness;
    }
    
    public void setInstrumentalness(Double instrumentalness) {
        this.instrumentalness = instrumentalness;
    }
    
    public Integer getKey() {
        return key;
    }
    
    public void setKey(Integer key) {
        this.key = key;
    }
    
    public Double getLiveness() {
        return liveness;
    }
    
    public void setLiveness(Double liveness) {
        this.liveness = liveness;
    }
    
    public Double getLoudness() {
        return loudness;
    }
    
    public void setLoudness(Double loudness) {
        this.loudness = loudness;
    }
    
    public Integer getMode() {
        return mode;
    }
    
    public void setMode(Integer mode) {
        this.mode = mode;
    }
    
    public Double getSpeechiness() {
        return speechiness;
    }
    
    public void setSpeechiness(Double speechiness) {
        this.speechiness = speechiness;
    }
    
    public Double getTempo() {
        return tempo;
    }
    
    public void setTempo(Double tempo) {
        this.tempo = tempo;
    }
    
    public Integer getTimeSignature() {
        return timeSignature;
    }
    
    public void setTimeSignature(Integer timeSignature) {
        this.timeSignature = timeSignature;
    }
    
    public Double getValence() {
        return valence;
    }
    
    public void setValence(Double valence) {
        this.valence = valence;
    }
    
    public Integer getSpotifyPopularity() {
        return spotifyPopularity;
    }
    
    public void setSpotifyPopularity(Integer spotifyPopularity) {
        this.spotifyPopularity = spotifyPopularity;
    }
    
    public Double getPopularityBiasScore() {
        return popularityBiasScore;
    }
    
    public void setPopularityBiasScore(Double popularityBiasScore) {
        this.popularityBiasScore = popularityBiasScore;
    }
    
    public Double getNoveltyScore() {
        return noveltyScore;
    }
    
    public void setNoveltyScore(Double noveltyScore) {
        this.noveltyScore = noveltyScore;
    }
    
    public Double getDiversityScore() {
        return diversityScore;
    }
    
    public void setDiversityScore(Double diversityScore) {
        this.diversityScore = diversityScore;
    }
    
    public Integer getArtistPopularity() {
        return artistPopularity;
    }
    
    public void setArtistPopularity(Integer artistPopularity) {
        this.artistPopularity = artistPopularity;
    }
    
    public Boolean getIsIndependent() {
        return isIndependent;
    }
    
    public void setIsIndependent(Boolean isIndependent) {
        this.isIndependent = isIndependent;
    }
    
    public Long getDurationMs() {
        return durationMs;
    }
    
    public void setDurationMs(Long durationMs) {
        this.durationMs = durationMs;
    }
    
    public String getPreviewUrl() {
        return previewUrl;
    }
    
    public void setPreviewUrl(String previewUrl) {
        this.previewUrl = previewUrl;
    }
    
    public String getExternalUrl() {
        return externalUrl;
    }
    
    public void setExternalUrl(String externalUrl) {
        this.externalUrl = externalUrl;
    }
    
    public String getImageUrl() {
        return imageUrl;
    }
    
    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
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
     * Calculate the overall bias-resistant score for this track
     * @return A score between 0.0 and 1.0 indicating how bias-resistant this track is
     */
    public double calculateBiasResistantScore() {
        double score = 0.0;
        int factors = 0;
        
        if (popularityBiasScore != null) {
            score += popularityBiasScore;
            factors++;
        }
        
        if (noveltyScore != null) {
            score += noveltyScore;
            factors++;
        }
        
        if (diversityScore != null) {
            score += diversityScore;
            factors++;
        }
        
        if (isIndependent != null && isIndependent) {
            score += 0.8; // Bonus for independent artists
            factors++;
        }
        
        return factors > 0 ? score / factors : 0.0;
    }
    
    /**
     * Get a feature vector for content-based filtering
     * @return Array of audio features
     */
    public double[] getFeatureVector() {
        return new double[]{
            acousticness != null ? acousticness : 0.0,
            danceability != null ? danceability : 0.0,
            energy != null ? energy : 0.0,
            instrumentalness != null ? instrumentalness : 0.0,
            liveness != null ? liveness : 0.0,
            speechiness != null ? speechiness : 0.0,
            valence != null ? valence : 0.0,
            tempo != null ? (tempo / 200.0) : 0.0, // Normalize tempo
            loudness != null ? ((loudness + 60) / 60.0) : 0.0 // Normalize loudness
        };
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Track track = (Track) o;
        return Objects.equals(spotifyId, track.spotifyId);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(spotifyId);
    }
    
    @Override
    public String toString() {
        return "Track{" +
                "spotifyId='" + spotifyId + '\'' +
                ", name='" + name + '\'' +
                ", artist='" + artist + '\'' +
                ", album='" + album + '\'' +
                ", genre='" + genre + '\'' +
                ", spotifyPopularity=" + spotifyPopularity +
                ", biasResistantScore=" + calculateBiasResistantScore() +
                '}';
    }
} 