        
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import requests
from data_generator import SupplyChainGenerator
import time
import plotly.express as px
from datetime import datetime

load_dotenv()
server_url = os.getenv("SERVER_URL", "http://172.17.149.238/api")
# server_url = "https://antelope-worthy-glowworm.ngrok-free.app/api"
# server_url = "http://192.168.0.106:8000/api"


st.set_page_config(layout="wide")


def initialize_session_state():
    if 'generator' not in st.session_state:
        st.session_state.generator = None
    if 'current_period' not in st.session_state:
        st.session_state.current_period = 0


def export_data(generator, export_dir):
    try:
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        generator.export_to_csv(generator.temporal_graphs, export_dir)
        # generator.save_export_to_file()
        return True, f"Data successfully exported to {export_dir}"
    except Exception as e:
        return False, f"Error exporting data: {str(e)}"


def export_data_for_simulation(generator, export_dir):
    try:
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        generator.export_to_csv(generator.temporal_simulation_graphs, export_dir)
        return True, f"Data successfully exported to {export_dir}"

    except Exception as e:
        return False, f"Error exporting data"


def export_dictionaries(generator, url, version):
    [temporal_po_demand, temporal_po_cost] = generator.return_simulation_dictionaries_po()
    [temporal_sa_demand, temporal_sa_cost] = generator.return_simulation_dictionaries_sa()
    [temporal_rm_demand, temporal_rm_cost] = generator.return_simulation_dictionaries_rm()
    supplier_parts = generator.return_suppliers_parts

    for timestamp, po_demand in temporal_po_demand.items():
        payload_po = {
            "version": version,
            "timestamp": timestamp,
            "type": "PRODUCT_OFFERING_DEMAND",
            "dict": po_demand
        }

        requests.post(f"{url}/dicts", json=payload_po)
        # time.sleep(1)

    for timestamp, po_cost in temporal_po_cost.items():
        payload_po = {
            "version": version,
            "timestamp": timestamp,
            "type": "PRODUCT_OFFERING_COST",
            "dict": po_cost
        }

        requests.post(f"{url}/dicts", json=payload_po)
        # time.sleep(1)

    for timestamp, sa_demand in temporal_sa_demand.items():
        payload_sa = {
            "version": version,
            "timestamp": timestamp,
            "type": "SUB_ASSEMBLIES_DEMAND",
            "dict": sa_demand
        }

        requests.post(f"{url}/dicts", json=payload_sa)
        # time.sleep(1)

    for timestamp, sa_cost in temporal_sa_cost.items():
        payload_sa = {
            "version": version,
            "timestamp": timestamp,
            "type": "SUB_ASSEMBLIES_COST",
            "dict": sa_cost
        }

        requests.post(f"{url}/dicts", json=payload_sa)
        # time.sleep(1)

    for timestamp, rm_demand in temporal_rm_demand.items():
        payload_rm = {
            "version": version,
            "timestamp": timestamp,
            "type": "RAW_MATERIALS_DEMAND",
            "dict": rm_demand
        }

        requests.post(f"{url}/dicts", json=payload_rm)
        # time.sleep(1)

    for timestamp, rm_cost in temporal_rm_cost.items():
        payload_rm = {
            "version": version,
            "timestamp": timestamp,
            "type": "RAW_MATERIALS_COST",
            "dict": rm_cost
        }

        requests.post(f"{url}/dicts", json=payload_rm)

        # time.sleep(1)

    payload_sup_parts = {
        "version": version,
        "timestamp": 0,
        "type" : "SUPPLIERS_PARTS",
        "dict" : supplier_parts
    }

    requests.post(f"{url}/dicts", json=payload_sup_parts)


