package com.backend.site.AIDiaCar.controllers;

import com.backend.site.AIDiaCar.JwtTokenProvider;
import com.backend.site.AIDiaCar.models.Account;
import com.backend.site.AIDiaCar.models.Feedback;
import com.backend.site.AIDiaCar.repository.AccountRepository;
import com.backend.site.AIDiaCar.repository.FeedbackRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/feedback")
@CrossOrigin(origins = "http://localhost:5173")
public class FeedbackController {

    private final JwtTokenProvider jwtTokenProvider;
    private final AccountRepository accountRepository;
    private final FeedbackRepository feedbackRepository;

    public FeedbackController(JwtTokenProvider jwtTokenProvider,
                              AccountRepository accountRepository,
                              FeedbackRepository feedbackRepository) {
        this.jwtTokenProvider = jwtTokenProvider;
        this.accountRepository = accountRepository;
        this.feedbackRepository = feedbackRepository;
    }

    @GetMapping("/daily-limit")
    public ResponseEntity<?> getDailyLimit(@RequestHeader("Authorization") String authHeader) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            LocalDate today = LocalDate.now();
            LocalDateTime startOfDay = today.atStartOfDay();
            LocalDateTime endOfDay = today.atTime(23, 59, 59);

            long count = feedbackRepository.countByUserIdAndCreatedAtBetween(
                    user.getUserID(), startOfDay, endOfDay
            );

            Map<String, Object> response = new HashMap<>();
            response.put("count", count);
            response.put("limit", 2);
            response.put("canSubmit", count < 2);

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @PostMapping
    public ResponseEntity<?> createFeedback(@RequestHeader("Authorization") String authHeader,
                                            @RequestBody FeedbackRequest request) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            LocalDate today = LocalDate.now();
            LocalDateTime startOfDay = today.atStartOfDay();
            LocalDateTime endOfDay = today.atTime(23, 59, 59);

            long count = feedbackRepository.countByUserIdAndCreatedAtBetween(
                    user.getUserID(), startOfDay, endOfDay
            );

            if (count >= 2) {
                return ResponseEntity.status(429).body("❌ Лимит исчерпан: 2 обращения в день. Попробуйте завтра.");
            }

            Feedback feedback = new Feedback();
            feedback.setUserId(user.getUserID());
            feedback.setType(request.getType());
            feedback.setSubject(request.getSubject());
            feedback.setComment(request.getMessage());
            feedback.setEmail(request.getEmail());
            feedback.setStatus("new");
            LocalDateTime now = LocalDateTime.now();
            feedback.setCreatedAt(now);
            feedback.setUpdatedAt(now);
            feedback.setSubmittedDate(now);
            feedback.setSubmittedTime(now);

            feedbackRepository.save(feedback);
            return ResponseEntity.ok("✅ Обращение отправлено!");

        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @GetMapping("/all")
    public ResponseEntity<?> getAllFeedback(@RequestHeader("Authorization") String authHeader) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            if (!"admin".equals(user.getRole())) {
                return ResponseEntity.status(403).body("Доступ запрещён.");
            }

            List<Feedback> feedback = feedbackRepository.findAllByOrderByCreatedAtDesc();
            return ResponseEntity.ok(feedback);

        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @PutMapping("/{id}/status")
    public ResponseEntity<?> updateStatus(@RequestHeader("Authorization") String authHeader,
                                          @PathVariable Integer id,
                                          @RequestBody Map<String, String> statusRequest) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            if (!"admin".equals(user.getRole())) {
                return ResponseEntity.status(403).body("Доступ запрещён.");
            }

            Feedback feedback = feedbackRepository.findById(id)
                    .orElseThrow(() -> new RuntimeException("Обращение не найдено"));

            feedback.setStatus(statusRequest.get("status"));
            feedback.setAdminResponse(statusRequest.get("response"));
            feedback.setUpdatedAt(LocalDateTime.now());

            feedbackRepository.save(feedback);
            return ResponseEntity.ok("Статус обновлён!");

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

    public static class FeedbackRequest {
        private String type;
        private String subject;
        private String message;
        private String email;

        public String getType() { return type; }
        public void setType(String type) { this.type = type; }
        public String getSubject() { return subject; }
        public void setSubject(String subject) { this.subject = subject; }
        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }
        public String getEmail() { return email; }
        public void setEmail(String email) { this.email = email; }
    }
}