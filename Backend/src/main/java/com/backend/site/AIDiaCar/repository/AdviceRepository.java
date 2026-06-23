package com.backend.site.AIDiaCar.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.backend.site.AIDiaCar.models.Advice;

import java.util.List;

public interface AdviceRepository extends JpaRepository<Advice, Integer> {
    List<Advice> findAllByOrderByCreatedAtDesc();
}