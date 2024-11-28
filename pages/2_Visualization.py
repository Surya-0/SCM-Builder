# pages/2_Visualization.py
import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import os

st.set_page_config(layout="wide")
st.title("Supply Chain Network Visualization")

# Node type configuration with darker, more visible colors
NODE_CONFIG = {
    "business_group": {
        "color": "#D62828",  # Deep red
        "display_name": "Business Group",
        "size_multiplier": 2.0,
    },
    "product_families": {
        "color": "#1B4965",  # Dark blue
        "display_name": "Product Family",
        "size_multiplier": 1.8,
    },
    "product_offerings": {
        "color": "#1D3557",  # Navy blue
        "display_name": "Product",
        "size_multiplier": 1.5,
    },
    "suppliers": {
        "color": "#2D6A4F",  # Forest green
        "display_name": "Supplier",
        "size_multiplier": 1.6,
    },
    "warehouses": {
        "color": "#774936",  # Dark brown
        "display_name": "Warehouse",
        "size_multiplier": 1.7,
    },
    "facilities": {
        "color": "#9B2226",  # Dark red
        "display_name": "Facility",
        "size_multiplier": 1.7,
    },
    "parts": {
        "color": "#354F52",  # Dark green-gray
        "display_name": "Part",
        "size_multiplier": 1.3,
    },
}

# Visualization settings with darker edge color
EDGE_COLOR = "#666666"  # Darker gray for edges
MIN_NODE_SIZE = 8
MAX_NODE_SIZE = 25

# Layout algorithms dictionary
layout_algorithms = {
    "layout_kamada_kawai": nx.kamada_kawai_layout,
    "layout_spring": nx.spring_layout,
    "layout_spectral": nx.spectral_layout,
    "layout_multipartite": lambda G: (
        nx.multipartite_layout(G)
        if hasattr(G, "graph") and "subset" in G.graph
        else nx.spring_layout(G)
    ),
}

if not os.path.exists("exports"):
    st.warning(
        "No data found. Please generate and save the data first in the Generation page."
    )
