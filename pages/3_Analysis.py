
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.title("Supply Chain Analysis")

if not os.path.exists("exports"):
    st.warning("No data found. Please generate and save the data first in the Generation page.")
else:
    # Load all temporal data
    timestamps = sorted(os.listdir("exports"))

    # Prepare data for temporal analysis
    temporal_data = {
        'revenue': [],
        'costs': [],
        'inventory': [],
        'reliability': []
    }

    for timestamp in timestamps:
        try:
            date = datetime.strptime(timestamp, '%Y%m%d')

            # Load business group revenue with error handling
            try:
                bg_df = pd.read_csv(
                    f"exports/{timestamp}/business_group.csv",
                    on_bad_lines='skip'  # Replace error_bad_lines with on_bad_lines
                )
                if not bg_df.empty:
                    temporal_data['revenue'].append({
                        'date': date,
                        'value': bg_df['revenue'].iloc[0],
                        'metric': 'Business Group Revenue'
                    })
            except Exception as e:
                st.warning(f"Error loading business group data for {timestamp}: {str(e)}")

            # Load product costs
            try:
                po_df = pd.read_csv(
                    f"exports/{timestamp}/product_offerings.csv",
                    on_bad_lines='skip'
                )
                if not po_df.empty:
                    temporal_data['costs'].append({
                        'date': date,
                        'value': po_df['cost'].mean(),
                        'metric': 'Average Product Cost'
                    })
            except Exception as e:
                st.warning(f"Error loading product offerings data for {timestamp}: {str(e)}")

            # Load warehouse inventory
            try:
                edges_df = pd.read_csv(
                    f"exports/{timestamp}/edges.csv",
                    on_bad_lines='skip'
                )
                inventory_edges = edges_df[edges_df['inventory_level'].notna()]
                if not inventory_edges.empty:
                    temporal_data['inventory'].append({
                        'date': date,
                        'value': inventory_edges['inventory_level'].mean(),
                        'metric': 'Average Inventory Level'
                    })
            except Exception as e:
                st.warning(f"Error loading edges data for {timestamp}: {str(e)}")

            # Load supplier reliability
            try:
                suppliers_df = pd.read_csv(
                    f"exports/{timestamp}/suppliers.csv",
                    on_bad_lines='skip'
                )
                if not suppliers_df.empty:
                    temporal_data['reliability'].append({
                        'date': date,
                        'value': suppliers_df['reliability'].mean(),
                        'metric': 'Average Supplier Reliability'
                    })
            except Exception as e:
                st.warning(f"Error loading suppliers data for {timestamp}: {str(e)}")

        except Exception as e:
            st.error(f"Error processing timestamp {timestamp}: {str(e)}")
            continue

    # Convert to DataFrames with error handling
    metrics_dfs = {}
    for metric, data in temporal_data.items():
        if data:  # Only create DataFrame if we have data
            metrics_dfs[metric] = pd.DataFrame(data)

    # Create visualizations
    st.subheader("Temporal Analysis")

    # Revenue trend
    if 'revenue' in metrics_dfs and not metrics_dfs['revenue'].empty:
        fig_revenue = px.line(
            metrics_dfs['revenue'],
            x='date',
            y='value',
            title='Business Group Revenue Over Time'
        )
        st.plotly_chart(fig_revenue)
    else:
        st.warning("No revenue data available for visualization")

    # Costs and inventory
    col1, col2 = st.columns(2)

    with col1:
        if 'costs' in metrics_dfs and not metrics_dfs['costs'].empty:
            fig_costs = px.line(
                metrics_dfs['costs'],
                x='date',
                y='value',
                title='Average Product Cost Over Time'
            )
            st.plotly_chart(fig_costs)
        else:
            st.warning("No cost data available for visualization")

    with col2:
        if 'inventory' in metrics_dfs and not metrics_dfs['inventory'].empty:
            fig_inventory = px.line(
                metrics_dfs['inventory'],
                x='date',
                y='value',
                title='Average Inventory Level Over Time'
            )
            st.plotly_chart(fig_inventory)
        else:
            st.warning("No inventory data available for visualization")

    # Supplier reliability
    if 'reliability' in metrics_dfs and not metrics_dfs['reliability'].empty:
        fig_reliability = px.line(
            metrics_dfs['reliability'],
            x='date',
            y='value',
            title='Average Supplier Reliability Over Time'
        )
        st.plotly_chart(fig_reliability)
    else:
        st.warning("No supplier reliability data available for visualization")

    # Additional analysis
    if timestamps:
        st.subheader("Latest Period Analysis")
        latest_timestamp = timestamps[-1]

        try:
            # Load latest data with error handling
            suppliers_df = pd.read_csv(
                f"exports/{latest_timestamp}/suppliers.csv",
                on_bad_lines='skip'
            )
            warehouses_df = pd.read_csv(
                f"exports/{latest_timestamp}/warehouses.csv",
                on_bad_lines='skip'
            )

            col1, col2 = st.columns(2)

            with col1:
                if not suppliers_df.empty and 'size_category' in suppliers_df.columns:
                    fig_supplier_dist = px.pie(
                        suppliers_df,
                        names='size_category',
                        title='Supplier Size Distribution'
                    )
                    st.plotly_chart(fig_supplier_dist)
                else:
                    st.warning("No supplier size data available")

            with col2:
                if not warehouses_df.empty and all(col in warehouses_df.columns for col in ['current_capacity', 'max_capacity', 'type']):
                    warehouses_df['utilization'] = (warehouses_df['current_capacity'] /
                                                  warehouses_df['max_capacity'] * 100)
                    fig_warehouse_util = px.bar(
                        warehouses_df,
                        x='id',
                        y='utilization',
                        color='type',
                        title='Warehouse Capacity Utilization (%)'
                    )
                    st.plotly_chart(fig_warehouse_util)
                else:
                    st.warning("No warehouse capacity data available")

        except Exception as e:
            st.error(f"Error loading latest period data: {str(e)}")
    else:
        st.warning("No data available for latest period analysis")
