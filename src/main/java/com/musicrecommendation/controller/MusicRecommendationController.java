package com.musicrecommendation.controller;

import com.musicrecommendation.ml.HybridRecommendationSystem;
import com.musicrecommendation.ml.TrackRecommendation;
import com.musicrecommendation.model.Track;
import com.musicrecommendation.model.User;
import com.musicrecommendation.spotify.SpotifyService;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpSession;
import java.util.List;
import java.util.Map;

/**
 * Main controller for the music recommendation application.
 * Handles web requests for authentication, recommendations, and user interactions.
 */
@Controller
public class MusicRecommendationController {
    
    private static final Logger logger = LoggerFactory.getLogger(MusicRecommendationController.class);
    
    @Autowired
    private SpotifyService spotifyService;
    
    @Autowired
    private HybridRecommendationSystem recommendationSystem;
    
    /**
     * Home page
     */
    @GetMapping("/")
    public String home(Model model, HttpSession session) {
        User user = (User) session.getAttribute("user");
        model.addAttribute("user", user);
        model.addAttribute("isAuthenticated", user != null);
        return "index";
    }
    
    /**
     * Login page
     */
    @GetMapping("/login")
    public String login(Model model) {
        String authUrl = spotifyService.getAuthorizationUrl();
        model.addAttribute("authUrl", authUrl);
        return "login";
    }
    
    /**
     * Spotify OAuth callback
     */
    @GetMapping("/callback")
    public String callback(@RequestParam("code") String code, HttpSession session, Model model) {
        try {
            // Exchange code for access token
            Map<String, Object> credentials = spotifyService.getAccessToken(code);
            String accessToken = (String) credentials.get("access_token");
            
            // Get user profile
            User user = spotifyService.getCurrentUser();
            session.setAttribute("user", user);
            session.setAttribute("accessToken", accessToken);
            
            logger.info("User authenticated: {}", user.getDisplayName());
            
            return "redirect:/dashboard";
        } catch (Exception e) {
            logger.error("Authentication failed: {}", e.getMessage());
            model.addAttribute("error", "Authentication failed: " + e.getMessage());
            return "login";
        }
    }
    
    /**
     * Dashboard page
     */
    @GetMapping("/dashboard")
    public String dashboard(Model model, HttpSession session) {
        User user = (User) session.getAttribute("user");
        if (user == null) {
            return "redirect:/login";
        }
        
        model.addAttribute("user", user);
        return "dashboard";
    }
    
    /**
     * Get recommendations
     */
    @GetMapping("/recommendations")
    public String getRecommendations(@RequestParam(defaultValue = "FOR_YOU") String type,
                                   Model model, HttpSession session) {
        User user = (User) session.getAttribute("user");
        if (user == null) {
            return "redirect:/login";
        }
        
        try {
            // Get user's top tracks as seed data
            List<Track> seedTracks = spotifyService.getUserTopTracks(10);
            
            // Generate recommendations
            HybridRecommendationSystem.RecommendationType recommendationType = 
                    HybridRecommendationSystem.RecommendationType.valueOf(type);
            
            List<TrackRecommendation> recommendations = recommendationSystem.generateRecommendations(
                    user, seedTracks, recommendationType);
            
            model.addAttribute("recommendations", recommendations);
            model.addAttribute("recommendationType", type);
            model.addAttribute("user", user);
            
            return "recommendations";
        } catch (Exception e) {
            logger.error("Error generating recommendations: {}", e.getMessage());
            model.addAttribute("error", "Failed to generate recommendations: " + e.getMessage());
            return "dashboard";
        }
    }
    
    /**
     * Search tracks
     */
    @GetMapping("/search")
    public String searchTracks(@RequestParam String query, Model model, HttpSession session) {
        User user = (User) session.getAttribute("user");
        if (user == null) {
            return "redirect:/login";
        }
        
        try {
            List<Track> tracks = spotifyService.searchTracks(query, 20);
            model.addAttribute("tracks", tracks);
            model.addAttribute("query", query);
            model.addAttribute("user", user);
            
            return "search";
        } catch (Exception e) {
            logger.error("Error searching tracks: {}", e.getMessage());
            model.addAttribute("error", "Search failed: " + e.getMessage());
            return "dashboard";
        }
    }
    
    /**
     * Get track details
     */
    @GetMapping("/track/{trackId}")
    public String getTrackDetails(@PathVariable String trackId, Model model, HttpSession session) {
        User user = (User) session.getAttribute("user");
        if (user == null) {
            return "redirect:/login";
        }
        
        try {
            Track track = spotifyService.getTrack(trackId);
            model.addAttribute("track", track);
            model.addAttribute("user", user);
            
            return "track-details";
        } catch (Exception e) {
            logger.error("Error getting track details: {}", e.getMessage());
            model.addAttribute("error", "Failed to get track details: " + e.getMessage());
            return "dashboard";
        }
    }
    
