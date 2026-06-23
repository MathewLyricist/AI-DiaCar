package com.backend.site.AIDiaCar.models;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.time.LocalDateTime;

@Entity
@Table(name = "advice")
public class Advice {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Setter @Getter
    private Integer id;

    @Setter @Getter
    @Column(length = 255)
    private String title;

    @Setter @Getter
    @Column(columnDefinition = "TEXT")
    private String content;

    @Setter @Getter
    @Column(length = 100)
    private String category;

    @Setter @Getter
    @Column(length = 20)
    private String difficulty;

    @Setter @Getter
    @Column(length = 500)
    private String imageUrl;

    @Setter @Getter
    private Integer authorId;

    @Setter @Getter
    private LocalDateTime createdAt;
}