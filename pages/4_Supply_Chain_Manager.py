
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from config import *


def initialize_manager_state():
    if 'bulk_update_type' not in st.session_state:
        st.session_state.bulk_update_type = 'suppliers'
    if 'update_preview' not in st.session_state:
        st.session_state.update_preview = None
    if 'editing_mode' not in st.session_state:
        st.session_state.editing_mode = 'bulk'  # 'bulk' or 'individual'

def get_size_from_category(category):
    size_ranges = {
        'small': (100, 300),
        'medium': (301, 600),
        'large': (601, 1000)
    }
    if category in size_ranges:
        return random.uniform(*size_ranges[category])
    return random.uniform(*size_ranges['small'])  # Default to small range

def get_size_category(size_value):
    if size_value <= 300:
        return 'small'
    elif size_value <= 700:
        return 'medium'
    else:
        return 'large'
def render_attribute_input(attr, value_type, key_prefix, index=None):
    key_suffix = f"_{index}" if index is not None else ""

    if attr == 'size_category':
        return st.selectbox(
            f"Select {attr}",
            options=['small', 'medium', 'large'],
            key=f"{key_prefix}_{attr}{key_suffix}"
        )
    elif isinstance(value_type, list):
        if isinstance(value_type[0], list):  # For nested lists like supplied_part_types
            return st.multiselect(
                f"Select {attr}",
                options=[item for sublist in value_type for item in sublist],
                key=f"{key_prefix}_{attr}{key_suffix}"
            )
        return st.selectbox(
            f"Select {attr}",
            options=value_type,
            key=f"{key_prefix}_{attr}{key_suffix}"
        )
    elif isinstance(value_type, tuple):
        col1, col2 = st.columns(2)
        with col1:
            min_val = st.number_input(
                f"Min {attr}",
                value=value_type[0],
                key=f"{key_prefix}_{attr}_min{key_suffix}"
            )
        with col2:
            max_val = st.number_input(
                f"Max {attr}",
                value=value_type[1],
                key=f"{key_prefix}_{attr}_max{key_suffix}"
            )
        return (min_val, max_val)
    return None


def get_attribute_template(update_type):
    templates = {
        'suppliers': {
            'id': 'S_{counter:03d}',
            'name': 'Supplier_{counter}',
            'location': ['California', 'Texas', 'Arizona', 'Oregon', 'New York', 'Massachusetts','Washington','Florida', 'Georgia'],
            'reliability': (0.7, 1.0),
            'size': (100, 1000),
            'size_category': ['small', 'medium', 'large'],
            'supplied_part_types': [['Electronics', 'Metals'], ['Plastics', 'Composites'], ['Raw Materials']]
        },
        'parts': {
            'id': 'P_{counter:03d}',
            'name': 'Part_{counter}',
            'type': ['raw', 'subassembly'],
            'subtype': ['Electronics', 'Metals', 'Plastics', 'Composites'],
            'cost': (100, 1000),
            'importance_factor': (0.1, 1.0)
        },
        'warehouses': {
            'id': 'W_{counter:03d}',
            'name': 'Warehouse_{counter}',
            'type': ['supplier', 'subassembly', 'lam'],
            'location': ['California', 'Texas', 'Arizona', 'Oregon', 'New York', 'Massachusetts','Washington','Florida', 'Georgia'],
            'size_category': ['small', 'medium', 'large'],
            'max_capacity': (1000, 10000),
            'current_capacity': 0,
            'safety_stock': (100, 1000)
        }
    }
    return templates.get(update_type, {})


def generate_random_values(attr, range_or_options, user_config=None):
    if user_config is not None and attr in user_config:
        if attr == 'size_category':
            return get_size_from_category(user_config[attr])
        if isinstance(range_or_options, tuple) and isinstance(user_config[attr], tuple):
            return random.uniform(*user_config[attr])
        return user_config[attr]

    if attr == 'size_category':
        category = random.choice(['small', 'medium', 'large'])
        return get_size_from_category(category)

    if isinstance(range_or_options, (list, tuple)):
        if isinstance(range_or_options[0], (int, float)):
            return random.uniform(*range_or_options)
        elif isinstance(range_or_options[0], list):  # For nested lists
            return random.choice([item for sublist in range_or_options for item in sublist])
        return random.choice(range_or_options)
    return range_or_options