def export_to_server(generator, url, version, simulation=False):
    try:
        st.write(version)
        # export_list = generator.return_operation()
        if not simulation:
            create_ops_dict = generator.return_create_operations()
            update_ops_dict = generator.return_update_operations()

        else:
            create_ops_dict = generator.return_simulate_create_operations()
            update_ops_dict = generator.return_simulate_update_operations()

        total_create_ops = sum(len(ops) for ops in create_ops_dict.values())
        total_update_ops = sum(len(ops) for ops in update_ops_dict.values())
        total_ops = total_create_ops + total_update_ops
        # print(create_ops_dict)
        # sorted_create_ops_dict = {k:create_ops_dict[k] for k in sorted(create_ops_dict.keys())}
        # sorted_update_ops_dict = {k:update_ops_dict[k] for k in sorted(update_ops_dict.keys())}

        # print(update_ops_dict)

        st.write(f"Total operations : {total_ops}")

        progress = st.progress(0)
        current_progress = 0

        for key, list_ops in create_ops_dict.items():
            for i in range(0, len(list_ops), 1000):
                bulk_create_payload = {
                    "version": version,
                    "action": "bulk_create",
                    "type": "schema",
                    "timestamp": key,
                    "payload": []
                }
                for op in list_ops[i:i + 1000]:
                    bulk_create_payload['payload'].append(op['payload'])
                requests.post(f"{url}/schema/live/update", json=bulk_create_payload)
                time.sleep(1)

                current_progress += len(list_ops[i:i + 1000])
                progress.progress(current_progress / total_ops)

            # st.write(f"Timestamp {key} has been sent to the server for creation")

        for key, list_ops in update_ops_dict.items():
            for i in range(0, len(list_ops), 1000):
                bulk_update_payload = {
                    "version": version,
                    "action": "bulk_update",
                    "type": "schema",
                    "timestamp": key,
                    "payload": []
                }
                for op in list_ops[i:i + 1000]:
                    bulk_update_payload['payload'].append(op['payload'])
                requests.post(f"{url}/schema/live/update", json=bulk_update_payload)
                time.sleep(1)

                current_progress += len(list_ops[i:i + 1000])
                progress.progress(current_progress / total_ops)

            # st.write(f"Timestamp {key} has been sent to the server for updating")

        if simulation:
            export_dictionaries(generator, url, version)

        return True, "Data successfully exported to Server"


    except Exception as e:
        return False, f"Error exporting data: {str(e)}"

