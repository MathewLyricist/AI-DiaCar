package com.backend.site.AIDiaCar.controllers;

import com.backend.site.AIDiaCar.models.Advice;
import com.backend.site.AIDiaCar.models.Account;
import com.backend.site.AIDiaCar.repository.AdviceRepository;
import com.backend.site.AIDiaCar.repository.AccountRepository;
import com.backend.site.AIDiaCar.JwtTokenProvider;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/advice")
@CrossOrigin(origins = "http://localhost:5173")
public class AdviceController {

    private final JwtTokenProvider jwtTokenProvider;
    private final AccountRepository accountRepository;
    private final AdviceRepository adviceRepository;

    public AdviceController(JwtTokenProvider jwtTokenProvider,
                            AccountRepository accountRepository,
                            AdviceRepository adviceRepository) {
        this.jwtTokenProvider = jwtTokenProvider;
        this.accountRepository = accountRepository;
        this.adviceRepository = adviceRepository;
    }

    @GetMapping
    public ResponseEntity<?> getAllAdvice() {
        try {
            List<Advice> advice = adviceRepository.findAllByOrderByCreatedAtDesc();
            return ResponseEntity.ok(advice);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @PostMapping
    public ResponseEntity<?> createAdvice(@RequestHeader("Authorization") String authHeader,
                                          @RequestBody AdviceRequest request) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            if (!"ROLE_ADMIN".equals(user.getRole())) {
                return ResponseEntity.status(403).body("Доступ запрещён.");
            }

            Advice advice = new Advice();
            advice.setTitle(request.getTitle());
            advice.setContent(request.getContent());
            advice.setCategory(request.getCategory());
            advice.setDifficulty(request.getDifficulty());
            advice.setImageUrl(request.getImageUrl());
            advice.setAuthorId(user.getUserID());

            adviceRepository.save(advice);
            return ResponseEntity.ok("Совет создан!");

        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateAdvice(@RequestHeader("Authorization") String authHeader,
                                          @PathVariable Integer id,
                                          @RequestBody AdviceRequest request) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            if (!"ROLE_ADMIN".equals(user.getRole())) {
                return ResponseEntity.status(403).body("Доступ запрещён.");
            }

            Advice advice = adviceRepository.findById(id)
                    .orElseThrow(() -> new RuntimeException("Совет не найден"));

            advice.setTitle(request.getTitle());
            advice.setContent(request.getContent());
            advice.setCategory(request.getCategory());
            advice.setDifficulty(request.getDifficulty());
            advice.setImageUrl(request.getImageUrl());

            adviceRepository.save(advice);
            return ResponseEntity.ok("Совет обновлён!");

        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteAdvice(@RequestHeader("Authorization") String authHeader,
                                          @PathVariable Integer id) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            if (!"ROLE_ADMIN".equals(user.getRole())) {
                return ResponseEntity.status(403).body("Доступ запрещён.");
            }

            adviceRepository.deleteById(id);
            return ResponseEntity.ok("Совет удалён!");

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

    public static class AdviceRequest {
        private String title;
        private String content;
        private String category;
        private String difficulty;
        private String imageUrl;

        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        public String getContent() { return content; }
        public void setContent(String content) { this.content = content; }
        public String getCategory() { return category; }
        public void setCategory(String category) { this.category = category; }
        public String getDifficulty() { return difficulty; }
        public void setDifficulty(String difficulty) { this.difficulty = difficulty; }
        public String getImageUrl() { return imageUrl; }
        public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
    }
}