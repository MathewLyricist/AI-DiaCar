package com.backend.site.AIDiaCar.controllers;

import com.backend.site.AIDiaCar.DiagnosticSession;
import com.backend.site.AIDiaCar.SessionImageService;
import com.backend.site.AIDiaCar.models.Account;
import com.backend.site.AIDiaCar.models.Car;
import com.backend.site.AIDiaCar.models.DiagnosticReportService;
import com.backend.site.AIDiaCar.models.Manual;
import com.backend.site.AIDiaCar.models.ChatMessage;
import com.backend.site.AIDiaCar.repository.AccountRepository;
import com.backend.site.AIDiaCar.repository.CarRepository;
import com.backend.site.AIDiaCar.repository.DiagnosticSessionRepository;
import com.backend.site.AIDiaCar.repository.ChatMessageRepository;
import com.backend.site.AIDiaCar.models.ManualService;
import com.backend.site.AIDiaCar.JwtTokenProvider;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/cars")
@CrossOrigin(origins = "http://localhost:5173")
public class CarController {
    private final JwtTokenProvider jwtTokenProvider;
    private final AccountRepository accountRepository;
    private final CarRepository carRepository;
    private final DiagnosticSessionRepository sessionRepository;
    private final ChatMessageRepository chatMessageRepository;
    private final ManualService manualService;
    private final SessionImageService sessionImageService;
    private final DiagnosticReportService reportService;

    private static final String ML_SERVICE_URL = "http://localhost:8000/api/ml";

    public CarController(JwtTokenProvider jwtTokenProvider,
                         AccountRepository accountRepository,
                         CarRepository carRepository,
                         DiagnosticSessionRepository sessionRepository,
                         ChatMessageRepository chatMessageRepository,
                         ManualService manualService,
                         SessionImageService sessionImageService, DiagnosticReportService reportService) {
        this.jwtTokenProvider = jwtTokenProvider;
        this.accountRepository = accountRepository;
        this.carRepository = carRepository;
        this.sessionRepository = sessionRepository;
        this.chatMessageRepository = chatMessageRepository;
        this.manualService = manualService;
        this.sessionImageService = sessionImageService;
        this.reportService = reportService;
    }

    @GetMapping("/brands")
    public ResponseEntity<?> getUniqueBrands() {
        List<Car> allCars = carRepository.findAll();
        Set<String> brands = new HashSet<>();
        for (Car car : allCars) {
            if (car.getBrand() != null) {
                brands.add(car.getBrand());
            }
        }
        System.out.println("Бренды: " + brands);
        return ResponseEntity.ok(new ArrayList<>(brands));
    }

    @GetMapping("/models")
    public ResponseEntity<?> getModelsByBrand(@RequestParam String brand) {
        List<Car> allCars = carRepository.findAll();
        Set<String> models = new HashSet<>();
        for (Car car : allCars) {
            if (car.getBrand() != null &&
                    car.getBrand().equalsIgnoreCase(brand) &&
                    car.getModel() != null) {
                models.add(car.getModel());
            }
        }
        System.out.println("Модели для " + brand + ": " + models);
        return ResponseEntity.ok(new ArrayList<>(models));
    }

    @GetMapping("/check-exists")
    public ResponseEntity<?> checkExists(
            @RequestParam String brand,
            @RequestParam String model,
            @RequestParam Integer year,
            @RequestParam(required = false) String generation) {

        List<Car> allCars = carRepository.findAll();
        Optional<Car> existing = allCars.stream().filter(c ->
                c.getBrand() != null && c.getBrand().equalsIgnoreCase(brand) &&
                        c.getModel() != null && c.getModel().equalsIgnoreCase(model) &&
                        c.getYear() != null && c.getYear().equals(year) &&
                        (generation == null || generation.isEmpty() ||
                                (c.getGeneration() != null && c.getGeneration().equalsIgnoreCase(generation)))
        ).findFirst();

        Map<String, Object> response = new HashMap<>();
        response.put("exists", existing.isPresent());
        if (existing.isPresent()) {
            response.put("carId", existing.get().getCarID());
        }
        return ResponseEntity.ok(response);
    }

