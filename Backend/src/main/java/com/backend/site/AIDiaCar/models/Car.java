package com.backend.site.AIDiaCar.models;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
@Entity(name = "cars")
@Table(name = "cars")
public class Car {

    @Id
    @Column(name = "car_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer carID;

    @Column(nullable = false)
    private String brand;

    @Column(nullable = false)
    private String model;

    @Column(nullable = false)
    private Integer year;

    @Column(name = "engine_type")
    private String typeEngine;

    @Column
    private Integer capacity;

    @Column
    private String transmission;

    @Column
    private String equipment;

    @Column
    private String generation;

    @Column(name = "manual_path")
    private String manualPath;

    @Column(name = "image_path")
    private String imagePath;

    public Car() {}

    public Car(String brand, String model, Integer year, String typeEngine,
               String equipment, String generation) {
        this.brand = brand;
        this.model = model;
        this.year = year;
        this.typeEngine = typeEngine;
        this.equipment = equipment;
        this.generation = generation;
    }

}