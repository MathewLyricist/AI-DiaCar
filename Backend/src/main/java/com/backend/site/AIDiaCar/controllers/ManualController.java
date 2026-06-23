package com.backend.site.AIDiaCar.controllers;

import com.backend.site.AIDiaCar.models.Manual;
import com.backend.site.AIDiaCar.repository.ManualRepository;
import com.backend.site.AIDiaCar.models.ManualService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/manuals")
@CrossOrigin(origins = "http://localhost:5173")
public class ManualController {

    private final ManualRepository manualRepository;
    private final ManualService manualService;

    public ManualController(ManualRepository manualRepository, ManualService manualService) {
        this.manualRepository = manualRepository;
        this.manualService = manualService;
    }

    @PostMapping("/scan")
    public ResponseEntity<?> scanManuals() {
        try {
            manualService.scanAndRegisterManuals();
            return ResponseEntity.ok("Сканирование завершено");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Ошибка сканирования: " + e.getMessage());
        }
    }

    @GetMapping("/brands")
    public ResponseEntity<?> getBrands() {
        List<String> brands = manualService.getAvailableBrands();
        System.out.println("Бренды: " + brands);
        return ResponseEntity.ok(brands);
    }

    @GetMapping("/models")
    public ResponseEntity<?> getModels(@RequestParam String brand) {
        List<String> models = manualService.getModelsForBrand(brand);
        System.out.println("Модели для " + brand + ": " + models);
        return ResponseEntity.ok(models);
    }

    @GetMapping("/search")
    public ResponseEntity<?> searchManual(
            @RequestParam String brand,
            @RequestParam String model) {

        Optional<Manual> manual = manualService.findManualForCar(brand, model);

        if (manual.isPresent()) {
            Manual m = manual.get();
            Map<String, Object> response = new HashMap<>();
            response.put("found", true);
            response.put("manualId", m.getManualID());
            response.put("brand", m.getBrand());
            response.put("model", m.getModel());
            response.put("manualType", m.getManualType());
            response.put("hasText", m.getProcessedText() != null && !m.getProcessedText().isEmpty());
            response.put("textLength", m.getProcessedText() != null ? m.getProcessedText().length() : 0);
            return ResponseEntity.ok(response);
        } else {
            Map<String, Object> response = new HashMap<>();
            response.put("found", false);
            response.put("message", "Мануал не найден. Будет использована общая диагностика.");
            return ResponseEntity.ok(response);
        }
    }

    @GetMapping("/{manualId}/text")
    public ResponseEntity<?> getManualText(@PathVariable Integer manualId) {
        return manualRepository.findById(manualId)
                .map(m -> {
                    Map<String, Object> response = new HashMap<>();
                    response.put("manualId", manualId);
                    response.put("text", m.getProcessedText());
                    response.put("length", m.getProcessedText() != null ? m.getProcessedText().length() : 0);
                    return ResponseEntity.ok(response);
                })
                .orElseGet(() -> {
                    Map<String, Object> errorResponse = new HashMap<>();
                    errorResponse.put("error", "Текст мануала не найден");
                    errorResponse.put("manualId", manualId);
                    return ResponseEntity.status(404).body(errorResponse);
                });
    }

    @GetMapping("/all")
    public ResponseEntity<?> getAllManuals() {
        List<Manual> manuals = manualRepository.findAll();

        List<Map<String, Object>> result = manuals.stream().map(m -> {
            Map<String, Object> map = new HashMap<>();
            map.put("manualId", m.getManualID());
            map.put("brand", m.getBrand());
            map.put("model", m.getModel());
            map.put("manualType", m.getManualType());
            map.put("hasText", m.getProcessedText() != null);
            map.put("uploadedAt", m.getUploadedAt());
            return map;
        }).collect(Collectors.toList());

        return ResponseEntity.ok(result);
    }
}