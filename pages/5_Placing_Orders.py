import streamlit as st
from data_generator import SupplyChainGenerator
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict


def create_simulation_dashboard():
    st.title('🚚 Supply Chain Demand Simulator')
    st.session_state.simulate = False

    if 'generator' not in st.session_state or st.session_state.generator is None:
        st.warning("Please generate supply chain data first using the Generation page.")
        return

    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["📋 Input Demands", "📊 Simulation Results"])

    with tab1:
        st.header("Input Product Offering Demands")

        # Create a multiselect option to choose a product offering to update
        selected_offerings = st.multiselect(
            "Select Product Offerings to Update",
            options=[(offering['id'], offering['name']) for offering in
                     st.session_state.generator.product_offerings],
            format_func=lambda x: x[1]
        )

        # Set up default demands for product offerings not being updated
        demands = {}
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Enter Demands")
            for offering in st.session_state.generator.product_offerings:
                offering_id = offering['id']
                if (offering_id, offering['name']) in selected_offerings:
                    current_demand = st.session_state.generator.demand_po.get(offering_id, 0)
                    demands[offering_id] = st.number_input(
                        f"Enter demand for {offering['name']}",
                        min_value=0,
                        value=int(current_demand),
                        step=1,
                        key=f"demand_{offering_id}"
                    )
                else:
                    demands[offering_id] = st.session_state.generator.demand_po.get(offering_id, 0)

        with col2:
            st.subheader("Current Settings (Live Updates)")

            # Display the current demands dynamically
            current_demands = pd.DataFrame([
                {"Product": offering['name'],
                 "Current Demand": demands[offering['id']]
                 }
                for offering in st.session_state.generator.product_offerings
            ])
            st.dataframe(current_demands)

        # Button to trigger simulation
        if st.button("🔄 Run Simulation"):
            # Update demands and run simulation
            for offering_id, demand in demands.items():
                st.session_state.generator.demand_po[offering_id] = demand

            # Reset tracking dictionaries before running the simulation
            st.session_state.generator.demand_Lam_facility = defaultdict(int)
            st.session_state.generator.demand_sa = defaultdict(int)
            st.session_state.generator.demand_external_facility = defaultdict(int)
            st.session_state.generator.demand_rm = defaultdict(int)
            st.session_state.generator.cost_rm = defaultdict(float)
            st.session_state.generator.cost_external_facility_rm = defaultdict(float)
            st.session_state.generator.cost_sa_external_facility = defaultdict(float)
            st.session_state.generator.cost_LF = defaultdict(float)
            st.session_state.generator.cost_po = defaultdict(float)

            # Run the simulation
            st.session_state.generator.create_simulation()
            st.success("Simulation completed successfully!")
            st.session_state.simulate = True

    with tab2:
        if not st.session_state.simulate:
            st.info("Please run a simulation first to see results")
            return


        if hasattr(st.session_state.generator, 'simulation_graphs'):
            st.header("Simulation Results")

            # Display cost analysis
            st.subheader("Cost Analysis")
            cost_data = pd.DataFrame([
                {"Product": offering['name'],
                 "Demand": st.session_state.generator.demand_po[offering['id']],
                 "Total Cost": st.session_state.generator.cost_po[offering['id']],
                 "Cost per Unit": st.session_state.generator.cost_po[offering['id']] /
                                  st.session_state.generator.demand_po[offering['id']]
                 if st.session_state.generator.demand_po[offering['id']] > 0 else 0}
                for offering in st.session_state.generator.product_offerings
            ])
            st.dataframe(cost_data)

            # Create visualizations
            fig = px.bar(cost_data,
                         x="Product",
                         y=["Demand", "Total Cost"],
                         title="Demand vs Cost by Product",
                         barmode="group")
            st.plotly_chart(fig)

            # Display facility utilization
            st.subheader("Facility Utilization")
            lam_facility_data = pd.DataFrame([
                {"Facility": facility['name'],
                 "Demand": st.session_state.generator.demand_Lam_facility[facility['id']],
                 "Capacity": facility['max_capacity'],
                 "Utilization (%)": (st.session_state.generator.demand_Lam_facility[facility['id']] /
                                     facility['max_capacity'] * 100) if facility['max_capacity'] > 0 else 0}
                for facility in st.session_state.generator.facilities['lam']
            ])
            st.dataframe(lam_facility_data)


def main():
    create_simulation_dashboard()


if __name__ == '__main__':
    main()