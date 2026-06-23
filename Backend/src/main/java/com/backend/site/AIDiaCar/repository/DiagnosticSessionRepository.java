package com.backend.site.AIDiaCar.repository;

import com.backend.site.AIDiaCar.DiagnosticSession;
import com.backend.site.AIDiaCar.models.Account;
import com.backend.site.AIDiaCar.models.Car;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface DiagnosticSessionRepository extends JpaRepository<DiagnosticSession, Integer> {

    List<DiagnosticSession> findByUserOrderByCreatedAtDesc(Account user);

    List<DiagnosticSession> findByUserAndStatus(Account user, String status);

    List<DiagnosticSession> findByUserAndStatusOrderByCreatedAtDesc(Account user, String status);

    List<DiagnosticSession> findByLastActivityAtBefore(LocalDateTime dateTime);

    List<DiagnosticSession> findByUserAndCarAndStatus(Account user, Car car, String status);
}