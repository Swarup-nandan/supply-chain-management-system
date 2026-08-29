
package com.swarup.supplychain.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import com.swarup.supplychain.model.Shipment;
import com.swarup.supplychain.repository.ShipmentRepository;
import com.swarup.supplychain.service.RiskService;
import com.swarup.supplychain.service.MLClientService;

@RestController
@RequestMapping("/api/shipments")
@CrossOrigin(origins = "*")
public class ShipmentController {

    @Autowired
    private ShipmentRepository repository;

    @Autowired
    private RiskService riskService;

    @Autowired
    private MLClientService mlClient;

    @PostMapping
    public Shipment createShipment(@RequestBody Shipment shipment) {
        double risk = riskService.calculateRisk(shipment);
        shipment.setRiskScore(risk);
        repository.save(shipment);
        mlClient.callML(shipment.getDelayDays(),
                        shipment.getDemandSpikePercent(),
                        shipment.getWeatherSeverity());
        return shipment;
    }

    @GetMapping
    public List<Shipment> getAll() {
        return repository.findAll();
    }
}
