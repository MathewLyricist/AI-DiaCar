package com.backend.site.AIDiaCar.controllers;

import com.backend.site.AIDiaCar.models.News;
import com.backend.site.AIDiaCar.models.Account;
import com.backend.site.AIDiaCar.repository.NewsRepository;
import com.backend.site.AIDiaCar.repository.AccountRepository;
import com.backend.site.AIDiaCar.JwtTokenProvider;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/news")
@CrossOrigin(origins = "http://localhost:5173")
public class NewsController {

    private final JwtTokenProvider jwtTokenProvider;
    private final AccountRepository accountRepository;
    private final NewsRepository newsRepository;

    public NewsController(JwtTokenProvider jwtTokenProvider,
                          AccountRepository accountRepository,
                          NewsRepository newsRepository) {
        this.jwtTokenProvider = jwtTokenProvider;
        this.accountRepository = accountRepository;
        this.newsRepository = newsRepository;
    }

    @GetMapping
    public ResponseEntity<?> getAllNews() {
        try {
            List<News> news = newsRepository.findAllByOrderByDateDesc();
            return ResponseEntity.ok(news);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @PostMapping
    public ResponseEntity<?> createNews(@RequestHeader("Authorization") String authHeader,
                                        @RequestBody NewsRequest request) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            if (!"ROLE_ADMIN".equals(user.getRole())) {
                return ResponseEntity.status(403).body("Доступ запрещён. Требуются права администратора.");
            }

            News news = new News();
            news.setTitle(request.getTitle());
            news.setContent(request.getContent());
            news.setImageUrl(request.getImageUrl());
            news.setVideoUrl(request.getVideoUrl());
            news.setDate(request.getDate());
            news.setAuthorId(user.getUserID());

            newsRepository.save(news);
            return ResponseEntity.ok("Новость создана!");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateNews(@RequestHeader("Authorization") String authHeader,
                                        @PathVariable Integer id,
                                        @RequestBody NewsRequest request) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            if (!"ROLE_ADMIN".equals(user.getRole())) {
                return ResponseEntity.status(403).body("Доступ запрещён.");
            }

            News news = newsRepository.findById(id)
                    .orElseThrow(() -> new RuntimeException("Новость не найдена"));

            news.setTitle(request.getTitle());
            news.setContent(request.getContent());
            news.setImageUrl(request.getImageUrl());
            news.setVideoUrl(request.getVideoUrl());
            news.setDate(request.getDate());

            newsRepository.save(news);
            return ResponseEntity.ok("Новость обновлена!");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteNews(@RequestHeader("Authorization") String authHeader,
                                        @PathVariable Integer id) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            if (!"ROLE_ADMIN".equals(user.getRole())) {
                return ResponseEntity.status(403).body("Доступ запрещён.");
            }

            newsRepository.deleteById(id);
            return ResponseEntity.ok("Новость удалена!");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    private String extractEmailFromToken(String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new RuntimeException("Токен не предоставлен");
        }
        String token = authHeader.substring(7);
        return jwtTokenProvider.getEmailFromToken(token);
    }

    public static class NewsRequest {
        private String title;
        private String content;
        private String imageUrl;
        private String videoUrl;
        private String date;

        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        public String getContent() { return content; }
        public void setContent(String content) { this.content = content; }
        public String getImageUrl() { return imageUrl; }
        public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
        public String getVideoUrl() { return videoUrl; }
        public void setVideoUrl(String videoUrl) { this.videoUrl = videoUrl; }
        public String getDate() { return date; }
        public void setDate(String date) { this.date = date; }
    }
}