def display_bottleneck_analysis(generator):
    if not hasattr(generator, 'bottleneck_details_sa') or not hasattr(generator, 'bottleneck_details_po'):
        st.warning("No bottleneck analysis data available. Please run the simulation first.")
        return

    st.subheader("Bottleneck Analysis")

    # Create tabs for different views
    tab1, tab2 = st.tabs(["Product Offering Bottlenecks", "Sub-Assembly Bottlenecks"])

    with tab1:
        # Prepare data for product offering bottlenecks
        po_data = []
        for timestamp, bottlenecks in generator.bottleneck_details_po.items():
            for product_id, details in bottlenecks.items():
                po_data.append({
                    'Timestamp': details['timestamp'],
                    'Product ID': product_id,
                    'Demand': details['demand'],
                    'Max Capacity': details['max_capacity_lam_facs'],
                    'Bottleneck Factor': details['bottleneck_factor'],
                    'Capacity Ratio': details['demand'] / details['max_capacity_lam_facs']
                })

        if po_data:
            df_po = pd.DataFrame(po_data)
            df_po["Factored Max Capacity"] = df_po["Max Capacity"] * df_po["Bottleneck Factor"]
            # st.subheader("Product Offering Bottleneck Analysis")
            # st.write(df_po)

            col1, col2 = st.columns(2)
            with col1:
                # Create capacity utilization chart
                fig3 = px.line(df_po, x='Timestamp', y='Capacity Ratio',
                               color='Product ID', title='Product Offering Capacity Utilization Over Time')
                st.plotly_chart(fig3, use_container_width=True)

            # Aggregate data across timestamps (using mean)
            df_po_agg = df_po.groupby('Product ID').agg({
                'Demand': 'mean',
                'Factored Max Capacity': 'mean'
            }).reset_index()

            with col2:
                # Create demand vs capacity comparison with aggregated data
                fig4 = px.bar(df_po_agg, x='Product ID', y=['Demand', 'Factored Max Capacity'],
                              barmode='group', title='Average Demand vs Capacity by Product',
                              labels={'value': 'Units', 'variable': 'Metric'})
                st.plotly_chart(fig4, use_container_width=True)

            # # Show critical bottlenecks
            # critical_po = df_po[df_po['Capacity Ratio'] > 0.8].sort_values('Capacity Ratio', ascending=False)
            # if not critical_po.empty:
            #     st.warning("Critical Bottlenecks (>80% Capacity Utilization)")
            #     st.dataframe(critical_po)

    with tab2:
        # Prepare data for sub-assembly bottlenecks
        sa_data = []
        for timestamp, bottlenecks in generator.bottleneck_details_sa.items():
            for part_id, details in bottlenecks.items():
                sa_data.append({
                    'Timestamp': details['timestamp'],
                    'Part ID': part_id,
                    'Demand': details['demand'],
                    'Max Capacity': details['max_capacity_ext_facs'],
                    'Bottleneck Factor': details['bottleneck_factor'],
                    'Capacity Ratio': details['demand'] / details['max_capacity_ext_facs']
                })


        if sa_data:
            df_sa = pd.DataFrame(sa_data)
            df_sa["Factored Max Capacity"] = df_sa["Max Capacity"] * df_sa["Bottleneck Factor"]
            # st.subheader("Sub-Assembly Bottleneck Analysis")
            # st.write(df_sa)

            col1, col2 = st.columns(2)
            with col1:
                # Create capacity utilization chart
                fig1 = px.line(df_sa, x='Timestamp', y='Capacity Ratio',
                               color='Part ID', title='Sub-Assembly Capacity Utilization Over Time')
                st.plotly_chart(fig1, use_container_width=True)

            # Aggregate data across timestamps (using mean)
            df_sa_agg = df_sa.groupby('Part ID').agg({
                'Demand': 'mean',
                'Factored Max Capacity': 'mean'
            }).reset_index()

            with col2:
                # Create demand vs capacity comparison with aggregated data
                fig2 = px.bar(df_sa_agg, x='Part ID', y=['Demand', 'Factored Max Capacity'],
                              barmode='group', title='Average Demand vs Capacity by Sub-Assembly',
                              labels={'value': 'Units', 'variable': 'Metric'})
                st.plotly_chart(fig2, use_container_width=True)


