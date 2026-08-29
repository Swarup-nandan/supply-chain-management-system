
package com.swarup.supplychain.model;

import jakarta.persistence.*;
import java.time.LocalDate;

@Entity
public class Shipment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String supplierName;
    private LocalDate expectedDate;
    private LocalDate actualDate;
    private int demandSpikePercent;
    private int weatherSeverity;
    private double riskScore;

    public int getDelayDays() {
        if (actualDate == null) return 0;
        return actualDate.compareTo(expectedDate);
    }

    // Getters and Setters omitted for brevity
}
