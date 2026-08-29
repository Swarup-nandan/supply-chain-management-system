package com.swarup.supplychain.service;

import com.swarup.supplychain.model.Shipment;
import com.swarup.supplychain.repository.ShipmentRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;

@Service
public class RiskService {

    private final ShipmentRepository shipmentRepository;
    private final MLClientService mlClientService;

    public RiskService(ShipmentRepository shipmentRepository, MLClientService mlClientService) {
        this.shipmentRepository = shipmentRepository;
        this.mlClientService = mlClientService;
    }

    public Shipment createShipment(Shipment shipment) {
        if (shipment.getShipmentId() == null || shipment.getShipmentId().isEmpty()) {
            shipment.setShipmentId("SHP-" + System.currentTimeMillis());
        }
        if (shipment.getStatus() == null) {
            shipment.setStatus("IN_TRANSIT");
        }
        shipment = assessRisk(shipment);
        return shipmentRepository.save(shipment);
    }

    public Shipment assessRisk(Shipment shipment) {
        Map<String, Object> mlResult = mlClientService.predictRisk(shipment);

        shipment.setWeatherRiskScore(toDouble(mlResult.get("weather_risk_score")));
        shipment.setGeopoliticalRiskScore(toDouble(mlResult.get("geopolitical_risk_score")));
        shipment.setSupplierRiskScore(toDouble(mlResult.get("supplier_risk_score")));
        shipment.setOverallRiskScore(toDouble(mlResult.get("overall_risk_score")));
        shipment.setRiskLevel((String) mlResult.getOrDefault("risk_level", "LOW"));

        // Trigger alerts for HIGH or CRITICAL risk
        if ("HIGH".equals(shipment.getRiskLevel()) || "CRITICAL".equals(shipment.getRiskLevel())) {
            shipment.setAlertTriggered(true);
            shipment.setAlertMessage(buildAlertMessage(shipment));
            shipment.setStatus("AT_RISK");
        }

        return shipment;
    }

    public Shipment updateShipmentStatus(Long id, String status) {
        Shipment shipment = shipmentRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Shipment not found"));
        shipment.setStatus(status);
        if ("DELIVERED".equals(status)) {
            shipment.setActualDelivery(LocalDateTime.now());
            shipment.setAlertTriggered(false);
        }
        return shipmentRepository.save(shipment);
    }

    public List<Shipment> getAllShipments() {
        return shipmentRepository.findAllOrderByCreatedAtDesc();
    }

    public Optional<Shipment> getShipmentById(Long id) {
        return shipmentRepository.findById(id);
    }

    public List<Shipment> getAlertedShipments() {
        return shipmentRepository.findByAlertTriggeredTrue();
    }

    public List<Shipment> getHighRiskShipments() {
        return shipmentRepository.findHighRiskShipments(0.5);
    }

    public Map<String, Object> getDashboardStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("total", shipmentRepository.count());
        stats.put("critical", shipmentRepository.countByRiskLevel("CRITICAL"));
        stats.put("high", shipmentRepository.countByRiskLevel("HIGH"));
        stats.put("medium", shipmentRepository.countByRiskLevel("MEDIUM"));
        stats.put("low", shipmentRepository.countByRiskLevel("LOW"));
        stats.put("alerts", shipmentRepository.findByAlertTriggeredTrue().size());
        Double avg = shipmentRepository.averageRiskScore();
        stats.put("averageRisk", avg != null ? Math.round(avg * 100.0) / 100.0 : 0.0);
        stats.put("inTransit", shipmentRepository.findByStatus("IN_TRANSIT").size());
        stats.put("atRisk", shipmentRepository.findByStatus("AT_RISK").size());
        stats.put("delayed", shipmentRepository.findByStatus("DELAYED").size());
        return stats;
    }

    public void deleteShipment(Long id) {
        shipmentRepository.deleteById(id);
    }

    private String buildAlertMessage(Shipment shipment) {
        StringBuilder msg = new StringBuilder();
        msg.append("⚠️ ").append(shipment.getRiskLevel()).append(" RISK ALERT for shipment ")
                .append(shipment.getShipmentId()).append(". ");
        if (shipment.getWeatherRiskScore() > 0.6)
            msg.append("Severe weather conditions detected. ");
        if (shipment.getGeopoliticalRiskScore() > 0.6)
            msg.append("Geopolitical instability on route. ");
        if (shipment.getSupplierRiskScore() > 0.6)
            msg.append("Carrier/supplier reliability issues. ");
        if (shipment.getDelayDays() > 3)
            msg.append("Significant delay of ").append(shipment.getDelayDays()).append(" days. ");
        return msg.toString().trim();
    }

    private double toDouble(Object val) {
        if (val == null) return 0.0;
        if (val instanceof Number) return ((Number) val).doubleValue();
        try { return Double.parseDouble(val.toString()); }
        catch (Exception e) { return 0.0; }
    }
}