package com.backend.site.AIDiaCar;

import jakarta.persistence.*;

import java.util.Date;

@Entity(name = "users")
@Table(name = "users")
public class Account{
    @Column(name = "user_id")
    private Integer userID;
    @Column
    private String name;
    @Column
    private String email;
    @Column
    private String passwordHash;
    @Column(name = "created_at")
    private Date createdAt;
    @Column
    private String enterprise;
}