    /**
     * Rate a track
     */
    @PostMapping("/rate-track")
    @ResponseBody
    public Map<String, Object> rateTrack(@RequestParam String trackId, 
                                        @RequestParam int rating,
                                        HttpSession session) {
        User user = (User) session.getAttribute("user");
        if (user == null) {
            return Map.of("success", false, "error", "User not authenticated");
        }
        
        try {
            // In a real application, you would save this to the database
            logger.info("User {} rated track {} with rating {}", user.getDisplayName(), trackId, rating);
            
            return Map.of("success", true, "message", "Rating saved successfully");
        } catch (Exception e) {
            logger.error("Error saving rating: {}", e.getMessage());
            return Map.of("success", false, "error", "Failed to save rating");
        }
    }
    
    /**
     * Like a track
     */
    @PostMapping("/like-track")
    @ResponseBody
    public Map<String, Object> likeTrack(@RequestParam String trackId, HttpSession session) {
        User user = (User) session.getAttribute("user");
        if (user == null) {
            return Map.of("success", false, "error", "User not authenticated");
        }
        
        try {
            // In a real application, you would save this to the database
            logger.info("User {} liked track {}", user.getDisplayName(), trackId);
            
            return Map.of("success", true, "message", "Track liked successfully");
        } catch (Exception e) {
            logger.error("Error liking track: {}", e.getMessage());
            return Map.of("success", false, "error", "Failed to like track");
        }
    }
    
    /**
     * Dislike a track
     */
    @PostMapping("/dislike-track")
    @ResponseBody
    public Map<String, Object> dislikeTrack(@RequestParam String trackId, HttpSession session) {
        User user = (User) session.getAttribute("user");
        if (user == null) {
            return Map.of("success", false, "error", "User not authenticated");
        }
        
        try {
            // In a real application, you would save this to the database
            logger.info("User {} disliked track {}", user.getDisplayName(), trackId);
            
            return Map.of("success", true, "message", "Track disliked successfully");
        } catch (Exception e) {
            logger.error("Error disliking track: {}", e.getMessage());
            return Map.of("success", false, "error", "Failed to dislike track");
        }
    }
    
    /**
     * Update user preferences
     */
    @PostMapping("/update-preferences")
    @ResponseBody
    public Map<String, Object> updatePreferences(@RequestParam Double explorationLevel,
                                                @RequestParam Double diversityPreference,
                                                @RequestParam Double noveltyPreference,
                                                HttpSession session) {
        User user = (User) session.getAttribute("user");
        if (user == null) {
            return Map.of("success", false, "error", "User not authenticated");
        }
        
        try {
            user.setExplorationLevel(explorationLevel);
            user.setDiversityPreference(diversityPreference);
            user.setNoveltyPreference(noveltyPreference);
            
            // In a real application, you would save this to the database
            logger.info("User {} updated preferences: exploration={}, diversity={}, novelty={}", 
                    user.getDisplayName(), explorationLevel, diversityPreference, noveltyPreference);
            
            return Map.of("success", true, "message", "Preferences updated successfully");
        } catch (Exception e) {
            logger.error("Error updating preferences: {}", e.getMessage());
            return Map.of("success", false, "error", "Failed to update preferences");
        }
    }
    
    /**
     * Update user context
     */
    @PostMapping("/update-context")
    @ResponseBody
    public Map<String, Object> updateContext(@RequestParam String mood,
                                            @RequestParam String activity,
                                            HttpSession session) {
        User user = (User) session.getAttribute("user");
        if (user == null) {
            return Map.of("success", false, "error", "User not authenticated");
        }
        
        try {
            user.setCurrentMood(User.Mood.valueOf(mood.toUpperCase()));
            user.setCurrentActivity(User.Activity.valueOf(activity.toUpperCase()));
            
            // In a real application, you would save this to the database
            logger.info("User {} updated context: mood={}, activity={}", 
                    user.getDisplayName(), mood, activity);
            
            return Map.of("success", true, "message", "Context updated successfully");
        } catch (Exception e) {
            logger.error("Error updating context: {}", e.getMessage());
            return Map.of("success", false, "error", "Failed to update context");
        }
    }
    
    /**
     * Logout
     */
    @GetMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/";
    }
    
    /**
     * Error page
     */
    @GetMapping("/error")
    public String error(Model model) {
        model.addAttribute("error", "An error occurred");
        return "error";
    }
} 