    @GetMapping("/all")
    public ResponseEntity<?> getAllCars() {
        try {
            List<Car> cars = carRepository.findAll();
            List<Map<String, Object>> result = cars.stream().map(car -> {
                Map<String, Object> map = new HashMap<>();
                map.put("carID", car.getCarID());
                map.put("brand", car.getBrand());
                map.put("model", car.getModel());
                map.put("year", car.getYear());
                map.put("engine", car.getTypeEngine());
                map.put("equipment", car.getEquipment());
                map.put("generation", car.getGeneration());
                return map;
            }).collect(Collectors.toList());
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @PostMapping("/add")
    public ResponseEntity<?> addCar(@RequestHeader("Authorization") String authHeader,
                                    @RequestBody CarRequest request) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));
            if (!"ADMIN".equals(user.getRole())) {
                return ResponseEntity.status(403).body("Доступ запрещён");
            }

            Car newCar = new Car(
                    request.getBrand(),
                    request.getModel(),
                    request.getYear(),
                    request.getEngine(),
                    request.getEquipment(),
                    request.getGeneration()
            );

            Optional<Manual> manualOpt = manualService.findManualForCar(
                    request.getBrand(),
                    request.getModel()
            );

            String manualPath = manualOpt.isPresent() ? manualOpt.get().getDirectoryPath() : null;
            newCar.setManualPath(manualPath);

            if (newCar.getImagePath() == null || newCar.getImagePath().isEmpty()) {
                String defaultImage = "/images/cars/" + newCar.getBrand().toLowerCase() + "_" + newCar.getModel().toLowerCase() + ".jpg";
                newCar.setImagePath(defaultImage);
            }

            carRepository.save(newCar);
            return ResponseEntity.ok("Автомобиль добавлен в справочник");
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @PostMapping("/start-session")
    public ResponseEntity<?> startSession(@RequestHeader("Authorization") String authHeader,
                                          @RequestBody SessionRequest request) {
        try {
            System.out.println("=== НАЧАЛО СОЗДАНИЯ СЕССИИ ===");
            System.out.println("Car ID: " + request.getCarId());

            String email = extractEmailFromToken(authHeader);
            System.out.println("Email: " + email);

            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));
            System.out.println("User found: " + user.getUserID());

            Car car = carRepository.findById(request.getCarId())
                    .orElseThrow(() -> new RuntimeException("Автомобиль не найден: " + request.getCarId()));
            System.out.println("Car found: " + car.getBrand() + " " + car.getModel());

            List<DiagnosticSession> activeSessions = sessionRepository.findByUserAndCarAndStatus(user, car, "ACTIVE");
            if (!activeSessions.isEmpty()) {
                DiagnosticSession existing = activeSessions.get(0);
                existing.setLastActivityAt(LocalDateTime.now());
                sessionRepository.save(existing);
                System.out.println("Возвращена активная сессия: " + existing.getSessionID());

                Optional<Manual> manualOpt = manualService.findManualForCar(car.getBrand(), car.getModel());
                String carImage = car.getImagePath();

                Map<String, Object> response = new HashMap<>();
                response.put("sessionId", existing.getSessionID());
                response.put("carId", car.getCarID());
                response.put("carBrand", car.getBrand());
                response.put("carModel", car.getModel());
                response.put("carYear", car.getYear());
                response.put("carEngine", car.getTypeEngine() != null ? car.getTypeEngine() : "Не указан");
                response.put("carEquipment", car.getEquipment() != null ? car.getEquipment() : "Не указана");
                response.put("carGeneration", car.getGeneration() != null ? car.getGeneration() : "Не указано");
                response.put("manualAvailable", manualOpt.isPresent());
                response.put("manualType", manualOpt.isPresent() ? manualOpt.get().getManualType() : "NONE");
                response.put("manualPath", existing.getManualUsedPath());
                response.put("manualStatus", getManualStatusText(manualOpt.isPresent() ? manualOpt.get().getManualType() : "NONE"));
                response.put("status", existing.getStatus());
                response.put("carImage", carImage);

                return ResponseEntity.ok(response);
            }

            Optional<Manual> manualOpt = manualService.findManualForCar(car.getBrand(), car.getModel());
            String fullPdfPath = null;
            if (manualOpt.isPresent()) {
                fullPdfPath = manualService.findBestPdfForCar(
                        car.getBrand(),
                        car.getModel(),
                        car.getYear(),
                        manualOpt.get().getDirectoryPath()
                );
                if (fullPdfPath == null) {
                    File dir = new File(manualOpt.get().getDirectoryPath());
                    File[] pdfFiles = dir.listFiles((d, name) -> name.toLowerCase().endsWith(".pdf"));
                    if (pdfFiles != null && pdfFiles.length > 0) {
                        fullPdfPath = pdfFiles[0].getAbsolutePath();
                    }
                }
                System.out.println("Найден PDF: " + fullPdfPath);
            }

