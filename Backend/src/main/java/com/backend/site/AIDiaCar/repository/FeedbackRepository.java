package com.backend.site.AIDiaCar.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.backend.site.AIDiaCar.models.Feedback;

import java.time.LocalDateTime;
import java.util.List;

public interface FeedbackRepository extends JpaRepository<Feedback, Integer> {
    long countByUserIdAndCreatedAtBetween(Integer userId, LocalDateTime start, LocalDateTime end);
    List<Feedback> findAllByOrderByCreatedAtDesc();
}
