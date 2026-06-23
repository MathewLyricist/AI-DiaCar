package com.backend.site.AIDiaCar.repository;

import com.backend.site.AIDiaCar.models.Car;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface CarRepository extends JpaRepository<Car, Integer> {
    List<Car> findByBrand(String brand);
    @Query("SELECT DISTINCT c.year FROM cars c WHERE c.brand = :brand AND c.model = :model ORDER BY c.year")
    List<Integer> findYearsByBrandAndModel(@Param("brand") String brand, @Param("model") String model);
    List<Car> findByBrandAndModelAndYear(String brand, String model, Integer year);
}