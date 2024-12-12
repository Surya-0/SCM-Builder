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
- Maintains warehouse-supplier-parts relationships

### Export Capabilities
- CSV export functionality
- Simulation data export
- Temporal graph export
- Dictionary format export for PO data
- Suppliers-parts mapping export

### Network Generation
- Node and edge creation
- Relationship definition
- Attribute assignment
- Temporal evolution
- Warehouse capacity management

### Simulation Support
- Temporal simulation graphs
- PO demand simulation
- Cost simulation
- Network evolution simulation
- Warehouse storage simulation
- Disaster impact simulation

### Integration Features
- Server export support
- Version control
- Data validation
- Error handling
- Supplier-parts relationship tracking

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

4. **Relationship Tracking**
   - Warehouses-parts mapping
   - Suppliers-warehouses mapping
   - Suppliers-parts derived mapping
   - Warehouse capacity management

## Key Methods

### Node Operations
- `_log_node_operation`: Records node creation and updates
- `_log_edge_operation`: Records edge creation and updates
- `return_suppliers_parts`: Returns the mapping of suppliers to their parts

### Simulation
- `simulate_next_period`: Generates data for the next time period
- `simulate_disaster`: Simulates impact of disasters on the network
- `simulate_po_warehouse_storage`: Simulates warehouse storage for product offerings
- `simulate_raw_warehouse_storage`: Simulates warehouse storage for raw materials
- Handles temporal variations in:
  - Revenue
  - Cost
  - Demand
  - Capacity
  - Inventory levels
  - Warehouse storage

### Data Management
- `return_operation`: Retrieves all logged operations
- `return_create_operations`: Gets creation operations
- `return_update_operations`: Gets update operations
- `return_simulation_dictionaries_po`: Returns PO simulation dictionaries
- `return_simulation_dictionaries_sa`: Returns SA simulation dictionaries
- `return_simulation_dictionaries_rm`: Returns RM simulation dictionaries

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

# Simulate warehouse storage
warehouse_po = generator.simulate_po_warehouse_storage()
warehouse_rm = generator.simulate_raw_warehouse_storage()

# Get operations log
operations = generator.return_operation()
