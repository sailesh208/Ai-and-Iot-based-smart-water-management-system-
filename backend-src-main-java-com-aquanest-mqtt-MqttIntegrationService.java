package com.aquanest.mqtt;

import com.aquanest.dto.MqttTelemetryDTO;
import com.aquanest.service.ConsumptionService;
import com.aquanest.service.LeakageDetectionService;
import com.aquanest.service.TankService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.paho.client.mqttv3.*;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;

@Service
public class MqttIntegrationService implements MqttCallback {

    private static final Logger log = LoggerFactory.getLogger(MqttIntegrationService.class);

    @Value("${mqtt.broker.url:tcp://broker.hivemq.com:1883}")
    private String brokerUrl;

    @Value("${mqtt.client.id:aquanest-backend-server}")
    private String clientId;

    @Value("${data.mode:SIMULATION}")
    private String dataMode;

    private final TankService tankService;
    private final ConsumptionService consumptionService;
    private final LeakageDetectionService leakageService;
    private final ObjectMapper objectMapper;

    private MqttClient client;

    public MqttIntegrationService(TankService tankService, ConsumptionService consumptionService,
                                  LeakageDetectionService leakageService, ObjectMapper objectMapper) {
        this.tankService = tankService;
        this.consumptionService = consumptionService;
        this.leakageService = leakageService;
        this.objectMapper = objectMapper;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void init() {
        if ("SIMULATION".equalsIgnoreCase(dataMode)) {
            log.info("AquaNest MQTT running in autonomous SIMULATION mode. External broker connection is optional.");
        }
        tryConnectAsync();
    }

    private void tryConnectAsync() {
        new Thread(() -> {
            try {
                client = new MqttClient(brokerUrl, clientId + "-" + System.currentTimeMillis(), new MemoryPersistence());
                MqttConnectOptions options = new MqttConnectOptions();
                options.setCleanSession(true);
                options.setConnectionTimeout(10);
                options.setKeepAliveInterval(30);
                options.setAutomaticReconnect(true);

                client.setCallback(this);
                client.connect(options);
                log.info("Connected to MQTT Broker: {}", brokerUrl);

                client.subscribe("aquanest/#", 1);
                log.info("Subscribed to topic: aquanest/#");
            } catch (MqttException e) {
                log.warn("MQTT Broker connection deferred ({}: {}). System will operate in standalone simulated mode.",
                        brokerUrl, e.getMessage());
            }
        }).start();
    }

    public void publishPumpControl(String command, String mode) {
        if (client != null && client.isConnected()) {
            try {
                String payload = String.format("{\"command\":\"%s\",\"mode\":\"%s\",\"timestamp\":\"%s\"}",
                        command, mode, java.time.Instant.now().toString());
                MqttMessage message = new MqttMessage(payload.getBytes(StandardCharsets.UTF_8));
                message.setQos(1);
                client.publish("aquanest/pump/control", message);
                log.info("Published pump command to aquanest/pump/control: {}", payload);
            } catch (MqttException e) {
                log.error("Failed to publish pump control message over MQTT", e);
            }
        }
    }

    @Override
    public void connectionLost(Throwable cause) {
        log.warn("MQTT connection lost: {}. Reconnect will be attempted automatically.", cause != null ? cause.getMessage() : "Unknown");
    }

    @Override
    public void messageArrived(String topic, MqttMessage message) {
        try {
            String json = new String(message.getPayload(), StandardCharsets.UTF_8);
            MqttTelemetryDTO dto = objectMapper.readValue(json, MqttTelemetryDTO.class);

            if (topic.contains("tank/readings") && dto.getTankLevelPercent() != null) {
                tankService.processTankReading(dto.getTankLevelPercent(), dto.getDeviceId() != null ? dto.getDeviceId() : "JSN_SR04T");
            } else if (topic.contains("/flow") && dto.getHouseId() != null) {
                double rate = (dto.getFlowRate() != null) ? dto.getFlowRate() : 0.0;
                long pulses = (dto.getPulseCount() != null) ? dto.getPulseCount() : 0L;
                double cum = (dto.getCumulativeLitres() != null) ? dto.getCumulativeLitres() : 0.0;
                consumptionService.processFlowReading(dto.getHouseId(), rate, pulses, cum);
            } else if (topic.contains("pressure/readings") && dto.getPressureBar() != null) {
                leakageService.evaluatePipeLeakage(15.0, 14.5, dto.getPressureBar());
            }
        } catch (Exception e) {
            log.error("Error processing MQTT message on topic {}: {}", topic, e.getMessage());
        }
    }

    @Override
    public void deliveryComplete(IMqttDeliveryToken token) {
        // Ack callback
    }
}