            String carImage = car.getImagePath();
            if (carImage == null || carImage.isEmpty()) carImage = null;

            String manualType = manualOpt.isPresent() ? manualOpt.get().getManualType() : "NONE";
            DiagnosticSession session = new DiagnosticSession(user, car, fullPdfPath);
            sessionRepository.save(session);
            System.out.println("Session created: " + session.getSessionID());

            Map<String, Object> response = new HashMap<>();
            response.put("sessionId", session.getSessionID());
            response.put("carId", car.getCarID());
            response.put("carBrand", car.getBrand());
            response.put("carModel", car.getModel());
            response.put("carYear", car.getYear());
            response.put("carEngine", car.getTypeEngine() != null ? car.getTypeEngine() : "Не указан");
            response.put("carEquipment", car.getEquipment() != null ? car.getEquipment() : "Не указана");
            response.put("carGeneration", car.getGeneration() != null ? car.getGeneration() : "Не указано");
            response.put("manualAvailable", manualOpt.isPresent());
            response.put("manualType", manualType);
            response.put("manualPath", fullPdfPath);
            response.put("manualStatus", getManualStatusText(manualType));
            response.put("status", session.getStatus());
            response.put("carImage", carImage);

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            System.err.println("=== ОШИБКА СОЗДАНИЯ СЕССИИ ===");
            e.printStackTrace();
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @PostMapping("/sessions/{sessionId}/message")
    public ResponseEntity<?> sendMessage(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable Integer sessionId,
            @RequestBody MessageRequest messageRequest) {
        try {
            System.out.println("=== ПОЛУЧЕНО СООБЩЕНИЕ ===");
            System.out.println("Session ID: " + sessionId);
            System.out.println("Message: " + messageRequest.getMessage());

            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            DiagnosticSession session = sessionRepository.findById(sessionId)
                    .orElseThrow(() -> new RuntimeException("Сессия не найдена"));

            if (!session.getUser().getUserID().equals(user.getUserID())) {
                return ResponseEntity.status(403).body("Доступ запрещён");
            }

            if (!"ACTIVE".equals(session.getStatus())) {
                return ResponseEntity.status(400).body("Сессия завершена. Нельзя отправлять сообщения.");
            }

            session.setLastActivityAt(LocalDateTime.now());
            sessionRepository.save(session);

            ChatMessage userMessage = new ChatMessage(session, "user", messageRequest.getMessage());
            chatMessageRepository.save(userMessage);
            System.out.println("Сообщение пользователя сохранено: " + userMessage.getMessageId());

            Map<String, Object> mlResponse = callMLService(sessionId, messageRequest.getMessage(), session.getCar());
            String aiResponse = (String) mlResponse.get("answer");
            List<Map<String, Object>> suggestedPages = (List<Map<String, Object>>) mlResponse.get("suggested_pages");

            ChatMessage aiMessage = new ChatMessage(session, "ai", aiResponse);
            chatMessageRepository.save(aiMessage);
            System.out.println("Ответ AI сохранён: " + aiMessage.getMessageId());

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("userMessage", messageRequest.getMessage());
            response.put("aiResponse", aiResponse);
            if (suggestedPages != null && !suggestedPages.isEmpty()) {
                response.put("suggestedPages", suggestedPages);
            }
            response.put("timestamp", new Date());

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            System.err.println("=== ОШИБКА ОТПРАВКИ СООБЩЕНИЯ ===");
            e.printStackTrace();
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @GetMapping("/sessions/{sessionId}/messages")
    public ResponseEntity<?> getSessionMessages(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable Integer sessionId) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            DiagnosticSession session = sessionRepository.findById(sessionId)
                    .orElseThrow(() -> new RuntimeException("Сессия не найдена"));

            if (!session.getUser().getUserID().equals(user.getUserID())) {
                return ResponseEntity.status(403).body("Доступ запрещён");
            }

            List<ChatMessage> messages = chatMessageRepository.findBySession_SessionIDOrderByCreatedAtAsc(sessionId);

            List<Map<String, Object>> result = messages.stream().map(msg -> {
                Map<String, Object> map = new HashMap<>();
                map.put("messageId", msg.getMessageId());
                map.put("role", msg.getRole());
                map.put("content", msg.getContent());
                map.put("createdAt", msg.getCreatedAt());
                map.put("imageUrl", msg.getImageUrl());
                map.put("pageNumber", msg.getPageNumber());
                map.put("messageType", msg.getMessageType());
                return map;
            }).collect(Collectors.toList());

            System.out.println("Найдено сообщений: " + result.size());
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @PostMapping("/sessions/{sessionId}/send-page")
    public ResponseEntity<?> sendManualPage(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable Integer sessionId,
            @RequestBody PageRequest pageRequest) {
        try {
            System.out.println("=== ЗАПРОС СТРАНИЦЫ ИЗ МАНУАЛА ===");
            System.out.println("Session ID: " + sessionId);
            System.out.println("Page Number: " + pageRequest.getPageNumber());

            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            DiagnosticSession session = sessionRepository.findById(sessionId)
                    .orElseThrow(() -> new RuntimeException("Сессия не найдена"));

            if (!session.getUser().getUserID().equals(user.getUserID())) {
                return ResponseEntity.status(403).body("Доступ запрещён");
            }

            if (!"ACTIVE".equals(session.getStatus())) {
                return ResponseEntity.status(400).body("Сессия завершена.");
            }

            session.setLastActivityAt(LocalDateTime.now());
            sessionRepository.save(session);

            String manualPath = session.getManualUsedPath();
            if (manualPath == null || manualPath.isEmpty()) {
                return ResponseEntity.status(404).body("Мануал не подключен к этой сессии");
            }

            File manualFile = new File(manualPath);
            if (!manualFile.exists()) {
                return ResponseEntity.status(404).body("Мануал не найден: " + manualPath);
            }

            if (manualFile.isDirectory()) {
                File[] pdfs = manualFile.listFiles((dir, name) -> name.toLowerCase().endsWith(".pdf"));
                if (pdfs == null || pdfs.length == 0) {
                    return ResponseEntity.status(404).body("В указанной директории нет PDF-файлов");
                }
                manualFile = pdfs[0];
                System.out.println("Найден PDF файл: " + manualFile.getAbsolutePath());
            }

            if (!manualFile.isFile()) {
                return ResponseEntity.status(404).body("Путь не указывает на файл: " + manualFile.getAbsolutePath());
            }

            int offset = manualService.getPageOffsetFromFileName(manualFile.getAbsolutePath());
            int requestedPage = pageRequest.getPageNumber();
            int realPageNumber = requestedPage + offset;
            System.out.println("Запрошена страница " + requestedPage + ", смещение " + offset + ", реальная страница " + realPageNumber);

            byte[] imageData = manualService.convertPageToImage(manualFile.getAbsolutePath(), realPageNumber);
            if (imageData == null) {
                return ResponseEntity.status(404).body("Страница не найдена (реальная страница " + realPageNumber + ")");
            }

            String imageUrl = sessionImageService.savePageImage(sessionId, requestedPage, imageData);

            ChatMessage pageMessage = new ChatMessage(session, "ai",
                    "Вот страница " + requestedPage + " из технической документации:");
            pageMessage.setMessageType("PDF_PAGE");
            pageMessage.setImageUrl(imageUrl);
            pageMessage.setPageNumber(requestedPage);
            pageMessage.setManualReferences(manualFile.getAbsolutePath());
            chatMessageRepository.save(pageMessage);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("imageUrl", imageUrl);
            response.put("pageNumber", requestedPage);
            response.put("messageId", pageMessage.getMessageId());

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            System.err.println("=== ОШИБКА ОТПРАВКИ СТРАНИЦЫ ===");
            e.printStackTrace();
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @GetMapping("/sessions/active")
    public ResponseEntity<?> getActiveSessions(@RequestHeader("Authorization") String authHeader) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            List<DiagnosticSession> sessions = sessionRepository.findByUserAndStatus(user, "ACTIVE");

            List<Map<String, Object>> result = sessions.stream().map(session -> {
                Map<String, Object> map = new HashMap<>();
                map.put("sessionId", session.getSessionID());
                map.put("carId", session.getCar().getCarID());
                map.put("carBrand", session.getCar().getBrand());
                map.put("carModel", session.getCar().getModel());
                map.put("carYear", session.getCar().getYear());
                map.put("carGeneration", session.getCar().getGeneration());
                map.put("carEngine", session.getCar().getTypeEngine() != null ? session.getCar().getTypeEngine() : "Не указан");
                map.put("carEquipment", session.getCar().getEquipment() != null ? session.getCar().getEquipment() : "Не указана");
                map.put("createdAt", session.getCreatedAt());
                map.put("expiresAt", session.getExpiresAt());
                map.put("imagePath", session.getCar().getImagePath());

                String manualPath = session.getManualUsedPath();
                map.put("manualAvailable", manualPath != null && !manualPath.isEmpty());
                map.put("manualPath", manualPath);

                String manualType = "NONE";
                if (manualPath != null && !manualPath.isEmpty()) {
                    if (manualPath.contains("/Common/") || manualPath.contains("\\Common\\")) {
                        if (manualPath.split("/").length <= 4) {
                            manualType = "GENERAL";
                        } else {
                            manualType = "BRAND_COMMON";
                        }
                    } else {
                        manualType = "SPECIFIC";
                    }
                }
                map.put("manualType", manualType);
                map.put("status", session.getStatus());
                return map;
            }).collect(Collectors.toList());

            System.out.println("Найдено активных сессий: " + result.size());
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            System.err.println("Ошибка получения активных сессий: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @GetMapping("/sessions/completed")
    public ResponseEntity<?> getCompletedSessions(@RequestHeader("Authorization") String authHeader) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            List<DiagnosticSession> sessions = sessionRepository.findByUserAndStatus(user, "COMPLETED");

            List<Map<String, Object>> result = sessions.stream().map(session -> {
                Map<String, Object> map = new HashMap<>();
                map.put("sessionId", session.getSessionID());
                map.put("carId", session.getCar().getCarID());
                map.put("carBrand", session.getCar().getBrand());
                map.put("carModel", session.getCar().getModel());
                map.put("carYear", session.getCar().getYear());
                map.put("carGeneration", session.getCar().getGeneration());
                map.put("createdAt", session.getCreatedAt());
                map.put("completedAt", session.getCompletedAt());
                map.put("manualPath", session.getManualUsedPath());
                map.put("status", session.getStatus());
                return map;
            }).collect(Collectors.toList());

            System.out.println("Найдено завершённых сессий: " + result.size());
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            System.err.println("Ошибка получения завершённых сессий: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @PostMapping("/sessions/{sessionId}/complete")
    public ResponseEntity<?> completeSession(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable Integer sessionId) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            DiagnosticSession session = sessionRepository.findById(sessionId)
                    .orElseThrow(() -> new RuntimeException("Сессия не найдена"));

            if (!session.getUser().getUserID().equals(user.getUserID())) {
                return ResponseEntity.status(403).body("Доступ запрещён");
            }

            session.setStatus("COMPLETED");
            session.setCompletedAt(new Date());
            session.setLastActivityAt(LocalDateTime.now());
            sessionRepository.save(session);

            sessionImageService.deleteSessionImages(sessionId);

            System.out.println("Сессия " + sessionId + " завершена");

            Map<String, Object> response = new HashMap<>();
            response.put("sessionId", session.getSessionID());
            response.put("status", "COMPLETED");
            response.put("message", "Сессия успешно завершена");

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            System.err.println("Ошибка завершения сессии: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @GetMapping("/sessions/{sessionId}")
    public ResponseEntity<?> getSessionById(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable Integer sessionId) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            DiagnosticSession session = sessionRepository.findById(sessionId)
                    .orElseThrow(() -> new RuntimeException("Сессия не найдена"));

            if (!session.getUser().getUserID().equals(user.getUserID())) {
                return ResponseEntity.status(403).body("Доступ запрещён");
            }

            Car car = session.getCar();
            String manualPath = session.getManualUsedPath();
            String manualType = manualPath != null ? getManualTypeFromPath(manualPath) : "NONE";

            Map<String, Object> response = new HashMap<>();
            response.put("sessionId", session.getSessionID());
            response.put("carId", car.getCarID());
            response.put("carBrand", car.getBrand());
            response.put("carModel", car.getModel());
            response.put("carYear", car.getYear());
            response.put("carEngine", car.getTypeEngine() != null ? car.getTypeEngine() : "Не указан");
            response.put("carEquipment", car.getEquipment() != null ? car.getEquipment() : "Не указана");
            response.put("carGeneration", car.getGeneration() != null ? car.getGeneration() : "Не указано");
            response.put("status", session.getStatus());
            response.put("createdAt", session.getCreatedAt());
            response.put("expiresAt", session.getExpiresAt());
            response.put("completedAt", session.getCompletedAt());
            response.put("manualPath", manualPath);
            response.put("manualAvailable", manualPath != null && !manualPath.isEmpty());
            response.put("manualType", manualType);
            response.put("manualStatus", getManualStatusText(manualType));
            response.put("carImage", car.getImagePath());

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Ошибка: " + e.getMessage());
        }
    }

    @GetMapping("/sessions/{sessionId}/download")
    public ResponseEntity<?> downloadReport(
            @RequestHeader("Authorization") String authHeader,
            @PathVariable Integer sessionId) {
        try {
            String email = extractEmailFromToken(authHeader);
            Account user = accountRepository.findByEmail(email)
                    .orElseThrow(() -> new UsernameNotFoundException("Пользователь не найден"));

            DiagnosticSession session = sessionRepository.findById(sessionId)
                    .orElseThrow(() -> new RuntimeException("Сессия не найдена"));

            if (!session.getUser().getUserID().equals(user.getUserID())) {
                return ResponseEntity.status(403).body("Доступ запрещён");
            }

            byte[] pdfBytes = reportService.generateReport(session);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_PDF);
            headers.setContentDispositionFormData("attachment", "diagnostic_card_" + sessionId + ".pdf");
            headers.setContentLength(pdfBytes.length);

            return ResponseEntity.ok()
                    .headers(headers)
                    .body(pdfBytes);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("Ошибка генерации PDF: " + e.getMessage());
        }
    }

    private String extractEmailFromToken(String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new RuntimeException("Токен не предоставлен");
        }
        String token = authHeader.substring(7);
        return jwtTokenProvider.getEmailFromToken(token);
    }

    private String generateAIResponse(String userMessage, Car car) {
        if (car == null) {
            return "Пожалуйста, опишите проблему подробнее.";
        }

        return String.format(
                "Анализирую проблему для %s %s (%d) с двигателем %s... " +
                        "Пожалуйста, опишите симптомы подробнее: когда началась проблема, " +
                        "при каких условиях проявляется, есть ли посторонние звуки или индикаторы на панели?",
                car.getBrand() != null ? car.getBrand() : "неизвестно",
                car.getModel() != null ? car.getModel() : "неизвестно",
                car.getYear() != null ? car.getYear() : 0,
                car.getTypeEngine() != null ? car.getTypeEngine() : "не указан"
        );
    }

    private String getManualStatusText(String manualType) {
        if (manualType == null || manualType.equals("NONE")) {
            return "Специализированный мануал не найден. Диагностика проводится по общим техническим регламентам.";
        }
        switch (manualType) {
            case "SPECIFIC":
                return "Загружен мануал для конкретной модели. Диагностика проводится с учетом спецификации производителя.";
            case "BRAND_COMMON":
                return "Загружен общий мануал бренда. Диагностика проводится с учетом технических данных марки.";
            case "GENERAL":
                return "Используется общий мануал для всех автомобилей. Диагностика проводится по базовым регламентам.";
            default:
                return "Мануал не найден";
        }
    }

    private String getManualTypeFromPath(String path) {
        if (path == null) return "NONE";
        if (path.contains("/Common/") || path.contains("\\Common\\")) {
            return "GENERAL";
        } else if (path.contains("Common")) {
            return "BRAND_COMMON";
        } else {
            return "SPECIFIC";
        }
    }

    private Map<String, Object> callMLService(Integer sessionId, String message, Car car) {
        try {
            System.out.println("🔄 [ML] Вызов ML сервиса...");

            DiagnosticSession session = sessionRepository.findById(sessionId)
                    .orElseThrow(() -> new RuntimeException("Сессия не найдена"));

            String pdfPath = session.getManualUsedPath();
            if (pdfPath == null || pdfPath.isEmpty()) {
                System.err.println("⚠️ [ML] В сессии нет пути к PDF");
            } else {
                File pdfFile = new File(pdfPath);
                if (!pdfFile.exists() || !pdfFile.isFile()) {
                    System.err.println("⚠️ [ML] PDF не существует или не файл: " + pdfPath);
                    pdfPath = null;
                } else {
                    System.out.println("✅ [ML] PDF путь из сессии: " + pdfPath);
                }
            }

            List<ChatMessage> recentMessages = chatMessageRepository
                    .findBySession_SessionIDOrderByCreatedAtAsc(sessionId);
            List<Map<String, String>> history = new ArrayList<>();
            if (recentMessages != null && !recentMessages.isEmpty()) {
                int start = Math.max(0, recentMessages.size() - 10);
                for (int i = start; i < recentMessages.size(); i++) {
                    ChatMessage msg = recentMessages.get(i);
                    Map<String, String> turn = new HashMap<>();
                    turn.put("role", msg.getRole().equals("user") ? "user" : "assistant");
                    turn.put("content", msg.getContent());
                    history.add(turn);
                }
                System.out.println("📜 [ML] Загружено " + history.size() + " сообщений истории");
            }

            Map<String, Object> mlRequest = new HashMap<>();
            mlRequest.put("message", message);
            mlRequest.put("session_id", sessionId);
            mlRequest.put("car_info", Map.of(
                    "brand", car.getBrand(),
                    "model", car.getModel(),
                    "year", car.getYear(),
                    "engine", car.getTypeEngine() != null ? car.getTypeEngine() : ""
            ));
            mlRequest.put("pdf_path", pdfPath != null ? pdfPath : "");
            if (!history.isEmpty()) {
                mlRequest.put("history", history);
            }

            RestTemplate restTemplate = new RestTemplate();
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(mlRequest, headers);

            ResponseEntity<Map> response = restTemplate.postForEntity(
                    ML_SERVICE_URL + "/query",
                    entity,
                    Map.class
            );

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> mlBody = response.getBody();
                System.out.println("✅ [ML] Получен ответ");
                return mlBody;
            } else {
                System.err.println("❌ [ML] Ошибка HTTP: " + response.getStatusCode());
            }

        } catch (Exception e) {
            System.err.println("❌ [ML] Ошибка: " + e.getMessage());
            e.printStackTrace();
        }

        Map<String, Object> fallback = new HashMap<>();
        fallback.put("answer", generateAIResponse(message, car));
        fallback.put("suggested_pages", Collections.emptyList());
        return fallback;
    }

    private List<String> searchFragments(String fullText, String query, int maxResults) {
        List<String> results = new ArrayList<>();

        String[] keywords = query.toLowerCase().split("\\s+");
        Set<String> stopWords = Set.of("как", "что", "где", "когда", "почему", "зачем", "если", "то", "и", "в", "на", "не", "для");

        List<String> filteredKeywords = new ArrayList<>();
        for (String kw : keywords) {
            if (kw.length() > 3 && !stopWords.contains(kw)) {
                filteredKeywords.add(kw);
                if (kw.length() > 4) {
                    filteredKeywords.add(kw.substring(0, kw.length() - 2));
                }
            }
        }

        if (query.toLowerCase().contains("кулис")) {
            filteredKeywords.addAll(Arrays.asList("привод", "переключения", "механизм", "тяга", "рычаг"));
            System.out.println("🔑 [Search] Добавлены синонимы для кулисы");
        }

        System.out.println("🔑 [Search] Ключевые слова: " + filteredKeywords);

        Set<String> instructionVerbs = Set.of(
                "измерьте", "проверьте", "отрегулируйте", "ослабьте", "затяните",
                "снимите", "установите", "замените", "нажмите", "поверните",
                "добейтесь", "вращайте", "отпустите", "выньте", "вставьте"
        );

        Set<String> exclusionPatterns = Set.of(
                "раздел", "особенности конструкции", "проверка технического",
                "замена ", "снятие и установка", "рис.", "см. с.",
                "трансмиссия", "двигатель", "ходовая часть"
        );

        String[] sentences = fullText.split("[.!?]+");
        List<Map.Entry<String, Integer>> scoredSentences = new ArrayList<>();

        for (String sentence : sentences) {
            String lower = sentence.toLowerCase().trim();
            if (lower.length() < 40) continue;

            boolean isExcluded = false;
            for (String pattern : exclusionPatterns) {
                if (lower.contains(pattern)) {
                    isExcluded = true;
                    break;
                }
            }
            if (isExcluded) continue;

            int keywordMatches = 0;
            for (String kw : filteredKeywords) {
                if (lower.contains(kw)) keywordMatches++;
            }

            boolean hasInstructionVerb = false;
            for (String verb : instructionVerbs) {
                if (lower.contains(verb)) {
                    hasInstructionVerb = true;
                    break;
                }
            }

            if (keywordMatches >= 1 && hasInstructionVerb) {
                String clean = cleanSentence(sentence);
                if (clean.length() > 50) {
                    scoredSentences.add(new AbstractMap.SimpleEntry<>(clean, keywordMatches));
                }
            }
        }

        scoredSentences.sort((a, b) -> b.getValue().compareTo(a.getValue()));

        Set<String> added = new HashSet<>();
        for (Map.Entry<String, Integer> entry : scoredSentences) {
            if (!added.contains(entry.getKey())) {
                results.add(entry.getKey());
                added.add(entry.getKey());
                if (results.size() >= maxResults) break;
            }
        }

        System.out.println("✅ [Search] Найдено инструкций: " + results.size());
        return results;
    }

    private String cleanSentence(String text) {
        text = text.replaceAll("\\s+", " ").trim();
        text = text.replaceAll("([а-яА-Яa-zA-Z]+)-\\s*\\n\\s*([а-яА-Яa-zA-Z]+)", "$1$2");
        text = text.replaceAll("([А-Я])\\s+([А-Я])", "$1$2");
        return text;
    }

    public static class SearchRequest {
        private String query;
        public String getQuery() { return query; }
        public void setQuery(String query) { this.query = query; }
    }

    public static class CarRequest {
        private String brand, model, engine, equipment, generation;
        private Integer year;

        public String getBrand() { return brand; }
        public void setBrand(String brand) { this.brand = brand; }
        public String getModel() { return model; }
        public void setModel(String model) { this.model = model; }
        public Integer getYear() { return year; }
        public void setYear(Integer year) { this.year = year; }
        public String getEngine() { return engine; }
        public void setEngine(String engine) { this.engine = engine; }
        public String getEquipment() { return equipment; }
        public void setEquipment(String equipment) { this.equipment = equipment; }
        public String getGeneration() { return generation; }
        public void setGeneration(String generation) { this.generation = generation; }
    }

    public static class SessionRequest {
        private Integer carId;
        public Integer getCarId() { return carId; }
        public void setCarId(Integer carId) { this.carId = carId; }
    }

    public static class MessageRequest {
        private String message;
        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }
    }

    public static class PageRequest {
        private Integer pageNumber;
        private String pdfPath;
        private String searchQuery;

        public Integer getPageNumber() { return pageNumber; }
        public void setPageNumber(Integer pageNumber) { this.pageNumber = pageNumber; }
        public String getPdfPath() { return pdfPath; }
        public void setPdfPath(String pdfPath) { this.pdfPath = pdfPath; }
        public String getSearchQuery() { return searchQuery; }
        public void setSearchQuery(String searchQuery) { this.searchQuery = searchQuery; }
    }

    @GetMapping("/manuals/page")
    public ResponseEntity<byte[]> getManualPageImage(
            @RequestParam String path,
            @RequestParam int page) {
        try {
            System.out.println("🖼️ [Image] Запрос изображения: path=" + path + ", page=" + page);

            File manualFile = new File(path);
            if (!manualFile.isAbsolute()) {
                manualFile = manualFile.getCanonicalFile();
            }

            byte[] imageData = manualService.convertPageToImage(manualFile.getAbsolutePath(), page);

            if (imageData == null) {
                System.err.println("❌ [Image] Не удалось конвертировать страницу");
                return ResponseEntity.notFound().build();
            }

            System.out.println("✅ [Image] Изображение отправлено: " + imageData.length + " байт");

            return ResponseEntity.ok()
                    .contentType(MediaType.IMAGE_PNG)
                    .body(imageData);

        } catch (Exception e) {
            System.err.println("❌ [Image] Ошибка: " + e.getMessage());
            e.printStackTrace();
            return ResponseEntity.status(500).build();
        }
    }

    @GetMapping("/years")
    public ResponseEntity<?> getYearsByBrandAndModel(
            @RequestParam String brand,
            @RequestParam String model) {
        try {
            List<Integer> years = carRepository.findYearsByBrandAndModel(brand, model);
            return ResponseEntity.ok(years);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка получения годов: " + e.getMessage());
        }
    }

    @GetMapping("/car-details")
    public ResponseEntity<?> getCarDetails(
            @RequestParam String brand,
            @RequestParam String model,
            @RequestParam Integer year) {
        List<Car> cars = carRepository.findByBrandAndModelAndYear(brand, model, year);
        if (cars.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        Car car = cars.get(0);
        Map<String, Object> response = new HashMap<>();
        response.put("carId", car.getCarID());
        response.put("brand", car.getBrand());
        response.put("model", car.getModel());
        response.put("year", car.getYear());
        response.put("engine", car.getTypeEngine());
        response.put("equipment", car.getEquipment());
        response.put("generation", car.getGeneration());
        response.put("imagePath", car.getImagePath());
        return ResponseEntity.ok(response);
    }
}