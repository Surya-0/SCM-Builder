# config.py
from datetime import datetime, timedelta

BUSINESS_GROUP = 'Etch'

PRODUCT_FAMILIES = ['Kyo', 'Coronus', 'Flex', 'Versys Metal']

PRODUCT_OFFERINGS = {
    'Kyo': ['Versys® Kyo®', 'Versys® Kyo® C Series', 'Kyo® C Series', 'Kyo® E Series', 'Kyo® F Series', 'Kyo® G Series'],
    'Coronus': ['Coronus®', 'Coronus® HP', 'Coronus® DX'],
    'Flex': ['Exelan® Flex®', 'Exelan® Flex45™', 'Flex® D Series', 'Flex® E Series', 'Flex® F Series', 'Flex® G Series', 'Flex® H Series'],
    'Versys Metal': ['Versys® Metal', 'Versys® Metal45™', 'Versys® Metal L', 'Versys® Metal M', 'Versys® Metal N']
}

# Part types
PART_TYPES = {
    'raw': ['metal_sheet', 'metal_rod', 'electronic_component', 'plastic_component', 'chemical'],
    'subassembly': ['circuit_board', 'housing_unit', 'control_panel', 'power_unit', 'sensor_array']
}

# Node features
BUSINESS_GROUP_FEATURES = ['id', 'name', 'description', 'revenue']
PRODUCT_FAMILY_FEATURES = ['id', 'name', 'revenue']
PRODUCT_OFFERINGS_FEATURES = ['id', 'name', 'cost','demand']
FACILITY_FEATURES = ['id', 'name', 'type', 'location', 'max_capacity', 'operating_cost']
WAREHOUSE_FEATURES = ['id', 'name', 'type', 'location', 'max_capacity', 'current_capacity', 'safety_stock', 'max_parts']
SUPPLIER_FEATURES = ['id', 'name', 'location', 'reliability', 'size', 'supplied_part_types']
PART_FEATURES = ['id', 'name', 'type', 'subtype', 'cost', 'importance_factor', 'valid_from', 'valid_till','units_in_chain']
# Need to add units in chain to the part features

# Temporal configuration
TIME_PERIODS = 12  # number of months
BASE_DATE = datetime(2024, 1, 1)
TEMPORAL_VARIATION = {
    'revenue': {'max_change': 0.12, 'trend': 0.03},  # 12% max random variation, 3% upward trend
    'cost': {'max_change': 0.1, 'trend': 0.02},  # 10% max random variation, 2% upward trend
    'demand': {'max_change': 0.15, 'trend': 0.03},  # 15% max random variation, 3% upward trends
    'capacity': {'max_change': 0.005, 'trend': 0},  # .5% max random variation, no trend
    'inventory': {'max_change': 0.2, 'trend': 0},  # 20% max random variation, no trend
    'reliability': {'max_change': 0.05, 'trend': 0},  # 5% max random variation, no trend
    'transportation_cost': {'max_change': 0.08, 'trend': 0.01},  # 8% max random variation, 1% upward trend
    'quantity': {'max_change': 0.2, 'trend': 0.02, 'start_after': 3}  # Start variation after timestamp 3, with 2% trend
}

# Warehouse types
WAREHOUSE_TYPES = ['supplier', 'subassembly', 'lam']

# Facility types
FACILITY_TYPES = ['external', 'lam']

# Location pools for random generation
LOCATIONS = ['California', 'Texas', 'Arizona', 'Oregon', 'New York', 'Massachusetts','Washington','Florida', 'Georgia']

# Configuration for random value generation

INVENTORY_RANGE = (700, 1500)
SAFETY_STOCK_RANGE = (10, 50)
DEMAND_RANGE = (50, 300)
IMPORTANCE_FACTOR_RANGE = (0.1, 1.0)
COST_RANGE = (10, 200)
CAPACITY_RANGE = (1000, 3000)
RELIABILITY_RANGE = (0.6, 0.99)
SIZE_RANGE = (100, 1000)
QUANTITY_RANGE = (1, 5)
TRANSPORTATION_COST_RANGE = (10, 1000)
TRANSPORTATION_TIME_RANGE = (1, 30)  # in days
DISTANCE_RANGE = (10, 1000)  # in miles
UNITS_IN_CHAIN = (10,20) # units in chain
EXPIRY = (60,90) # Number of expiry days

# Part validity periods (in months)
PART_VALIDITY_RANGE = (12, 36)  # parts valid for 1-3 years

# Minimum number of nodes per type
MIN_SUPPLIERS = 20
MIN_WAREHOUSES = {'supplier': 3, 'subassembly': 3, 'lam': 3}
MIN_FACILITIES = {'external': 2, 'lam': 2}
MIN_PARTS = {'raw': 10, 'subassembly': 15}


# Edge features based on type
EDGE_FEATURES = {
    'supplier_warehouse': ['transportation_cost', 'lead_time'],
    'warehouse_parts': ['inventory_level', 'storage_cost'],
    'parts_facility': ['quantity', 'distance', 'transport_cost', 'lead_time'],
    'facility_parts': ['production_cost', 'lead_time', 'quantity'],
    'facility_product': ['product_cost', 'lead_time', 'quantity'],
    'warehouse_product': ['inventory_level', 'storage_cost'],
    'hierarchy': []
}


SUPPLIER_SIZES = {
    'small': {'range': (100, 300), 'max_connections': 2},
    'medium': {'range': (301, 600), 'max_connections': 4},
    'large': {'range': (601, 1000), 'max_connections': 6}
}

WAREHOUSE_SIZES = {
    "small": {"capacity": (10000, 15000), "max_parts": 5},
    "medium": {"capacity": (15001, 20000), "max_parts": 10},
    "large": {"capacity": (20001, 30000), "max_parts": 15}
}