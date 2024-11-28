# Home.py
import streamlit as st
import pandas as pd
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from data_generator import SupplyChainGenerator

st.set_page_config(
    page_title="Supply Chain Data Generator",
    page_icon="🏭",
    layout="wide"
)

st.title("Dynamic Supply Chain Data Generator")

st.markdown("""
## Welcome to the Supply Chain Data Generator!

This application allows you to generate, visualize, and analyze synthetic supply chain data with temporal variations. The generator creates a complete supply chain network including:

### Core Components
- **Business Groups**: Top-level organizational units
- **Product Families**: Groups of related products
- **Product Offerings**: Individual products available for sale
- **Suppliers**: Companies providing raw materials and components
- **Warehouses**: Storage facilities for different types of materials
- **Facilities**: Manufacturing and assembly locations
- **Parts**: Raw materials and subassemblies

### Key Features
1. **Dynamic Data Generation**: Create realistic supply chain networks with configurable parameters
2. **Temporal Analysis**: View how various metrics change over time
3. **Network Visualization**: Explore the relationships between different components
4. **Performance Analytics**: Analyze key metrics and identify patterns

### Getting Started
1. Go to the **Generation** page to create new supply chain data
2. Use the **Visualization** page to explore the generated network
3. Visit the **Analysis** page for detailed metrics and insights
4. Try the **Supply chain manager** page for adding new nodes into the graph

### Navigation
Use the sidebar to switch between different pages and functionalities.
""")
