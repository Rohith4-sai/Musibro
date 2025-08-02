package com.musicrecommendation.ml.context;

import com.musicrecommendation.ml.TrackRecommendation;
import com.musicrecommendation.model.Track;
import com.musicrecommendation.model.User;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.time.LocalTime;
import java.util.List;
import java.util.Map;

/**
 * Engine for applying contextual weights to recommendations based on
 * user's current mood, activity, and time of day.
 */
@Component
public class ContextEngine {
    
    private static final Logger logger = LoggerFactory.getLogger(ContextEngine.class);
    
    // Context weights from configuration
    private final Map<String, Double> moodWeights = Map.of(
        "happy", 1.2,
        "sad", 0.8,
        "energetic", 1.1,
        "calm", 0.9,
        "focused", 1.0,
        "party", 1.3,
        "romantic", 1.1
    );
    
    private final Map<String, Double> activityWeights = Map.of(
        "working", 0.9,
        "exercising", 1.2,
        "studying", 0.8,
        "relaxing", 1.0,
        "commuting", 1.1,
        "socializing", 1.2
    );
    
    /**
     * Apply context weights to recommendations based on user's current context
     */
    public List<TrackRecommendation> applyContextWeights(List<TrackRecommendation> recommendations, User user) {
        if (recommendations.isEmpty()) {
            return recommendations;
        }
        
        logger.debug("Applying context weights for user: {}", user.getDisplayName());
        
        // Get user's current context
        User.Mood currentMood = user.getCurrentMood();
        User.Activity currentActivity = user.getCurrentActivity();
        User.TimeOfDay timeOfDay = user.getTimeOfDay();
        
        // Apply context weights to each recommendation
        for (TrackRecommendation rec : recommendations) {
            double contextScore = calculateContextScore(rec.getTrack(), currentMood, currentActivity, timeOfDay);
            rec.setScore(rec.getScore() * contextScore);
        }
        
        return recommendations;
    }
    
    /**
     * Calculate context score for a track based on current context
     */
    private double calculateContextScore(Track track, User.Mood mood, User.Activity activity, User.TimeOfDay timeOfDay) {
        double score = 1.0; // Base score
        
        // Apply mood-based weights
        score *= calculateMoodScore(track, mood);
        
        // Apply activity-based weights
        score *= calculateActivityScore(track, activity);
        
        // Apply time-based weights
        score *= calculateTimeScore(track, timeOfDay);
        
        return score;
    }
    
    /**
     * Calculate mood-based score
     */
    private double calculateMoodScore(Track track, User.Mood mood) {
        if (mood == null) {
            return 1.0;
        }
        
        double score = 1.0;
        
        switch (mood) {
            case HAPPY -> {
                // Prefer high valence and energy
                if (track.getValence() != null && track.getValence() > 0.7) {
                    score *= 1.3;
                }
                if (track.getEnergy() != null && track.getEnergy() > 0.6) {
                    score *= 1.2;
                }
                if (track.getDanceability() != null && track.getDanceability() > 0.7) {
                    score *= 1.1;
                }
            }
            case SAD -> {
                // Prefer lower valence and acousticness
                if (track.getValence() != null && track.getValence() < 0.4) {
                    score *= 1.3;
                }
                if (track.getAcousticness() != null && track.getAcousticness() > 0.6) {
                    score *= 1.2;
                }
                if (track.getEnergy() != null && track.getEnergy() < 0.4) {
                    score *= 1.1;
                }
            }
            case ENERGETIC -> {
                // Prefer high energy and tempo
                if (track.getEnergy() != null && track.getEnergy() > 0.8) {
                    score *= 1.4;
                }
                if (track.getTempo() != null && track.getTempo() > 120) {
                    score *= 1.3;
                }
                if (track.getDanceability() != null && track.getDanceability() > 0.8) {
                    score *= 1.2;
                }
            }
            case CALM -> {
                // Prefer low energy and high acousticness
                if (track.getEnergy() != null && track.getEnergy() < 0.3) {
                    score *= 1.4;
                }
                if (track.getAcousticness() != null && track.getAcousticness() > 0.8) {
                    score *= 1.3;
                }
                if (track.getInstrumentalness() != null && track.getInstrumentalness() > 0.6) {
                    score *= 1.2;
                }
            }
            case FOCUSED -> {
                // Prefer instrumental and low speechiness
                if (track.getInstrumentalness() != null && track.getInstrumentalness() > 0.7) {
                    score *= 1.4;
                }
                if (track.getSpeechiness() != null && track.getSpeechiness() < 0.1) {
                    score *= 1.3;
                }
                if (track.getEnergy() != null && track.getEnergy() > 0.4 && track.getEnergy() < 0.7) {
                    score *= 1.2;
                }
            }
            case PARTY -> {
                // Prefer high danceability and energy
                if (track.getDanceability() != null && track.getDanceability() > 0.8) {
                    score *= 1.4;
                }
                if (track.getEnergy() != null && track.getEnergy() > 0.8) {
                    score *= 1.3;
                }
                if (track.getValence() != null && track.getValence() > 0.7) {
                    score *= 1.2;
                }
            }
            case ROMANTIC -> {
                // Prefer moderate valence and acousticness
                if (track.getValence() != null && track.getValence() > 0.5 && track.getValence() < 0.8) {
                    score *= 1.3;
                }
                if (track.getAcousticness() != null && track.getAcousticness() > 0.6) {
                    score *= 1.2;
                }
                if (track.getEnergy() != null && track.getEnergy() > 0.3 && track.getEnergy() < 0.6) {
                    score *= 1.1;
                }
            }
        }
        
        return score;
    }
    