def analyze_disaster_impact(generator, disaster_results):
    """Analyze and visualize the impact of a disaster on the supply chain"""
    st.subheader("🌋 Disaster Impact Analysis")

    # Create tabs for different analysis views
    cost_tab, demand_tab, capacity_tab = st.tabs([
        "💰 Cost Propagation",
        "📈 Demand & Bottlenecks",
        "🏭 Capacity Analysis"
    ])

    pre_disaster_ts = disaster_results['timestamp'] - 1
    post_disaster_ts = disaster_results['timestamp']

    with cost_tab:
        st.markdown("### Cost Propagation Analysis")

        # Compare product offering costs before and after disaster
        pre_costs = disaster_results['pre_disaster_cost_po']
        post_costs = generator.cost_po

        cost_changes = []
        for po_id in pre_costs:
            if po_id in post_costs:
                pct_change = ((post_costs[po_id] - pre_costs[po_id]) / pre_costs[po_id]) * 100
                cost_changes.append({
                    'Product ID': po_id,
                    'Pre-Disaster Cost': pre_costs[po_id],
                    'Post-Disaster Cost': post_costs[po_id],
                    'Change (%)': pct_change
                })

        cost_df = pd.DataFrame(cost_changes)
        if not cost_df.empty:
            # Cost propagation visualization
            fig = px.scatter(cost_df,
                             x='Pre-Disaster Cost',
                             y='Post-Disaster Cost',
                             color='Change (%)',
                             size=abs(cost_df['Change (%)']),
                             hover_data=['Product ID'],
                             title='Cost Propagation in Product Offerings',
                             color_continuous_scale='RdYlBu_r')
            fig.add_shape(type='line',
                          x0=cost_df['Pre-Disaster Cost'].min(),
                          y0=cost_df['Pre-Disaster Cost'].min(),
                          x1=cost_df['Pre-Disaster Cost'].max(),
                          y1=cost_df['Pre-Disaster Cost'].max(),
                          line=dict(color='gray', dash='dash'))
            st.plotly_chart(fig, use_container_width=True)

            # Cost impact distribution
            fig2 = px.histogram(cost_df,
                                x='Change (%)',
                                title='Distribution of Cost Changes',
                                color_discrete_sequence=['#ff7f0e'])
            st.plotly_chart(fig2, use_container_width=True)

            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Cost Impact",
                          f"{cost_df['Change (%)'].mean():.1f}%")
            with col2:
                st.metric("Most Affected Product",
                          f"Product {cost_df.loc[cost_df['Change (%)'].idxmax(), 'Product ID']}",
                          f"{cost_df['Change (%)'].max():.1f}%")
            with col3:
                st.metric("Products Affected",
                          f"{len(cost_df[cost_df['Change (%)'] > 0])}")

    with demand_tab:
        st.markdown("### Demand and Bottleneck Analysis")

        # Analyze bottlenecks in product offerings
        po_bottlenecks = generator.bottleneck_details_po.get(post_disaster_ts, {})
        st.markdown("#### Product Offering Bottlenecks")
        if not po_bottlenecks:
            st.success("✅ No bottlenecks detected in any product offerings! All capacity requirements are being met.")
        else:
            po_bottleneck_data = []
            for po_id, details in po_bottlenecks.items():
                demand = float(details['demand'])
                max_capacity = float(details['max_capacity_lam_facs'])
                bottleneck_factor = float(details['bottleneck_factor'])
                capacity_ratio = demand / max_capacity

                po_bottleneck_data.append({
                    'Product ID': po_id,
                    'Demand': demand,
                    'Available Capacity': max_capacity,
                    'Capacity Ratio': capacity_ratio,
                    'Severity': capacity_ratio / bottleneck_factor,
                    'Bottleneck Factor': bottleneck_factor
                })

            if po_bottleneck_data:
                po_df = pd.DataFrame(po_bottleneck_data)

                # Bottleneck visualization
                fig = px.scatter(po_df,
                                 x='Demand',
                                 y='Available Capacity',
                                 size='Severity',
                                 color='Capacity Ratio',
                                 hover_data=['Product ID', 'Bottleneck Factor'],
                                 title='Product Offering Bottleneck Analysis',
                                 labels={
                                     'Capacity Ratio': 'Demand/Capacity Ratio',
                                     'Demand': 'Product Demand',
                                     'Available Capacity': 'Maximum Production Capacity'
                                 },
                                 color_continuous_scale='RdYlBu_r')

                # Add reference line for balanced demand/capacity
                max_val = max(po_df['Demand'].max(), po_df['Available Capacity'].max())
                fig.add_shape(
                    type='line',
                    x0=0, y0=0,
                    x1=max_val, y1=max_val,
                    line=dict(color='gray', dash='dash')
                )
                fig.update_layout(
                    annotations=[{
                        'text': 'Balanced Line (Demand = Capacity)',
                        'x': max_val / 2,
                        'y': max_val / 2,
                        'showarrow': False,
                        'font': {'size': 10},
                        'textangle': 45
                    }]
                )

                st.plotly_chart(fig, use_container_width=True)

                # Add summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    critical_bottlenecks = len(po_df[po_df['Capacity Ratio'] > 1.0])
                    st.metric(
                        "Critical Bottlenecks",
                        critical_bottlenecks,
                        help="Products where demand exceeds capacity"
                    )
                with col2:
                    avg_utilization = po_df['Capacity Ratio'].mean() * 100
                    st.metric(
                        "Avg Capacity Utilization",
                        f"{avg_utilization:.1f}%"
                    )
                with col3:
                    max_ratio = po_df['Capacity Ratio'].max()
                    st.metric(
                        "Max Utilization",
                        f"{max_ratio * 100:.1f}%"
                    )
            else:
                st.info("No bottlenecks detected in product offerings")

        # Analyze bottlenecks in sub-assemblies
        sa_bottlenecks = generator.bottleneck_details_sa.get(post_disaster_ts, {})
        if sa_bottlenecks:
            st.markdown("#### Sub-Assembly Bottlenecks")
            sa_bottleneck_data = []
            for sa_id, details in sa_bottlenecks.items():
                demand = float(details['demand'])
                max_capacity = float(details['max_capacity_ext_facs'])
                bottleneck_factor = float(details['bottleneck_factor'])
                capacity_ratio = demand / max_capacity

                sa_bottleneck_data.append({
                    'Sub-Assembly ID': sa_id,
                    'Demand': demand,
                    'Available Capacity': max_capacity,
                    'Capacity Ratio': capacity_ratio,
                    'Severity': capacity_ratio / bottleneck_factor,
                    'Bottleneck Factor': bottleneck_factor
                })

            if sa_bottleneck_data:
                sa_df = pd.DataFrame(sa_bottleneck_data)

                # Sub-assembly bottleneck visualization
                fig = px.scatter(sa_df,
                                 x='Demand',
                                 y='Available Capacity',
                                 size='Severity',
                                 color='Capacity Ratio',
                                 hover_data=['Sub-Assembly ID', 'Bottleneck Factor'],
                                 title='Sub-Assembly Bottleneck Analysis',
                                 labels={
                                     'Capacity Ratio': 'Demand/Capacity Ratio',
                                     'Demand': 'Required Demand',
                                     'Available Capacity': 'Maximum Production Capacity'
                                 },
                                 color_continuous_scale='RdYlBu_r')

                # Add reference line for balanced demand/capacity
                max_val = max(sa_df['Demand'].max(), sa_df['Available Capacity'].max())
                fig.add_shape(
                    type='line',
                    x0=0, y0=0,
                    x1=max_val, y1=max_val,
                    line=dict(color='gray', dash='dash')
                )
                fig.update_layout(
                    annotations=[{
                        'text': 'Balanced Line (Demand = Capacity)',
                        'x': max_val / 2,
                        'y': max_val / 2,
                        'showarrow': False,
                        'font': {'size': 10},
                        'textangle': 45
                    }]
                )

                st.plotly_chart(fig, use_container_width=True)

                # Add summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    critical_bottlenecks = len(sa_df[sa_df['Capacity Ratio'] > 1.0])
                    st.metric(
                        "Critical Bottlenecks",
                        critical_bottlenecks,
                        help="Sub-assemblies where demand exceeds capacity"
                    )
                with col2:
                    avg_utilization = sa_df['Capacity Ratio'].mean() * 100
                    st.metric(
                        "Avg Capacity Utilization",
                        f"{avg_utilization:.1f}%"
                    )
                with col3:
                    max_ratio = sa_df['Capacity Ratio'].max()
                    st.metric(
                        "Max Utilization",
                        f"{max_ratio * 100:.1f}%"
                    )
            else:
                st.info("No bottlenecks detected in sub-assemblies")

    with capacity_tab:
        st.markdown("### Facility Capacity Analysis")

        # Analyze facility capacities and their impact
        capacity_changes = []
        for facility in generator.facilities['external'] + generator.facilities['lam']:
            facility_id = facility['id']
            pre_cap = generator.temporal_simulation_graphs[pre_disaster_ts].nodes[facility_id].get('max_capacity', 0)
            post_cap = generator.temporal_simulation_graphs[post_disaster_ts].nodes[facility_id].get('max_capacity', 0)

            if pre_cap > 0:
                pct_change = ((post_cap - pre_cap) / pre_cap) * 100
                capacity_changes.append({
                    'Facility ID': facility_id,
                    'Type': 'External' if facility in generator.facilities['external'] else 'LAM',
                    'Pre-Disaster Capacity': pre_cap,
                    'Post-Disaster Capacity': post_cap,
                    'Change (%)': pct_change,
                    'Absolute Change': post_cap - pre_cap
                })

        capacity_df = pd.DataFrame(capacity_changes)
        if not capacity_df.empty:
            # Capacity change visualization
            fig = px.scatter(capacity_df,
                             x='Pre-Disaster Capacity',
                             y='Post-Disaster Capacity',
                             color='Type',
                             size=abs(capacity_df['Change (%)']),
                             hover_data=['Facility ID', 'Change (%)'],
                             title='Facility Capacity Changes')

            # Add reference line
            fig.add_shape(type='line',
                          x0=capacity_df['Pre-Disaster Capacity'].min(),
                          y0=capacity_df['Pre-Disaster Capacity'].min(),
                          x1=capacity_df['Pre-Disaster Capacity'].max(),
                          y1=capacity_df['Pre-Disaster Capacity'].max(),
                          line=dict(color='gray', dash='dash'))

            st.plotly_chart(fig, use_container_width=True)

            # Capacity change distribution by facility type
            fig2 = px.box(capacity_df,
                          x='Type',
                          y='Change (%)',
                          title='Distribution of Capacity Changes by Facility Type',
                          points='all',
                          color='Type')
            st.plotly_chart(fig2, use_container_width=True)

            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Capacity Impact",
                          f"{capacity_df['Change (%)'].mean():.1f}%")
            with col2:
                st.metric("Most Affected Facility",
                          f"Facility {capacity_df.loc[capacity_df['Change (%)'].idxmin(), 'Facility ID']}",
                          f"{capacity_df['Change (%)'].min():.1f}%")
            with col3:
                st.metric("Facilities Affected",
                          f"{len(capacity_df[capacity_df['Change (%)'] < 0])}")


