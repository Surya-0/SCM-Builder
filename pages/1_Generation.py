        
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
# server_url = os.getenv("SERVER_URL", "http://localhost:8000")
server_url = "https://antelope-worthy-glowworm.ngrok-free.app/api"
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
    tab1, tab2, tab3 = st.tabs(["Generate Data", "Simulation Control", "Supply - chain Simulator"])

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


if __name__ == "__main__":
    main()