    /**
     * Calculate activity-based score
     */
    private double calculateActivityScore(Track track, User.Activity activity) {
        if (activity == null) {
            return 1.0;
        }
        
        double score = 1.0;
        
        switch (activity) {
            case WORKING -> {
                // Prefer instrumental and low speechiness
                if (track.getInstrumentalness() != null && track.getInstrumentalness() > 0.8) {
                    score *= 1.4;
                }
                if (track.getSpeechiness() != null && track.getSpeechiness() < 0.05) {
                    score *= 1.3;
                }
                if (track.getEnergy() != null && track.getEnergy() > 0.3 && track.getEnergy() < 0.6) {
                    score *= 1.2;
                }
            }
            case EXERCISING -> {
                // Prefer high energy and tempo
                if (track.getEnergy() != null && track.getEnergy() > 0.8) {
                    score *= 1.4;
                }
                if (track.getTempo() != null && track.getTempo() > 120) {
                    score *= 1.3;
                }
                if (track.getDanceability() != null && track.getDanceability() > 0.7) {
                    score *= 1.2;
                }
            }
            case STUDYING -> {
                // Prefer instrumental and low energy
                if (track.getInstrumentalness() != null && track.getInstrumentalness() > 0.9) {
                    score *= 1.4;
                }
                if (track.getSpeechiness() != null && track.getSpeechiness() < 0.05) {
                    score *= 1.3;
                }
                if (track.getEnergy() != null && track.getEnergy() < 0.4) {
                    score *= 1.2;
                }
            }
            case RELAXING -> {
                // Prefer low energy and high acousticness
                if (track.getEnergy() != null && track.getEnergy() < 0.3) {
                    score *= 1.4;
                }
                if (track.getAcousticness() != null && track.getAcousticness() > 0.8) {
                    score *= 1.3;
                }
                if (track.getTempo() != null && track.getTempo() < 100) {
                    score *= 1.2;
                }
            }
            case COMMUTING -> {
                // Prefer moderate energy and danceability
                if (track.getEnergy() != null && track.getEnergy() > 0.5) {
                    score *= 1.3;
                }
                if (track.getDanceability() != null && track.getDanceability() > 0.6) {
                    score *= 1.2;
                }
                if (track.getValence() != null && track.getValence() > 0.5) {
                    score *= 1.1;
                }
            }
            case SOCIALIZING -> {
                // Prefer high danceability and valence
                if (track.getDanceability() != null && track.getDanceability() > 0.7) {
                    score *= 1.4;
                }
                if (track.getValence() != null && track.getValence() > 0.6) {
                    score *= 1.3;
                }
                if (track.getEnergy() != null && track.getEnergy() > 0.6) {
                    score *= 1.2;
                }
            }
        }
        
        return score;
    }
    