def connect_new_nodes(generator, update_type, new_nodes):

    latest_period = max(generator.temporal_graphs.keys())
    current_graph = generator.temporal_graphs[latest_period]

    if update_type == 'suppliers':
        # Connect suppliers to appropriate warehouses based on size
        for _, supplier in new_nodes.iterrows():
            size_category = supplier['size_category']
            max_connections = SUPPLIER_SIZES[size_category]['max_connections']

            # Find appropriate warehouses based on supplied part types
            supplier_part_types = supplier['supplied_part_types']
            possible_warehouses = []

            if any(t in PART_TYPES['raw'] for t in supplier_part_types):
                possible_warehouses.extend(generator.warehouses['supplier'])
            if any(t in PART_TYPES['subassembly'] for t in supplier_part_types):
                possible_warehouses.extend(generator.warehouses['subassembly'])

            if possible_warehouses:
                num_connections = min(max_connections, len(possible_warehouses))
                selected_warehouses = random.sample(possible_warehouses, num_connections)

                for warehouse in selected_warehouses:
                    edge_data = {
                        'transportation_cost': random.uniform(*TRANSPORTATION_COST_RANGE),
                        'lead_time': random.uniform(*TRANSPORTATION_TIME_RANGE)
                    }
                    current_graph.add_edge(supplier['id'], warehouse['id'], **edge_data)

    elif update_type == 'parts':
        # Connect parts to appropriate warehouses and facilities
        for _, part in new_nodes.iterrows():
            if part['type'] == 'raw':
                # Connect to supplier warehouses
                possible_warehouses = generator.warehouses['supplier']
                for warehouse in possible_warehouses:
                    if warehouse['current_capacity'] < warehouse['max_capacity']:
                        inventory_level = min(
                            random.randint(*INVENTORY_RANGE),
                            warehouse['max_capacity'] - warehouse['current_capacity']
                        )
                        edge_data = {
                            'inventory_level': inventory_level,
                            'storage_cost': random.uniform(*COST_RANGE)
                        }
                        current_graph.add_edge(warehouse['id'], part['id'], **edge_data)
                        warehouse['current_capacity'] += inventory_level

                # Connect to external facilities
                for facility in generator.facilities['external']:
                    if random.random() < 0.3:  # 30% chance to connect
                        edge_data = {
                            'quantity': random.randint(*QUANTITY_RANGE),
                            'distance': random.randint(*DISTANCE_RANGE),
                            'transport_cost': random.uniform(*TRANSPORTATION_COST_RANGE),
                            'lead_time': random.uniform(*TRANSPORTATION_TIME_RANGE)
                        }
                        current_graph.add_edge(part['id'], facility['id'], **edge_data)

            elif part['type'] == 'subassembly':
                # Connect to subassembly warehouses
                possible_warehouses = generator.warehouses['subassembly']
                for warehouse in possible_warehouses:
                    if warehouse['current_capacity'] < warehouse['max_capacity']:
                        inventory_level = min(
                            random.randint(*INVENTORY_RANGE),
                            warehouse['max_capacity'] - warehouse['current_capacity']
                        )
                        edge_data = {
                            'inventory_level': inventory_level,
                            'storage_cost': random.uniform(*COST_RANGE)
                        }
                        current_graph.add_edge(warehouse['id'], part['id'], **edge_data)
                        warehouse['current_capacity'] += inventory_level

                # Connect to LAM facilities
                for facility in generator.facilities['lam']:
                    if random.random() < 0.3:  # 30% chance to connect
                        edge_data = {
                            'quantity': random.randint(*QUANTITY_RANGE),
                            'distance': random.randint(*DISTANCE_RANGE),
                            'transport_cost': random.uniform(*TRANSPORTATION_COST_RANGE),
                            'lead_time': random.uniform(*TRANSPORTATION_TIME_RANGE)
                        }
                        current_graph.add_edge(part['id'], facility['id'], **edge_data)

    elif update_type == 'warehouses':
        # Connect warehouses to appropriate suppliers and parts
        for _, warehouse in new_nodes.iterrows():
            if warehouse['type'] == 'supplier':
                # Connect to suppliers
                for supplier in generator.suppliers:
                    if random.random() < 0.2:  # 20% chance to connect
                        edge_data = {
                            'transportation_cost': random.uniform(*TRANSPORTATION_COST_RANGE),
                            'lead_time': random.uniform(*TRANSPORTATION_TIME_RANGE)
                        }
                        current_graph.add_edge(supplier['id'], warehouse['id'], **edge_data)

                # Connect to raw parts
                max_parts = warehouse['max_parts']
                selected_parts = random.sample(
                    generator.parts['raw'],
                    min(max_parts, len(generator.parts['raw']))
                )
                for part in selected_parts:
                    inventory_level = random.randint(*INVENTORY_RANGE)
                    edge_data = {
                        'inventory_level': inventory_level,
                        'storage_cost': random.uniform(*COST_RANGE)
                    }
                    current_graph.add_edge(warehouse['id'], part['id'], **edge_data)

            elif warehouse['type'] in ['subassembly', 'lam']:
                # Connect to appropriate parts or products based on type
                part_pool = (generator.parts['subassembly'] if warehouse['type'] == 'subassembly'
                             else generator.product_offerings)
                max_items = warehouse['max_parts']
                selected_items = random.sample(
                    part_pool,
                    min(max_items, len(part_pool))
                )
                for item in selected_items:
                    inventory_level = random.randint(*INVENTORY_RANGE)
                    edge_data = {
                        'inventory_level': inventory_level,
                        'storage_cost': random.uniform(*COST_RANGE)
                    }
                    current_graph.add_edge(warehouse['id'], item['id'], **edge_data)
    # Update the temporal graph
    generator.temporal_graphs[latest_period] = current_graph


