package com.backend.site.AIDiaCar.models;

import jakarta.persistence.*;
import java.util.Date;

@Entity(name = "manuals")
@Table(name = "manuals")
public class Manual {
    @Id
    @Column(name = "manual_id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer manualID;

    @Column(nullable = false)
    private String brand;

    @Column
    private String model;

    @Column(name = "directory_path", nullable = false)
    private String directoryPath;

    @Column(name = "file_path")
    private String filePath;

    @Column(name = "manual_type")
    private String manualType = "SPECIFIC";

    @Column(name = "processed_text", columnDefinition = "TEXT")
    private String processedText;

    @Column(name = "uploaded_at", nullable = false)
    @Temporal(TemporalType.TIMESTAMP)
    private Date uploadedAt;

    @Column(name = "processed_at")
    @Temporal(TemporalType.TIMESTAMP)
    private Date processedAt;

    public Manual() {
        this.uploadedAt = new Date();
    }

    public Manual(String brand, String model, String directoryPath) {
        this.brand = brand;
        this.model = model;
        this.directoryPath = directoryPath;
        this.uploadedAt = new Date();
    }

    public Integer getManualID() { return manualID; }
    public void setManualID(Integer manualID) { this.manualID = manualID; }

    public String getBrand() { return brand; }
    public void setBrand(String brand) { this.brand = brand; }

    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }

    public String getDirectoryPath() { return directoryPath; }
    public void setDirectoryPath(String directoryPath) { this.directoryPath = directoryPath; }

    public String getFilePath() { return filePath; }
    public void setFilePath(String filePath) { this.filePath = filePath; }

    public String getManualType() { return manualType; }
    public void setManualType(String manualType) { this.manualType = manualType; }

    public String getProcessedText() { return processedText; }
    public void setProcessedText(String processedText) { this.processedText = processedText; }

    public Date getUploadedAt() { return uploadedAt; }
    public void setUploadedAt(Date uploadedAt) { this.uploadedAt = uploadedAt; }

    public Date getProcessedAt() { return processedAt; }
    public void setProcessedAt(Date processedAt) { this.processedAt = processedAt; }
}