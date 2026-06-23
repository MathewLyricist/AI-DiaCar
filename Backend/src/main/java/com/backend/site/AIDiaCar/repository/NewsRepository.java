package com.backend.site.AIDiaCar.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.backend.site.AIDiaCar.models.News;

import java.util.List;

public interface NewsRepository extends JpaRepository<News, Integer> {
    List<News> findAllByOrderByDateDesc();
}
