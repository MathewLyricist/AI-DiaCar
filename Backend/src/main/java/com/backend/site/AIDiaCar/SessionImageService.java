package com.backend.site.AIDiaCar;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Service
public class SessionImageService {

    @Value("${session.images.path:./session-images}")
    private String imagesRootPath;

    public String savePageImage(Integer sessionId, Integer pageNumber, byte[] imageData) throws IOException {
        Path sessionDir = Paths.get(imagesRootPath, sessionId.toString());
        if (!Files.exists(sessionDir)) {
            Files.createDirectories(sessionDir);
        }
        String filename = String.format("page_%d.png", pageNumber);
        Path filePath = sessionDir.resolve(filename);
        Files.write(filePath, imageData);

        return ServletUriComponentsBuilder.fromCurrentContextPath()
                .path("/api/session-images/")
                .path(sessionId.toString())
                .path("/")
                .path(filename)
                .build()
                .toUriString();
    }

    public void deleteSessionImages(Integer sessionId) throws IOException {
        Path sessionDir = Paths.get(imagesRootPath, sessionId.toString());
        if (Files.exists(sessionDir)) {
            Files.walk(sessionDir)
                    .sorted((a, b) -> b.compareTo(a))
                    .forEach(path -> {
                        try {
                            Files.deleteIfExists(path);
                        } catch (IOException e) {
                        }
                    });
        }
    }

    public void cleanOldSessions(int daysOld) {
        try {
            Path root = Paths.get(imagesRootPath);
            if (!Files.exists(root)) return;
            long cutoff = System.currentTimeMillis() - daysOld * 24L * 60 * 60 * 1000;
            Files.list(root).forEach(path -> {
                try {
                    if (Files.getLastModifiedTime(path).toMillis() < cutoff) {
                        deleteSessionImages(Integer.parseInt(path.getFileName().toString()));
                    }
                } catch (IOException e) {
                }
            });
        } catch (IOException e) {
        }
    }
}