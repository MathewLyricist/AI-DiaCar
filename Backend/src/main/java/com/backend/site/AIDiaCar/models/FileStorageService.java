package com.backend.site.AIDiaCar.models;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

@Service
public class FileStorageService {

    @Value("${manuals.images.path:uploads/manual-images}")
    private String uploadDir;

    public String savePageImage(byte[] imageBytes, Integer sessionId, Integer pageNumber) throws IOException {
        Path uploadPath = Paths.get(uploadDir);
        if (!Files.exists(uploadPath)) {
            Files.createDirectories(uploadPath);
        }

        String fileName = "session_" + sessionId + "_page_" + pageNumber + "_" +
                UUID.randomUUID().toString() + ".png";

        Path filePath = uploadPath.resolve(fileName);
        Files.write(filePath, imageBytes);

        return "/api/manuals/images/" + fileName;
    }

    public byte[] getImage(String fileName) throws IOException {
        Path filePath = Paths.get(uploadDir).resolve(fileName);
        return Files.readAllBytes(filePath);
    }
}