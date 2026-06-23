package com.backend.site.AIDiaCar.models;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import java.time.LocalDateTime;

@Entity
@Table(name = "news")
public class News {
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
    @Column(length = 500)
    private String imageUrl;

    @Setter @Getter
    @Column(length = 500)
    private String videoUrl;

    @Setter @Getter
    @Column(length = 50)
    private String date;

    @Setter @Getter
    private Integer authorId;

    @Setter @Getter
    private LocalDateTime createdAt;
}