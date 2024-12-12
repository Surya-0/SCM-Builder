# Supply Chain Generation

The Generation module provides functionality for creating and managing supply chain networks.

## Features

### Network Generation
- Creates complete supply chain networks
- Generates nodes for all supply chain entities
- Establishes relationships between entities
- Manages warehouse-supplier-parts relationships

### Data Generation
- Creates synthetic but realistic supply chain data
- Supports temporal variations in data
- Maintains data consistency across the network
- Handles warehouse capacity allocation

### Version Control
- Tracks all changes to the network
- Maintains operation history
- Supports multiple versions of the network

## Generation Page

The Generation page is responsible for creating and managing supply chain network data. It provides the following key functionalities:

### Data Generation
- Creates supply chain network data using the `SupplyChainGenerator` class
- Allows configuration of network parameters through an intuitive interface
- Supports temporal data generation for time-series analysis
- Manages warehouse storage allocation and capacity

### Export Functionality
- Exports generated data to CSV files in the `exports` directory
- Creates separate exports for simulation and actual data
- Supports versioned data export with timestamps
- Includes export of Purchase Order (PO) demand and cost dictionaries
- Exports supplier-parts relationships

### Server Integration
- Provides functionality to export data to a remote server
- Supports both simulation and actual data transmission
- Uses secure API endpoints for data transfer
- Includes supplier-parts dictionary transmission

### Network Analysis
- Includes bottleneck analysis visualization
- Displays network metrics and KPIs
- Provides real-time feedback on network generation
- Visualizes warehouse capacity utilization
- Analyzes disaster impact on supply chain

### Simulation Features
- Disaster impact simulation
- Warehouse storage optimization
- LAM and Supplier warehouse analysis
- Cost impact visualization
- Capacity utilization tracking

### Session Management
- Maintains generator state across sessions
- Tracks current period for temporal analysis
- Handles data persistence and state management
- Manages warehouse allocation states

## Key Components

### Network Structure
- Business hierarchy
- Product relationships
- Supply chain connections
- Temporal relationships
- Warehouse-supplier mappings

### Data Types
- Node properties
- Edge properties
- Temporal variations
- Operational metrics
- Warehouse capacities
- Disaster impact metrics

### Export Options
- JSON format
- CSV format
- Network visualizations
- Warehouse allocation reports

## Usage

The generation module can be used through the streamlit interface:

1. Navigate to the Generation page
2. Configure network parameters:
   - Number of nodes
   - Time periods
   - Version identifier
3. Generate the network
4. View and export the generated data
5. Simulate disasters or warehouse storage scenarios
6. Analyze results through interactive visualizations

### Tabs Overview

1. **Generate Data**
   - Basic network generation
   - Parameter configuration
   - Initial data setup

2. **Simulation Control**
   - Temporal simulation management
   - Network evolution control
   - Data validation

3. **Supply Chain Simulator**
   - Network performance analysis
   - Bottleneck visualization
   - KPI tracking

4. **Simulate Disasters**
   - Disaster impact analysis
   - Cost change visualization
   - Network resilience testing

5. **Simulate Warehousing**
   - LAM warehouse analysis
   - Supplier warehouse analysis
   - Capacity optimization
   - Storage allocation visualization
