package com.backend.site.AIDiaCar;

import com.backend.site.AIDiaCar.models.Account;
import com.backend.site.AIDiaCar.models.Car;
import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.Date;

@Entity(name = "diagnostic_sessions")
@Table(name = "diagnostic_sessions")
public class DiagnosticSession {

    @Id
    @Column(name = "session_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer sessionID;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private Account user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "car_id", nullable = false)
    private Car car;

    @Column(name = "created_at", nullable = false)
    @Temporal(TemporalType.TIMESTAMP)
    private Date createdAt;

    @Column(name = "status")
    private String status = "ACTIVE";

    @Column(name = "manual_used_path")
    private String manualUsedPath;

    @Column(name = "expires_at")
    @Temporal(TemporalType.TIMESTAMP)
    private Date expiresAt;

    @Column(name = "completed_at")
    @Temporal(TemporalType.TIMESTAMP)
    private Date completedAt;

    @Column(name = "session_name")
    private String sessionName;

    @Column(name = "last_activity_at")
    private LocalDateTime lastActivityAt;

    public DiagnosticSession() {
        this.createdAt = new Date();
        this.expiresAt = new Date(System.currentTimeMillis() + 7L * 24 * 60 * 60 * 1000);
        this.status = "ACTIVE";
        this.lastActivityAt = LocalDateTime.now();
    }

    public DiagnosticSession(Account user, Car car, String manualUsedPath) {
        this.user = user;
        this.car = car;
        this.manualUsedPath = manualUsedPath;
        this.createdAt = new Date();
        this.status = "ACTIVE";
        this.expiresAt = new Date(System.currentTimeMillis() + 7L * 24 * 60 * 60 * 1000);
        this.sessionName = car.getBrand() + " " + car.getModel() + " (" + car.getYear() + ")";
        this.lastActivityAt = LocalDateTime.now();
    }

    public Integer getSessionID() { return sessionID; }
    public void setSessionID(Integer sessionID) { this.sessionID = sessionID; }

    public Account getUser() { return user; }
    public void setUser(Account user) { this.user = user; }

    public Car getCar() { return car; }
    public void setCar(Car car) { this.car = car; }

    public Date getCreatedAt() { return createdAt; }
    public void setCreatedAt(Date createdAt) { this.createdAt = createdAt; }

    public String getStatus() { return status; }
    public void setStatus(String status) {
        this.status = status;
        if ("COMPLETED".equals(status)) {
            this.completedAt = new Date();
        }
    }

    public String getManualUsedPath() { return manualUsedPath; }
    public void setManualUsedPath(String manualUsedPath) { this.manualUsedPath = manualUsedPath; }

    public Date getExpiresAt() { return expiresAt; }
    public void setExpiresAt(Date expiresAt) { this.expiresAt = expiresAt; }

    public Date getCompletedAt() { return completedAt; }
    public void setCompletedAt(Date completedAt) { this.completedAt = completedAt; }

    public String getSessionName() { return sessionName; }
    public void setSessionName(String sessionName) { this.sessionName = sessionName; }

    public LocalDateTime getLastActivityAt() { return lastActivityAt; }
    public void setLastActivityAt(LocalDateTime lastActivityAt) { this.lastActivityAt = lastActivityAt; }
}