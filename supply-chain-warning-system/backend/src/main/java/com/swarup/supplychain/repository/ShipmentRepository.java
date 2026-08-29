
package com.swarup.supplychain.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.swarup.supplychain.model.Shipment;

public interface ShipmentRepository extends JpaRepository<Shipment, Long> {}