    /**
     * Calculate time-based score
     */
    private double calculateTimeScore(Track track, User.TimeOfDay timeOfDay) {
        if (timeOfDay == null) {
            return 1.0;
        }
        
        double score = 1.0;
        
        switch (timeOfDay) {
            case MORNING -> {
                // Prefer energetic and positive music
                if (track.getEnergy() != null && track.getEnergy() > 0.6) {
                    score *= 1.3;
                }
                if (track.getValence() != null && track.getValence() > 0.6) {
                    score *= 1.2;
                }
                if (track.getTempo() != null && track.getTempo() > 100) {
                    score *= 1.1;
                }
            }
            case DAY -> {
                // Neutral preferences, slight boost for moderate energy
                if (track.getEnergy() != null && track.getEnergy() > 0.4 && track.getEnergy() < 0.7) {
                    score *= 1.1;
                }
            }
            case EVENING -> {
                // Prefer relaxing and positive music
                if (track.getValence() != null && track.getValence() > 0.5) {
                    score *= 1.2;
                }
                if (track.getDanceability() != null && track.getDanceability() > 0.6) {
                    score *= 1.1;
                }
            }
            case NIGHT -> {
                // Prefer calm and low-energy music
                if (track.getEnergy() != null && track.getEnergy() < 0.4) {
                    score *= 1.3;
                }
                if (track.getAcousticness() != null && track.getAcousticness() > 0.6) {
                    score *= 1.2;
                }
                if (track.getTempo() != null && track.getTempo() < 90) {
                    score *= 1.1;
                }
            }
        }
        
        return score;
    }
    
    /**
     * Determine time of day based on current time
     */
    public User.TimeOfDay getCurrentTimeOfDay() {
        LocalTime now = LocalTime.now();
        int hour = now.getHour();
        
        if (hour >= 5 && hour < 12) {
            return User.TimeOfDay.MORNING;
        } else if (hour >= 12 && hour < 17) {
            return User.TimeOfDay.DAY;
        } else if (hour >= 17 && hour < 22) {
            return User.TimeOfDay.EVENING;
        } else {
            return User.TimeOfDay.NIGHT;
        }
    }
    
    /**
     * Get context description for a track
     */
    public String getContextDescription(Track track, User user) {
        StringBuilder description = new StringBuilder();
        
        // Mood context
        if (user.getCurrentMood() != null) {
            description.append("Mood: ").append(user.getCurrentMood().name().toLowerCase()).append(". ");
        }
        
        // Activity context
        if (user.getCurrentActivity() != null) {
            description.append("Activity: ").append(user.getCurrentActivity().name().toLowerCase()).append(". ");
        }
        
        // Time context
        if (user.getTimeOfDay() != null) {
            description.append("Time: ").append(user.getTimeOfDay().name().toLowerCase()).append(". ");
        }
        
        // Audio feature highlights
        if (track.getEnergy() != null && track.getEnergy() > 0.8) {
            description.append("High energy. ");
        }
        if (track.getDanceability() != null && track.getDanceability() > 0.8) {
            description.append("Very danceable. ");
        }
        if (track.getAcousticness() != null && track.getAcousticness() > 0.8) {
            description.append("Acoustic. ");
        }
        if (track.getInstrumentalness() != null && track.getInstrumentalness() > 0.8) {
            description.append("Instrumental. ");
        }
        
        return description.toString().trim();
    }
    
    /**
     * Calculate overall context fit score
     */
    public double calculateContextFitScore(Track track, User user) {
        double moodScore = calculateMoodScore(track, user.getCurrentMood());
        double activityScore = calculateActivityScore(track, user.getCurrentActivity());
        double timeScore = calculateTimeScore(track, user.getTimeOfDay());
        
        // Weighted average
        return (moodScore * 0.4 + activityScore * 0.4 + timeScore * 0.2);
    }
} 