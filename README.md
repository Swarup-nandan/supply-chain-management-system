# 🌐 Supply Chain Early Warning System (SCWS)
An end-to-end intelligent **Supply Chain Risk Early Warning & Disruption Prediction System** designed to detect, assess, and alert supply chain managers to shipment delays and logistical bottlenecks before they cause operational failure.
---
## 📌 Overview
The **Supply Chain Early Warning System (SCWS)** monitors multi-tier logistics by fusing real-time operational data (delays, cargo values, temperature anomalies) with external risk vectors (geopolitical instability, extreme weather events, and carrier historical reliability). It leverages a machine learning engine alongside a Spring Boot enterprise core and a reactive dark-themed operations dashboard.
```
       ┌──────────────────┐
       │   React 18 UI    │  <─── Operations Center & Real-time Alerts
       │   (Port 3000)    │
       └────────┬─────────┘
                │ REST API
                ▼
       ┌──────────────────┐
       │   Spring Boot    │  <─── Business Logic, JPA Persistence & Alerting
       │   (Port 8080)    │
       └────┬────────┬────┘
            │        │ HTTP REST
            │        ▼
            │   ┌───────────────────┐
            │   │ ML Microservice   │  <─── Random Forest & Gradient Boosting
            │   │  Flask (Port 5000)│       (Weather, Geo, & Supplier Risk)
            │   └───────────────────┘
            ▼
 ┌──────────────────────┐
 │   PostgreSQL DB      │  <─── Shipment records, risk indices, alert logs
 │ (Docker - Port 5432) │
 └──────────────────────┘
```
---
## ⚡ Key Capabilities
- **Multi-Factor Risk Prediction**:
  - **Weather Risk Engine**: Evaluates weather severity (hurricanes, typhoons, blizzards, floods, ice, extreme temperatures) and route delays.
  - **Geopolitical Risk Engine**: Analyzes route origins and destinations against regional volatility indices.
  - **Supplier / Carrier Reliability Model**: Measures carrier on-time performance (FedEx, DHL, Maersk, Evergreen, MSC, etc.).
- **Automatic Alert Triaging**:
  - Classifies shipments into risk levels: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
  - Flags shipments triggering early warning thresholds (`HIGH` or `CRITICAL`) with contextual alert messages.
- **Enterprise Operations Console**:
  - High-contrast, dark-themed operations dashboard designed with `IBM Plex Mono`.
  - Real-time polling (15-second heartbeat) for dynamic alert notification.
  - Instant shipment creation and assessment pipeline.
---
## 🛠️ Technology Stack
| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Axios, CSS-in-JS, IBM Plex Typography |
| **Backend** | Java 17+, Spring Boot 3.x, Spring Data JPA, Hibernate, RestTemplate |
