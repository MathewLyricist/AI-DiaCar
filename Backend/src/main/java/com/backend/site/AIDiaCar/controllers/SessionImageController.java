package com.backend.site.AIDiaCar.controllers;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.nio.file.Path;
import java.nio.file.Paths;

@RestController
@RequestMapping("/api/session-images")
public class SessionImageController {

    @Value("${session.images.path:./session-images}")
    private String imagesRootPath;

    @GetMapping("/{sessionId}/{filename}")
    public ResponseEntity<Resource> getImage(@PathVariable Integer sessionId,
                                             @PathVariable String filename) {
        Path filePath = Paths.get(imagesRootPath, sessionId.toString(), filename);
        Resource resource = new FileSystemResource(filePath.toFile());
        if (!resource.exists()) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok()
                .contentType(MediaType.IMAGE_PNG)
                .body(resource);
    }
}