else:
    timestamps = sorted(os.listdir("exports"))
    selected_timestamp = st.selectbox("Select Timestamp", timestamps)

    # Visualization controls
    st.sidebar.header("Visualization Controls")

    # Node type filters
    st.sidebar.subheader("Node Types")
    selected_node_types = {}
    for node_type, config in NODE_CONFIG.items():
        selected_node_types[node_type] = st.sidebar.checkbox(
            config["display_name"], value=True
        )

    # Edge visibility
    show_edges = st.sidebar.checkbox("Show Edges", value=True)

    # Node size control
    size_scale = st.sidebar.slider(
        "Node Size Scale", min_value=0.5, max_value=2.0, value=1.0, step=0.1
    )

    try:
        # Load edges first with error handling
        edges_df = pd.read_csv(f"exports/{selected_timestamp}/edges.csv")
        valid_nodes = set(edges_df["source_id"].unique()) | set(
            edges_df["target_id"].unique()
        )

        # Load nodes with error handling
        nodes = []
        node_counts = {}

        for node_type in NODE_CONFIG.keys():
            if selected_node_types[node_type]:
                try:
                    df = pd.read_csv(f"exports/{selected_timestamp}/{node_type}.csv")
                    df = df[df["id"].isin(valid_nodes)]
                    df["node_type"] = node_type
                    nodes.append(df)
                    node_counts[node_type] = len(df)
                except Exception as e:
                    st.sidebar.warning(
                        f"Could not load {NODE_CONFIG[node_type]['display_name']} data"
                    )
                    continue

        if nodes:
            nodes_df = pd.concat(nodes, ignore_index=True)

            # Create network
            G = nx.DiGraph()

            # Add nodes with attributes

            for _, row in nodes_df.iterrows():
                # Convert row to dictionary and filter out NaN/null values
                node_attrs = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
                G.add_node(row["id"], **node_attrs)
            # Add edges if enabled
            if show_edges:
                valid_edges = edges_df[
                    edges_df["source_id"].isin(G.nodes())
                    & edges_df["target_id"].isin(G.nodes())
                ]
                G.add_edges_from(valid_edges[["source_id", "target_id"]].values)

            # Graph is ready here!

            # Layout algorithm selector
            layout_options = {
                "Kamada-Kawai": "layout_kamada_kawai",
                "Spring": "layout_spring",
                "Spectral": "layout_spectral",
                "Multipartite": "layout_multipartite",
            }

            layout_choice = st.selectbox(
                "Select Layout Algorithm", options=list(layout_options.keys())
            )

            # Calculate layout
            # pos = nx.spring_layout(G, k=1/np.sqrt(len(G.nodes())), iterations=50)
            layout_function = layout_algorithms.get(
                layout_options[layout_choice], nx.spring_layout
            )
            pos = layout_function(G)

            # Create edge trace if edges are enabled
            traces = []
            if show_edges:
                edge_x = []
                edge_y = []
                for edge in G.edges():
                    x0, y0 = pos[edge[0]]
                    x1, y1 = pos[edge[1]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])

                edge_trace = go.Scatter(
                    x=edge_x,
                    y=edge_y,
                    line=dict(width=0.5, color=EDGE_COLOR),
                    hoverinfo="none",
                    mode="lines",
                    name="Connections",
                    opacity=0.7,  # Increased opacity for better visibility
                )
                traces.append(edge_trace)

            # print(G.nodes(data=True))

            # Create node traces with improved hover information
            for node_type, config in NODE_CONFIG.items():
                if selected_node_types[node_type]:
                    node_x = []
                    node_y = []
                    node_text = []
                    node_size = []

                    for node in G.nodes():
                        if G.nodes[node]["node_type"] == node_type:
                            x, y = pos[node]
                            node_x.append(x)
                            node_y.append(y)

                            # Enhanced hover information
                            degree = G.degree(node)
                            in_degree = G.in_degree(node)
                            out_degree = G.out_degree(node)

                            # Initialize hover text
                            hover_text = f"<b>{config['display_name']}</b><br>"
                            hover_text += f"ID: {node}<br>"
                            hover_text += f"Connections: {degree}<br>"
                            hover_text += f"Incoming: {in_degree}<br>"
                            hover_text += f"Outgoing: {out_degree}"

                            # Add additional node attributes if they exist
                            # node_data = G.nodes[node]
                            # st.write(G.nodes[node])
                            for key, value in G.nodes[node].items():
                                if (
                                    key != "node_type"
                                ):  # Skip node_type as it's already shown
                                    hover_text += f"<br>{key}: {value}"

                            node_text.append(hover_text)

                            # Calculate node size based on degree and configuration
                            base_size = np.sqrt(degree + 1) * config["size_multiplier"]
                            scaled_size = base_size * size_scale
                            node_size.append(
                                np.clip(scaled_size, MIN_NODE_SIZE, MAX_NODE_SIZE)
                            )

                    if node_x:  # Only create trace if nodes exist for this type
                        node_trace = go.Scatter(
                            x=node_x,
                            y=node_y,
                            mode="markers",
                            name=f"<b>{config['display_name']}</b>",  # Bold text in legend
                            marker=dict(
                                size=20,
                                color=config["color"],
                                line=dict(width=1, color="white"),
                                opacity=0.9,  # Increased opacity
                            ),
                            text=node_text,
                            hoverinfo="text",
                            legendgroup=node_type,
                            showlegend=True,
                        )
                        traces.append(node_trace)

            # Create figure with improved layout and darker legend
            fig = go.Figure(
                data=traces,
                layout=go.Layout(
                    title=dict(
                        text="",
                        x=0.5,
                        y=0.95,
                        font=dict(size=20, color="black"),
                    ),
                    showlegend=True,
                    hovermode="closest",
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    height=800,
                    legend=dict(
                        title=dict(
                            text="<b>Network Components</br></br></b>",
                            font=dict(size=14, color="black"),
                        ),
                        font=dict(size=10, color="black"),
                        bgcolor="rgba(255, 255, 255, 0.9)",  # Semi-transparent white background
                        bordercolor="black",
                        borderwidth=1,  # Thicker border
                        itemsizing="constant",
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=1.02,
                        itemwidth=50,  # Wider legend items
                        itemclick=False,  # Prevent accidental clicking
                        itemdoubleclick=False,
                    ),
                    hoverlabel=dict(
                        bgcolor="white",
                        font=dict(size=12, color="black"),
                        bordercolor="black",
                    ),
                ),
            )

            # Display network statistics
            st.subheader("Network Statistics")
            stats_cols = st.columns(4)

            with stats_cols[0]:
                st.metric("Total Nodes", len(G.nodes()))

            with stats_cols[1]:
                st.metric("Total Edges", len(G.edges()))

            with stats_cols[2]:
                st.metric("Network Density", f"{nx.density(G):.3f}")

            with stats_cols[3]:
                avg_degree = sum(dict(G.degree()).values()) / len(G.nodes())
                st.metric("Average Degree", f"{avg_degree:.2f}")

            # Display node type distribution
            st.subheader("Node Distribution")
            dist_cols = st.columns(len(node_counts))
            for i, (node_type, count) in enumerate(node_counts.items()):
                with dist_cols[i]:
                    st.metric(NODE_CONFIG[node_type]["display_name"], count)
            st.write("---")
            # Display the network visualization
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("No node data found for the selected timestamp.")

    except Exception as e:
        st.error(f"Error loading or processing data: {str(e)}")
