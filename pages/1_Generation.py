        
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
server_url = os.getenv("SERVER_URL", "http://localhost:8000")


def initialize_session_state():
    if 'generator' not in st.session_state:
        st.session_state.generator = None
    if 'current_period' not in st.session_state:
        st.session_state.current_period = 0


def export_data(generator, export_dir):
    try:
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        generator.export_to_csv(generator.temporal_graphs,export_dir)
        # generator.save_export_to_file()
        return True, f"Data successfully exported to {export_dir}"
    except Exception as e:
        return False, f"Error exporting data: {str(e)}"

def export_data_for_simulation(generator,export_dir):
    try:
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        generator.export_to_csv(generator.simulation_graphs,export_dir)
        return True, f"Data successfully exported to {export_dir}"

    except Exception as e:
        return False, f"Error exporting data"



def export_to_server(generator, url,version):
    try:
        # export_list = generator.return_operation()
        create_ops_dict = generator.return_create_operations()
        update_ops_dict = generator.return_update_operations()

        total_create_ops = sum(len(ops) for ops in create_ops_dict.values())
        total_update_ops = sum(len(ops) for ops in update_ops_dict.values())
        total_ops = total_create_ops + total_update_ops
        # print(create_ops_dict)
        # sorted_create_ops_dict = {k:create_ops_dict[k] for k in sorted(create_ops_dict.keys())}
        # sorted_update_ops_dict = {k:update_ops_dict[k] for k in sorted(update_ops_dict.keys())}

        # print(update_ops_dict)

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

        return True, "Data successfully exported to Server"
    except Exception as e:
        return False, f"Error exporting data: {str(e)}"


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
            max_value=36,
            value=12,
            step=1
        )
        version = st.text_input("Enter the version")

    # Main area tabs
    tab1, tab2,tab3 = st.tabs(["Generate Data", "Simulation Control","Supply - chain Simulator"])

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

                col3,col4 = st.columns(2)
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
                            success, message = export_to_server(st.session_state.generator, url,version)
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
            col1,col2 = st.columns(2)
            with col1:
                if st.button("Simulate the graph"):
                    st.session_state.generator.create_simulation()
                    st.success("✅ Simulation Done!")

            with col2:
                if st.session_state.generator is not None:
                    export_dir = st.text_input(
                        "Export Directory",
                        value="simulation_exports",
                        help="Specify the directory where the simulation files will be saved"
                    )
                    if st.button("Export simulation to CSV"):
                        success,message = export_data_for_simulation(st.session_state.generator,export_dir)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)




if __name__ == "__main__":
    main()