def get_current_node_count(generator, node_type):
    if node_type == 'suppliers':
        return len(generator.suppliers)
    elif node_type == 'parts':
        return sum(len(parts) for parts in generator.parts.values())
    elif node_type == 'warehouses':
        return sum(len(warehouses) for warehouses in generator.warehouses.values())
    return 0


def create_bulk_update_preview(update_type, num_items, attributes, generator, user_config=None):
    template = get_attribute_template(update_type)
    preview_data = []
    current_count = get_current_node_count(generator, update_type)

    for i in range(num_items):
        item = {}
        for attr, value in template.items():
            if attr in attributes:
                if attr == 'id':
                    prefix = value.split('_')[0]
                    item[attr] = f"{prefix}_{current_count + i + 1:03d}"
                elif attr == 'name':
                    item[attr] = f"{update_type[:-1].capitalize()}_{current_count + i + 1}"
                elif attr == 'size_category':
                    # If size_category is specified in user_config, use it
                    if user_config and 'size_category' in user_config:
                        if isinstance(user_config['size_category'], dict):
                            item[attr] = user_config['size_category'][str(i)]
                        else:
                            item[attr] = user_config['size_category']
                    else:
                        item[attr] = random.choice(['small', 'medium', 'large'])

                    # Generate corresponding size value
                    item['size'] = get_size_from_category(item[attr])
                elif attr == 'size':
                    # Skip size as it's handled with size_category
                    continue
                else:
                    # Handle individual configurations
                    if user_config and isinstance(user_config.get(attr), dict) and str(i) in user_config[attr]:
                        config_value = user_config[attr][str(i)]
                        if isinstance(config_value, tuple):
                            item[attr] = random.uniform(*config_value)
                        else:
                            item[attr] = config_value
                    else:
                        item[attr] = generate_random_values(attr, value, user_config)

        preview_data.append(item)

    return pd.DataFrame(preview_data)


def edit_individual_records(num_items, template, update_type):
    individual_config = {}

    for attr, value_type in template.items():
        if attr not in ['id', 'name']:  # Skip ID and name as they're auto-generated
            st.subheader(f"Configure {attr}")
            individual_config[attr] = {}

            cols = st.columns(min(3, num_items))  # Create up to 3 columns
            for i in range(num_items):
                with cols[i % 3]:
                    st.write(f"Record {i + 1}")
                    user_input = render_attribute_input(attr, value_type, f"{update_type}_{i}", i)
                    if user_input is not None:
                        individual_config[attr][str(i)] = user_input

    return individual_config


