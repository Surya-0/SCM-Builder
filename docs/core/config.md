# Configuration Settings

This document outlines the configuration settings used in the Supply Chain Management Builder.

## Business Structure

### Business Groups and Products
```python
BUSINESS_GROUP = 'Etch'
PRODUCT_FAMILIES = ['Kyo', 'Coronus', 'Flex', 'Versys Metal']
```

The system is configured with a hierarchical product structure:
- Business Group
- Product Families
- Product Offerings (detailed offerings for each family)

## Component Types

### Part Categories
- **Raw Materials**:
  - Metal sheets
  - Metal rods
  - Electronic components
  - Plastic components
  - Chemicals
  
- **Subassemblies**:
  - Circuit boards
  - Housing units
  - Control panels
  - Power units
  - Sensor arrays

## Node Features

Different node types have specific feature sets:
- Business Group Features: id, name, description, revenue
- Product Family Features: id, name, revenue
- Product Offering Features: id, name, cost, demand
- Facility Features: id, name, type, location, capacity, operating cost

## Temporal Configuration

- Base simulation period: 12 months
- Base date: January 1, 2024

### Temporal Variations
- Revenue: ±12% variation, 3% upward trend
- Cost: ±10% variation, 2% upward trend
- Demand: ±15% variation, 3% upward trend
- Capacity: ±8% variation, no trend
- Inventory: ±20% variation, no trend
- Reliability: ±5% variation, no trend
- Transportation Cost: ±8% variation, 1% upward trend

## Configuration

The configuration module manages system-wide settings and parameters. Key features include:

### Environment Configuration
- Server URL configuration
- API endpoint management
- Environment variable handling
- Development/Production mode settings

### Data Settings
- Export directory configuration
- File format settings
- Version control parameters
- Backup settings

### Network Parameters
- Node configuration
- Edge parameters
- Relationship settings
- Attribute definitions

### Simulation Settings
- Temporal parameters
- Cost calculation settings
- PO generation parameters
- Network evolution settings

### Integration Configuration
- API authentication
- Data transfer settings
- Error handling configuration
- Logging parameters

## Facility Configuration

### Warehouse Types
- Supplier warehouses
- Subassembly warehouses
- LAM warehouses

### Facility Types
- External facilities
- LAM facilities

### Locations
Facilities can be located in:
- California
- Texas
- Arizona
- Oregon
- New York
- Massachusetts
- Washington
- Florida
- Georgia

## Operational Parameters

### Inventory and Demand
- Inventory Range: 50-1000 units
- Demand Range: 10-200 units
- Cost Range: $100-$10,000
- Capacity Range: 1,000-10,000 units

### Transportation
- Cost Range: $10-$1,000
- Time Range: 1-30 days
- Distance Range: 10-1,000 miles

### Part Validity
- Validity Period: 12-36 months

## Minimum Node Requirements
- Suppliers: 20
- Warehouses: 3 each for supplier, subassembly, and LAM
- Facilities: 2 each for external and LAM
- Parts: 10 raw materials, 15 subassemblies
