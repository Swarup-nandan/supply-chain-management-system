
package com.swarup.supplychain.service;

import org.springframework.stereotype.Service;
import com.swarup.supplychain.model.Shipment;

@Service
public class RiskService {
    public double calculateRisk(Shipment s) {
        return (s.getDelayDays() * 0.4) +
               (s.getDemandSpikePercent() * 0.3) +
               (s.getWeatherSeverity() * 0.3);
    }
}