def apply_bulk_update(generator, update_type, preview_data):
    if generator is None:
        return False, "No generator instance found. Please generate supply chain data first."

    try:
        # Get the latest time period
        latest_period = max(generator.temporal_graphs.keys())
        current_graph = generator.temporal_graphs[latest_period]

        if update_type == 'suppliers':
            for _, row in preview_data.iterrows():
                supplier_data = row.to_dict()
                supplier_id = supplier_data['id']
                current_graph.add_node(supplier_id, **supplier_data, node_type='supplier')
                generator.suppliers.append(supplier_data)

        elif update_type == 'parts':
            for _, row in preview_data.iterrows():
                part_data = row.to_dict()
                part_id = part_data['id']
                current_graph.add_node(part_id, **part_data, node_type='part')
                generator.parts[part_data['type']].append(part_data)

        elif update_type == 'warehouses':
            for _, row in preview_data.iterrows():
                warehouse_data = row.to_dict()
                warehouse_id = warehouse_data['id']
                current_graph.add_node(warehouse_id, **warehouse_data, node_type='warehouse')
                generator.warehouses[warehouse_data['type']].append(warehouse_data)
        
        st.write("Before adding new nodes")
        connect_new_nodes(generator, update_type, preview_data)
        st.write("After adding new nodes")

        # Update the temporal graph for the latest period
        generator.temporal_graphs[latest_period] = current_graph
        return True, f"Successfully added {len(preview_data)} new {update_type}"

    except Exception as e:
        return False, f"Error applying updates: {str(e)}"

def main():
    st.title("Supply Chain Manager")
    initialize_manager_state()

    if 'generator' not in st.session_state or st.session_state.generator is None:
        st.warning("Please generate supply chain data first using the Generation page.")
        return

    with st.sidebar:
        st.header("Bulk Update Configuration")
        update_type = st.selectbox(
            "Select Update Type",
            ['suppliers', 'parts', 'warehouses'],
            key='bulk_update_type'
        )

        num_items = st.number_input(
            "Number of Items to Add",
            min_value=1,
            max_value=100,
            value=5
        )

        editing_mode = st.radio(
            "Editing Mode",
            options=['bulk', 'individual'],
            format_func=lambda x: 'Bulk Edit' if x == 'bulk' else 'Individual Edit',
            key='editing_mode'
        )

    st.subheader(f"Bulk Add {update_type.title()}")
    st.write("Latest timestamp:", max(st.session_state.generator.temporal_graphs.keys()))

    # Get template for selected update type
    template = get_attribute_template(update_type)
    selected_attributes = []
    user_config = {}

    # Create an expander for attribute selection
    with st.expander("Select Attributes", expanded=True):
        st.write("Select attributes to include:")
        cols = st.columns(3)
        for i, (attr, _) in enumerate(template.items()):
            with cols[i % 3]:
                if st.checkbox(f"Include {attr}", value=True):
                    selected_attributes.append(attr)

    # Configure attributes based on editing mode
    if selected_attributes:
        if editing_mode == 'bulk':  # Changed from st.session_state.editing_mode
            with st.expander("Configure Bulk Values", expanded=True):
                for attr, values in template.items():
                    if attr in selected_attributes and attr not in ['id', 'name']:
                        st.subheader(f"Configure {attr}")
                        user_input = render_attribute_input(attr, values, update_type)
                        if user_input is not None:
                            user_config[attr] = user_input
        else:  # Individual Edit
            with st.expander("Configure Individual Values", expanded=True):
                user_config = edit_individual_records(num_items,
                                                   {k: v for k, v in template.items() if k in selected_attributes},
                                                   update_type)

    # Generate preview button
    if st.button("Generate Preview"):
        with st.spinner("Generating preview..."):
            preview_df = create_bulk_update_preview(
                update_type,
                num_items,
                selected_attributes,
                st.session_state.generator,
                user_config
            )
            st.session_state.update_preview = preview_df

    # Show preview if available
    if st.session_state.update_preview is not None:
        st.subheader("Preview")
        st.dataframe(st.session_state.update_preview)

        if st.button("Apply Updates"):
            with st.spinner("Applying updates..."):
                success, message = apply_bulk_update(
                    st.session_state.generator,
                    update_type,
                    st.session_state.update_preview
                )
                if success:
                    st.success(message)
                    st.session_state.update_preview = None
                else:
                    st.error(message)

if __name__ == "__main__":
    main()
    