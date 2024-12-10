# Supply Chain Data Generator

The `SupplyChainGenerator` class is responsible for generating synthetic supply chain network data with temporal variations.

## Overview

The data generator creates a complex supply chain network that includes:
- Business Groups
- Product Families
- Product Offerings
- Facilities
- Warehouses
- Suppliers
- Parts and Materials

## Data Generator

The Data Generator module is responsible for creating synthetic supply chain data for simulation and analysis. Key features include:

### Data Generation
- Creates realistic supply chain network structures
- Generates temporal data for time-series analysis
- Supports both simulation and actual data generation
- Includes PO demand and cost calculations

### Export Capabilities
- CSV export functionality
- Simulation data export
- Temporal graph export
- Dictionary format export for PO data

### Network Generation
- Node and edge creation
- Relationship definition
- Attribute assignment
- Temporal evolution

### Simulation Support
- Temporal simulation graphs
- PO demand simulation
- Cost simulation
- Network evolution simulation

### Integration Features
- Server export support
- Version control
- Data validation
- Error handling

## Class Structure

### Initialization Parameters

- `total_variable_nodes`: Number of total variable nodes (default: 1000)
- `base_periods`: Number of time periods to simulate (default: 12)
- `version`: Version identifier for the generator (default: "NSS_V1")

### Key Components

1. **Graph Structure**
   - Uses NetworkX DiGraph for network representation
   - Maintains temporal graphs for different time periods
   - Supports simulation graphs for what-if scenarios

2. **Node Types**
   - Fixed nodes (Business Groups, Product Families, Product Offerings)
   - Variable nodes (Facilities, Warehouses, Suppliers, Parts)

3. **Operation Logging**
   - Tracks all create/update operations
   - Maintains version control
   - Timestamps all changes

## Key Methods

### Node Operations
- `_log_node_operation`: Records node creation and updates
- `_log_edge_operation`: Records edge creation and updates

### Simulation
- `simulate_next_period`: Generates data for the next time period
- Handles temporal variations in:
  - Revenue
  - Cost
  - Demand
  - Capacity
  - Inventory levels

### Data Management
- `return_operation`: Retrieves all logged operations
- `return_create_operations`: Gets creation operations
- `return_update_operations`: Gets update operations

## Usage Example

```python
# Initialize the generator
generator = SupplyChainGenerator(
    total_variable_nodes=1000,
    base_periods=12,
    version="NSS_V1"
)

# Generate initial network
generator.generate_network()

# Simulate next period
generator.simulate_next_period()

# Get operations log
operations = generator.return_operation()
```
