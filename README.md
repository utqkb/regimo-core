# regimo-core
The foundational library and base abstractions for the Regimo Energy Data Orchestrator. Provides the internal engine for ontology-aware Kafka communication.

## Overview
The `regimo-core` repository contains the fundamental abstractions and internal libraries for **Regimo**, the microservice-based Energy Data Orchestrator developed at the **Karlsruhe Institute of Technology (KIT)**. It provides the "scaffolding" required for any functional socket to participate in the orchestrator's event-driven architecture.

## Core Responsibilities
As the engine of the ecosystem (referencing **KITopen-ID: 1000168804**), this repository manages:

* **Bus Orchestration:** Shared logic for Kafka producer/consumer patterns, ensuring consistent message delivery and robust error handling.
* **Semantic Middleware:** Internal tools for parsing the `regimo-ontology` and mapping it to runtime objects.
* **Socket Templates:** Base classes and interfaces that define how an "ontology-aware socket" should behave, significantly reducing boilerplate for new microservices.
* **Telemetry & Logging:** Standardised monitoring for energy data streams to ensure system health and data lineage.



## Repository Contents
* `lib/`: The core Python/Java libraries used as dependencies by all Regimo sockets.
* `interfaces/`: Definitions for the Kafka message headers and metadata required for ontology awareness.
* `utils/`: Common utilities for timestamp synchronisation, unit conversion (e.g., $kW$ to $MW$), and data validation.

## Usage
`regimo-core` is the primary dependency for all `socket-*` repositories. It is designed to be imported as a library or utilised as a base Docker image to ensure that every component in the Energy Data Orchestrator follows the same communication protocols.