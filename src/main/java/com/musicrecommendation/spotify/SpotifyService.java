package com.musicrecommendation.spotify;

import com.musicrecommendation.model.Track;
import com.musicrecommendation.model.User;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.*;

/**
 * Simplified Spotify service for demo purposes.
 * In a real implementation, this would integrate with the Spotify Web API.
 */
@Service
public class SpotifyService {
    
    private static final Logger logger = LoggerFactory.getLogger(SpotifyService.class);
    
    @Value("${spotify.client.id:demo}")
    private String clientId;
    
    @Value("${spotify.client.secret:demo}")
    private String clientSecret;
    
    @Value("${spotify.client.redirect-uri:http://localhost:8080/callback}")
    private String redirectUri;
    
    /**
     * Get authorization URL for user login
     */
    public String getAuthorizationUrl() {
        return "https://accounts.spotify.com/authorize?client_id=" + clientId + 
               "&response_type=code&redirect_uri=" + redirectUri + 
               "&scope=user-read-private,user-read-email,user-top-read";
    }
    
    /**
     * Mock access token exchange
     */
    public Map<String, Object> getAccessToken(String code) {
        Map<String, Object> credentials = new HashMap<>();
        credentials.put("access_token", "mock_access_token_" + System.currentTimeMillis());
        credentials.put("refresh_token", "mock_refresh_token");
        credentials.put("expires_in", 3600);
        return credentials;
    }
    
    /**
     * Get current user profile (mock data)
     */
    public User getCurrentUser() {
        User user = new User();
        user.setSpotifyUserId("demo_user_123");
        user.setDisplayName("Demo User");
        user.setEmail("demo@example.com");
        return user;
    }
    
    /**
     * Search for tracks (mock data)
     */
    public List<Track> searchTracks(String query, int limit) {
        List<Track> tracks = new ArrayList<>();
        
        // Generate mock tracks based on search query
        for (int i = 1; i <= Math.min(limit, 10); i++) {
            Track track = new Track();
            track.setSpotifyId("track_" + i);
            track.setName(query + " Song " + i);
            track.setArtist("Artist " + i);
            track.setAlbum("Album " + i);
            track.setSpotifyPopularity(70 + (i * 3));
            track.setGenre("Pop");
            track.setExternalUrl("https://open.spotify.com/track/track_" + i);
            track.setImageUrl("https://via.placeholder.com/300x300?text=Album+" + i);
            
            // Mock audio features
            track.setAcousticness(0.1 + (i * 0.05));
            track.setDanceability(0.5 + (i * 0.03));
            track.setEnergy(0.6 + (i * 0.02));
            track.setInstrumentalness(0.1 + (i * 0.01));
            track.setLiveness(0.1 + (i * 0.02));
            track.setLoudness(-10.0 + (i * 0.5));
            track.setSpeechiness(0.05 + (i * 0.01));
            track.setTempo(120.0 + (i * 5));
            track.setValence(0.4 + (i * 0.03));
            
            tracks.add(track);
        }
        
        return tracks;
    }
    
    /**
     * Get user's top tracks (mock data)
     */
    public List<Track> getUserTopTracks(int limit) {
        List<Track> tracks = new ArrayList<>();
        
        String[] popularSongs = {
            "Bohemian Rhapsody", "Hotel California", "Stairway to Heaven", 
            "Imagine", "Hey Jude", "Yesterday", "Let It Be", "Wonderwall",
            "Smells Like Teen Spirit", "Sweet Child O' Mine"
        };
        
        String[] artists = {
            "Queen", "Eagles", "Led Zeppelin", "John Lennon", "The Beatles",
            "The Beatles", "The Beatles", "Oasis", "Nirvana", "Guns N' Roses"
        };
        
        for (int i = 0; i < Math.min(limit, popularSongs.length); i++) {
            Track track = new Track();
            track.setSpotifyId("top_track_" + i);
            track.setName(popularSongs[i]);
            track.setArtist(artists[i]);
            track.setAlbum("Greatest Hits " + (i + 1));
            track.setSpotifyPopularity(85 + (i * 2));
            track.setGenre("Rock");
            track.setExternalUrl("https://open.spotify.com/track/top_track_" + i);
            track.setImageUrl("https://via.placeholder.com/300x300?text=" + popularSongs[i].replace(" ", "+"));
            
            // Mock audio features
            track.setAcousticness(0.2 + (i * 0.03));
            track.setDanceability(0.4 + (i * 0.04));
            track.setEnergy(0.7 + (i * 0.02));
            track.setInstrumentalness(0.1 + (i * 0.01));
            track.setLiveness(0.1 + (i * 0.02));
            track.setLoudness(-8.0 + (i * 0.3));
            track.setSpeechiness(0.03 + (i * 0.01));
            track.setTempo(110.0 + (i * 8));
            track.setValence(0.5 + (i * 0.02));
            
            tracks.add(track);
        }
        
        return tracks;
    }
    
    /**
     * Get a specific track by ID (mock data)
     */
    public Track getTrack(String trackId) {
        Track track = new Track();
        track.setSpotifyId(trackId);
        track.setName("Sample Track");
        track.setArtist("Sample Artist");
        track.setAlbum("Sample Album");
        track.setSpotifyPopularity(75);
        track.setGenre("Pop");
        track.setExternalUrl("https://open.spotify.com/track/" + trackId);
        track.setImageUrl("https://via.placeholder.com/300x300?text=Sample+Track");
        
        // Mock audio features
        track.setAcousticness(0.3);
        track.setDanceability(0.6);
        track.setEnergy(0.7);
        track.setInstrumentalness(0.1);
        track.setLiveness(0.1);
        track.setLoudness(-9.0);
        track.setSpeechiness(0.05);
        track.setTempo(120.0);
        track.setValence(0.6);
        
        return track;
    }
    
    /**
     * Get multiple tracks by IDs (mock data)
     */
    public List<Track> getTracks(List<String> trackIds) {
        List<Track> tracks = new ArrayList<>();
        for (String trackId : trackIds) {
            tracks.add(getTrack(trackId));
        }
        return tracks;
    }
    
    /**
     * Get playlist tracks (mock data)
     */
    public List<Track> getPlaylistTracks(String playlistId, int limit) {
        return getUserTopTracks(limit); // Use same mock data for simplicity
    }
    
    /**
     * Check if access token is valid (always true for mock)
     */
    public boolean isAccessTokenValid() {
        return true;
    }
} 