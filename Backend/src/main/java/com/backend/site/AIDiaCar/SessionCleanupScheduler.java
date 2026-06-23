package com.backend.site.AIDiaCar;

import com.backend.site.AIDiaCar.repository.DiagnosticSessionRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import com.backend.site.AIDiaCar.SessionImageService;
import com.backend.site.AIDiaCar.DiagnosticSession;

import java.time.LocalDateTime;
import java.util.List;

@Component
@EnableScheduling
public class SessionCleanupScheduler {

    private final DiagnosticSessionRepository sessionRepository;
    private final SessionImageService sessionImageService;

    @Value("${session.expiration.days:7}")
    private int expirationDays;

    public SessionCleanupScheduler(DiagnosticSessionRepository sessionRepository,
                                   SessionImageService sessionImageService) {
        this.sessionRepository = sessionRepository;
        this.sessionImageService = sessionImageService;
    }

    @Scheduled(cron = "0 0 3 * * ?")
    @Transactional
    public void cleanExpiredSessions() {
        LocalDateTime cutoff = LocalDateTime.now().minusDays(expirationDays);
        List<DiagnosticSession> expiredSessions = sessionRepository.findByLastActivityAtBefore(cutoff);
        for (DiagnosticSession session : expiredSessions) {
            try {
                sessionImageService.deleteSessionImages(session.getSessionID());
                sessionRepository.delete(session);
            } catch (Exception e) {
                System.err.println("Ошибка удаления сессии " + session.getSessionID() + ": " + e.getMessage());
            }
        }
    }
}