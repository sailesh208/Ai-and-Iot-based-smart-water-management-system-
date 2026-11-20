package com.aquanest.controller;

import com.aquanest.model.Sensor;
import com.aquanest.repository.DataStore;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.NoSuchElementException;

@RestController
@RequestMapping("/api/sensors")
@CrossOrigin(origins = "*")
public class SensorController {

    private final DataStore dataStore;

    public SensorController(DataStore dataStore) {
        this.dataStore = dataStore;
    }

    @GetMapping
    public ResponseEntity<List<Sensor>> getAllSensors() {
        return ResponseEntity.ok(new ArrayList<>(dataStore.getSensors().values()));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Sensor> getSensorById(@PathVariable(name = "id") String id) {
        Sensor s = dataStore.getSensors().get(id);
        if (s == null) {
            throw new NoSuchElementException("Sensor " + id + " not found.");
        }
        return ResponseEntity.ok(s);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Sensor> updateSensor(@PathVariable(name = "id") String id, @RequestBody Sensor updated) {
        Sensor s = dataStore.getSensors().get(id);
        if (s == null) {
            throw new NoSuchElementException("Sensor " + id + " not found.");
        }
        if (updated.getCalibrationFactor() > 0) s.setCalibrationFactor(updated.getCalibrationFactor());
        if (updated.getStatus() != null) s.setStatus(updated.getStatus());
        dataStore.getSensors().put(id, s);
        return ResponseEntity.ok(s);
    }
}
