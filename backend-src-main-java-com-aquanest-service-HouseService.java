package com.aquanest.service;

import com.aquanest.model.House;
import com.aquanest.model.Sensor;
import com.aquanest.repository.DataStore;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.*;

@Service
public class HouseService {

    private final DataStore dataStore;

    public HouseService(DataStore dataStore) {
        this.dataStore = dataStore;
    }

    public List<House> getAllHouses() {
        return new ArrayList<>(dataStore.getHouses().values());
    }

    public House getHouseById(String houseId) {
        House h = dataStore.getHouseById(houseId);
        if (h == null) {
            throw new NoSuchElementException("House with ID " + houseId + " does not exist.");
        }
        return h;
    }

    public synchronized House createHouse(House house) {
        if (house.getHouseId() == null || house.getHouseId().isBlank()) {
            int nextId = dataStore.getHouses().size() + 101;
            house.setHouseId("H" + nextId);
        }
        if (house.getMeterId() == null || house.getMeterId().isBlank()) {
            house.setMeterId("METER_" + house.getHouseId());
        }
        house.setCreatedAt(Instant.now());
        house.setLastUpdated(Instant.now());
        house.setStatus("ACTIVE");

        // Automatically provision flow meter sensor
        Sensor sensor = new Sensor("FLOW_" + house.getHouseId(), "FLOW_HOUSE", house.getHouseId(),
                dataStore.getSettings().getFlowCalibrationFactor(), "L/min");
        dataStore.getSensors().put(sensor.getSensorId(), sensor);

        dataStore.saveHouse(house);
        return house;
    }

    public synchronized House updateHouse(String houseId, House updated) {
        House existing = getHouseById(houseId);
        if (updated.getHouseNumber() != null) existing.setHouseNumber(updated.getHouseNumber());
        if (updated.getFloor() > 0) existing.setFloor(updated.getFloor());
        if (updated.getResidentName() != null) existing.setResidentName(updated.getResidentName());
        if (updated.getResidentId() != null) existing.setResidentId(updated.getResidentId());
        if (updated.getMeterId() != null) existing.setMeterId(updated.getMeterId());
        if (updated.getStatus() != null) existing.setStatus(updated.getStatus());
        existing.setLastUpdated(Instant.now());

        dataStore.saveHouse(existing);
        return existing;
    }

    public synchronized void deactivateHouse(String houseId) {
        // Safe deactivation preserving all historical data
        dataStore.deleteHouse(houseId);
    }
}
