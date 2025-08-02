package com.musicrecommendation;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Main Spring Boot application class for the Music Recommendation System.
 * 
 * This application provides bias-resistant, deeply personalized music recommendations
 * using advanced Java-based machine learning algorithms and Spotify API integration.
 */
@SpringBootApplication
@EnableAsync
@EnableScheduling
public class MusicRecommendationApplication {

    public static void main(String[] args) {
        SpringApplication.run(MusicRecommendationApplication.class, args);
    }
} 