## Config Module Specification

# Overview

This folder contains default connection variables and schema parameters for the ingestion pipelines.

# Configuration Files

neo_config.py: Controls Neo4j database endpoint parameters:

URI: Bolt connection string (Default: bolt://localhost:7687)

USER: Database user (Default: neo4j)

PASSWORD: User password (Default: EnergyUp)

oep_config.py: Controls Open Energy Platform API parameters:

BASE_URL: OEP API endpoint (https://openenergyplatform.org/api/v0)

SCHEMA: Target schema partition (Default: model_draft; options: sandbox, public)

hkg_config.py: Holds Helmholtz Knowledge Graph download and validation configurations.

# Security Best Practices

Do not commit production credentials directly to these files. You can override defaults using environment variables or a local .env file where supported.