def simulate_disaster_section():
    """Add disaster simulation section to the Streamlit app"""
    st.header("🌋 Supply Chain Disaster Simulation")

    col1, col2 = st.columns([2, 1])

    with col1:
        disaster_type = st.selectbox(
            "Select Disaster Type",
            ["cost", "demand", "capacity"],
            format_func=lambda x: {
                "cost": "💰 Raw Material Cost Increase",
                "demand": "📈 Product Demand Surge",
                "capacity": "🏭 Facility Capacity Reduction"
            }[x]
        )

        impact_description = {
            "cost": "Increase in raw material costs due to supply shortages or market disruptions",
            "demand": "Sudden surge in product demand due to market changes or emergency situations",
            "capacity": "Reduction in facility capacity due to disruptions or resource constraints"
        }

        st.info(impact_description[disaster_type])

    with col2:
        impact_factor = st.slider(
            "Impact Factor",
            min_value=1.1,
            max_value=5.0,
            value=2.0,
            step=0.1,
            help="Multiplier for costs/demand or divisor for capacity"
        )

        affected_percentage = st.slider(
            "Affected Nodes (%)",
            min_value=0.1,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Percentage of nodes affected by the disaster"
        )

    if st.button("🚀 Simulate Disaster", type="primary"):
        if 'generator' in st.session_state and st.session_state.generator:
            with st.spinner("Simulating disaster impact..."):
                # Run the disaster simulation
                disaster_results = st.session_state.generator.simulate_disaster(
                    disaster_type=disaster_type,
                    impact_factor=impact_factor,
                    affected_nodes_percentage=affected_percentage
                )

                # Analyze and visualize the results
                analyze_disaster_impact(st.session_state.generator, disaster_results)
        else:
            st.error("Please generate the supply chain data first!")

