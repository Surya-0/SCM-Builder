# Supply Chain Analysis

The Analysis module provides tools for analyzing supply chain networks and their performance.

## Features

### Network Analysis
- Topology analysis
- Centrality metrics
- Path analysis
- Community detection

### Performance Analysis
- Efficiency metrics
- Cost analysis
- Time series analysis
- Bottleneck detection

### Risk Analysis
- Vulnerability assessment
- Impact analysis
- Scenario modeling
- Risk metrics

## Components

### Metrics
- Network metrics
- Performance indicators
- Risk scores
- Temporal trends

### Analysis Tools
- Statistical analysis
- Trend detection
- Anomaly detection
- Comparative analysis

### Reporting
- Automated insights
- Custom reports
- Visualization export
- Data export

## Analysis Page

The Analysis page provides comprehensive tools for analyzing supply chain network data. It includes:

### Temporal Analysis
- Tracks key metrics over time:
  - Business Group Revenue
  - Product Costs
  - Inventory Levels
  - Supply Chain Reliability
- Visualizes trends using interactive Plotly charts
- Supports date-based filtering and comparison

### Data Loading
- Automatically loads data from the `exports` directory
- Handles multiple temporal snapshots
- Provides robust error handling for data loading
- Supports various CSV formats and configurations

### Metrics Visualization
- Interactive line charts for trend analysis
- Multi-metric comparison capabilities
- Dynamic date range selection
- Customizable visualization options

### Error Handling
- Graceful handling of missing data
- Warning messages for data loading issues
- Skip functionality for corrupted lines in CSV files
- Comprehensive error reporting

## Usage

The analysis module can be accessed through the streamlit interface:

1. Navigate to the Analysis page
2. Select analysis type:
   - Network analysis
   - Performance analysis
   - Risk analysis
3. Configure analysis parameters
4. View results
5. Export findings
