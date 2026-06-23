package com.backend.site.AIDiaCar.models;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "feedback")
public class Feedback {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    @Setter
    @Getter
    @Column(name = "user_id")
    private Integer userId;
    @Setter
    @Getter
    private String type;
    @Setter
    @Getter
    private String subject;
    @Setter
    @Getter
    private String comment;
    @Setter
    @Getter
    private String email;
    @Setter
    @Getter
    private String status;
    @Setter
    @Getter
    @Column(name = "admin_response")
    private String adminResponse;
    @Setter
    @Getter
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    @Setter
    @Getter
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    @Setter
    @Getter
    @Column(name = "submitted_date")
    private LocalDateTime submittedDate;
    @Setter
    @Getter
    @Column(name = "submitted_time")
    private LocalDateTime submittedTime;
}