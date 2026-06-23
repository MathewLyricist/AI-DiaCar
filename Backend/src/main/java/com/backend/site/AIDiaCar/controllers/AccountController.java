package com.backend.site.AIDiaCar.controllers;

import com.backend.site.AIDiaCar.models.Account;
import com.backend.site.AIDiaCar.JwtTokenProvider;
import com.backend.site.AIDiaCar.repository.AccountRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/account")
@CrossOrigin(origins = "http://localhost:5173")
public class AccountController {

    private final JwtTokenProvider jwtTokenProvider;
    private final AccountRepository accountRepository;
    private final PasswordEncoder passwordEncoder;

    public AccountController(JwtTokenProvider jwtTokenProvider,
                             AccountRepository accountRepository,
                             PasswordEncoder passwordEncoder) {
        this.jwtTokenProvider = jwtTokenProvider;
        this.accountRepository = accountRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @GetMapping("/me")
    public ResponseEntity<?> getCurrentUser(@RequestHeader("Authorization") String authHeader) {
        try {
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                return ResponseEntity.status(401).body("Токен не предоставлен");
            }

            String token = authHeader.substring(7);
            if (!jwtTokenProvider.validateToken(token)) {
                return ResponseEntity.status(401).body("Неверный токен");
            }

            String email = jwtTokenProvider.getEmailFromToken(token);
            Account account = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            Map<String, Object> response = new HashMap<>();
            response.put("name", account.getName());
            response.put("email", account.getEmail());
            response.put("enterprise", account.getEnterprise() != null ? account.getEnterprise() : "не указано");
            response.put("createdAt", account.getCreatedAt());
            String rawPhone = account.getPhone();
            response.put("phone", (rawPhone != null && !rawPhone.isEmpty()) ? rawPhone : "не указан");
            response.put("carsCount", 0);
            response.put("role", account.getRole());

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка сервера: " + e.getMessage());
        }
    }

    @PutMapping("/me")
    public ResponseEntity<?> updateProfile(@RequestHeader("Authorization") String authHeader,
                                           @RequestBody UpdateProfileRequest request) {
        try {
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                return ResponseEntity.status(401).body("Токен не предоставлен");
            }

            String token = authHeader.substring(7);
            if (!jwtTokenProvider.validateToken(token)) {
                return ResponseEntity.status(401).body("Неверный токен");
            }

            String email = jwtTokenProvider.getEmailFromToken(token);
            Account account = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            if (request.getName() != null) account.setName(request.getName());
            if (request.getEnterprise() != null) account.setEnterprise(request.getEnterprise());
            if (request.getPhone() != null) account.setPhone(request.getPhone());

            accountRepository.save(account);

            Map<String, String> response = new HashMap<>();
            response.put("message", "Профиль успешно обновлен");

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка при обновлении: " + e.getMessage());
        }
    }

    @PutMapping("/update-security")
    public ResponseEntity<?> updateSecurity(@RequestHeader("Authorization") String authHeader,
                                            @RequestBody UpdateSecurityRequest request) {
        try {
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                return ResponseEntity.status(401).body("Токен не предоставлен");
            }

            String token = authHeader.substring(7);
            if (!jwtTokenProvider.validateToken(token)) {
                return ResponseEntity.status(401).body("Неверный токен");
            }

            String currentEmail = jwtTokenProvider.getEmailFromToken(token);
            Account account = accountRepository.findByEmail(currentEmail)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            if (!passwordEncoder.matches(request.getCurrentPassword(), account.getPasswordHash())) {
                return ResponseEntity.status(400).body("Неверный текущий пароль");
            }

            if (request.getEmail() != null && !request.getEmail().isEmpty() && !request.getEmail().equals(account.getEmail())) {
                if (accountRepository.existsByEmail(request.getEmail())) {
                    return ResponseEntity.badRequest().body("Email уже занят другим пользователем");
                }
                account.setEmail(request.getEmail());
            }

            if (request.getNewPassword() != null && !request.getNewPassword().isEmpty()) {
                if (request.getNewPassword().length() < 6) {
                    return ResponseEntity.badRequest().body("Новый пароль должен быть не менее 6 символов");
                }
                account.setPasswordHash(passwordEncoder.encode(request.getNewPassword()));
            }

            accountRepository.save(account);

            Map<String, String> response = new HashMap<>();
            response.put("message", "Данные безопасности обновлены");

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка при обновлении: " + e.getMessage());
        }
    }

    public static class UpdateProfileRequest {
        private String name;
        private String enterprise;
        private String phone;

        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public String getEnterprise() { return enterprise; }
        public void setEnterprise(String enterprise) { this.enterprise = enterprise; }
        public String getPhone() { return phone; }
        public void setPhone(String phone) { this.phone = phone; }
    }

    public static class UpdateSecurityRequest {
        private String currentPassword;
        private String email;
        private String newPassword;

        public String getCurrentPassword() { return currentPassword; }
        public void setCurrentPassword(String currentPassword) { this.currentPassword = currentPassword; }
        public String getEmail() { return email; }
        public void setEmail(String email) { this.email = email; }
        public String getNewPassword() { return newPassword; }
        public void setNewPassword(String newPassword) { this.newPassword = newPassword; }
    }
}