def main():
    st.title("Supply Chain Data Generation and Simulation")
    url = server_url
    initialize_session_state()

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        total_nodes = st.number_input(
            "Total Variable Nodes",
            min_value=30,
            max_value=100000,
            value=1000,
            step=200
        )
        base_periods = st.number_input(
            "Base Time Periods",
            min_value=1,
            max_value=108,
            value=12,
            step=1
        )
        version = st.text_input("Enter the version")

    # Main area tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Generate Data", "Simulation Control", "Supply - chain Simulator", "Simulate Disasters"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate New Supply Chain"):
                with st.spinner("Generating supply chain data..."):
                    st.session_state.generator = SupplyChainGenerator(
                        total_variable_nodes=total_nodes,
                        base_periods=base_periods,
                        version=version
                    )
                    st.session_state.generator.generate_data()
                    st.success("✅ Initial data generation complete!")

        with col2:
            if st.session_state.generator is not None:
                export_dir = st.text_input(
                    "Export Directory",
                    value="exports",
                    help="Specify the directory where CSV files will be saved"
                )

                col3, col4 = st.columns(2)
                with col3:
                    if st.button("Export to CSV"):
                        with st.spinner("Exporting data to CSV..."):
                            success, message = export_data(st.session_state.generator, export_dir)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)

                with col4:

                    if st.button("Export to server"):
                        with st.spinner("Exporting data to Server..."):
                            success, message = export_to_server(st.session_state.generator, url, version)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)

    with tab2:
        if st.session_state.generator is not None:
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Regenerate All Periods"):
                    st.session_state.generator.regenerate_all_periods()
                    st.success("✅ Data regenerated!")

            with col2:
                additional_periods = st.number_input(
                    "Number of Additional Periods",
                    min_value=1,
                    max_value=12,
                    value=1
                )
                if st.button("Simulate Additional Periods"):
                    new_periods = st.session_state.generator.simulate_multiple_periods(
                        additional_periods)
                    st.success(f"✅ Generated {len(new_periods)} new periods!")

            # Export section for simulation tab
            st.subheader("Export Simulation Data")
            col3, col4 = st.columns(2)

            with col3:
                export_dir = st.text_input(
                    "Export Directory (Simulation)",
                    value=f"exports",
                    help="Specify the directory where simulation CSV files will be saved"
                )

            with col4:
                if st.button("Export Simulation to CSV"):
                    with st.spinner("Exporting simulation data to CSV..."):
                        success, message = export_data(st.session_state.generator, export_dir)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)


        else:
            st.info("Please generate initial supply chain data first.")

    with tab3:

        col1, col2 = st.columns(2)
        with col1:
            Sim_button = st.button("Simulate the graph")
            if Sim_button:
                if not st.session_state.generator:
                    st.session_state.generator = SupplyChainGenerator(
                        total_variable_nodes=total_nodes,
                        base_periods=base_periods,
                        version=version
                    )

                st.session_state.generator.create_temporal_simulation()
                st.success("✅ Simulation Done!")


        with col2:
            col3, col4 = st.columns(2)
            with col3:
                if st.session_state.generator is not None:
                    export_dir = st.text_input(
                        "Export Directory",
                        value="simulation_exports",
                        help="Specify the directory where the simulation files will be saved"
                    )
                    if st.button("Export simulation to CSV"):
                        success, message = export_data_for_simulation(st.session_state.generator, export_dir)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

            with col4:
                if st.session_state.generator is not None:
                    if st.button("Export to Server"):
                        with st.spinner("Exporting data to Server..."):
                            success, message = export_to_server(st.session_state.generator, url, version, True)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)


        if Sim_button:
            # Add bottleneck visualization
            display_bottleneck_analysis(st.session_state.generator)

    with tab4:
        simulate_disaster_section()

if __name__ == "__main__":
    main()

