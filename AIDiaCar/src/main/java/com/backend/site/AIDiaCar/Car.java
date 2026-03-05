package com.backend.site.AIDiaCar;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

@Entity(name = "cars")
@Table(name = "cars")
public class Car {
    @Column(name = "car_id")
    private Integer carID;
    @Column
    private String brand;
    @Column
    private String model;
    @Column
    private Integer year;
    @Column(name = "engine_type")
    private String typeEngine;
    @Column
    private Integer capacity;
    @Column
    private String transmission;
    @Column
    private String equipment;
}
