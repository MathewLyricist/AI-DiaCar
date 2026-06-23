package com.backend.site.AIDiaCar.models;

import jakarta.persistence.*;
import java.util.Date;

@Entity(name = "users")
@Table(name = "users")
public class Account {

    @Id
    @Column(name = "user_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer userID;

    @Column(nullable = false)
    private String name;

    @Column(unique = true)
    private String email;

    @Column
    private String passwordHash;

    @Column(name = "created_at", nullable = false)
    @Temporal(TemporalType.TIMESTAMP)
    private Date createdAt;

    @Column
    private String enterprise;

    @Column(length = 20)
    private String phone;

    @Column(nullable = false)
    private String role = "ROLE_USER";

    public Account() {
        this.createdAt = new Date();
    }

    public Account(String name, String email, String passwordHash, String enterprise, String phone) {
        this.name = name;
        this.email = email;
        this.passwordHash = passwordHash;
        this.enterprise = enterprise;
        this.phone = phone;
        this.createdAt = new Date();
        this.role = "ROLE_USER";
    }

    public Integer getUserID() { return userID; }
    public void setUserID(Integer userID) { this.userID = userID; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getPasswordHash() { return passwordHash; }
    public void setPasswordHash(String passwordHash) { this.passwordHash = passwordHash; }
    public Date getCreatedAt() { return createdAt; }
    public void setCreatedAt(Date createdAt) { this.createdAt = createdAt; }
    public String getEnterprise() { return enterprise; }
    public void setEnterprise(String enterprise) { this.enterprise = enterprise; }
    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }
    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }
}