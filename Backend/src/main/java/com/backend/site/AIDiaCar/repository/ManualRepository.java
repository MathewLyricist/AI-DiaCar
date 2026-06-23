package com.backend.site.AIDiaCar.repository;

import com.backend.site.AIDiaCar.models.Manual;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ManualRepository extends JpaRepository<Manual, Integer> {

    List<Manual> findByBrandAndModel(String brand, String model);

    @Query("SELECT m FROM manuals m WHERE m.brand = :brand AND m.model = :model " +
            "ORDER BY CASE m.manualType WHEN 'SPECIFIC' THEN 1 WHEN 'BRAND_COMMON' THEN 2 ELSE 3 END")
    List<Manual> findByBrandAndModelOrdered(@Param("brand") String brand, @Param("model") String model);

    @Query("SELECT m FROM manuals m WHERE LOWER(m.brand) = LOWER(:brand) AND LOWER(m.model) = LOWER(:model) " +
            "ORDER BY CASE m.manualType WHEN 'SPECIFIC' THEN 1 WHEN 'BRAND_COMMON' THEN 2 ELSE 3 END")
    List<Manual> findByBrandAndModelOrderedIgnoreCase(@Param("brand") String brand, @Param("model") String model);

    List<Manual> findByBrandAndManualType(String brand, String manualType);
    List<Manual> findByBrand(String brand);
    List<Manual> findByManualType(String manualType);
    boolean existsByBrandAndModel(String brand, String model);
}