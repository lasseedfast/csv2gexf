import networkx as nx
import pandas as pd
import streamlit as st

import info

def add_edges(G, df, source, target, chosen_columns):
    # Iterate over each row in the DataFrame and add an edge to the graph.
    attrs = {}
    for key, row in df.iterrows():
        # Add edge with key.
        G.add_edge(row[source], row[target], key)

        # Set attributes for edge.
        d_attrs = {}
        for column in chosen_columns:
            try:
                d_attrs[column] = int(row[column])
            except ValueError:
                d_attrs[column] = row[column]
        attrs[(row[source], row[target], key)] = d_attrs


    # Add the attributes to the edges.
    nx.set_edge_attributes(G, attrs)

    return G


def add_nodes(G, df):
    """Add nodes to the graph."""
    d = df.to_dict(orient="index")
    nodes = [(k, v) for k, v in d.items()]
    G.add_nodes_from(nodes)
    return G

# Set oage config and CSS.
st.set_page_config(page_title='CSV→GEXF', page_icon='🎭')
st.markdown(info.css, unsafe_allow_html=True)
# Print title.
st.title("Make :green[GEXF] from :red[CSV]")

# Print tagline.
st.markdown(
    """*Upload your data as CSV to make it into a gexf-file compatible 
    with Gephi and [Gephi Light](https://gephi.org/gephi-lite/).*"""
)

# Print explainer.
expl = st.expander(label="More info")
with expl:
    st.write(info.explainer)

with st.form("files"):
    # Ask for nodes file.
    csv_nodes = st.file_uploader(
        label="Upload file with **nodes** (if you have one).", key="nodes", help=f'[Example]({info.node_example})'
    )

    # Ask for relations file.
    csv_edges = st.file_uploader(label="Upload file with **relations**.", key="relations", help=f'[Example]({info.relations_example})')

    sep = st.radio('Separator in your files:', options=['comma ( , )', 'semicolon ( ; )', 'tab ( \u21E5 )'], help='What are the values in your files separated with?')

    files_uploaded = st.form_submit_button("Done")

if files_uploaded:
    separators = {'comma ( , )': ',', 'semicolon ( ; )': ';', 'tab ( \u21E5 )': '\t'}
    if 'sep' not in st.session_state:
        st.session_state["sep"] =  separators[sep]

    if csv_edges == None:
        st.markdown(':red[You need to upload a file with relations.]')
        st.stop()

    df = pd.read_csv(csv_edges, sep=st.session_state["sep"])

    df.rename({'type': 'relation_type'}, inplace=True, axis=1) # 'type' can't be used as attribute.
    df.columns = [i.lower() for i in df.columns] # Remove capital letters from column names.
    columns = df.columns.tolist()

    # Find and store target column.
    if "target" not in st.session_state:
        if "target" in columns:
            preselected_target = "target"
        else:
            columns.append("")
            preselected_target = len(columns) - 1

        st.session_state["target"] = st.selectbox(
            label="Which one is the target column?",
            options=columns,
            index=columns.index(preselected_target),
        )

    # Find and store source column.
    if "source" not in st.session_state:
        if "source" in columns:
            preselected_source = "source"
        else:
            columns.append("")
            preselected_source = len(columns) - 1
        
        st.session_state["source"] = st.selectbox(
            label="Which one is the source column?",
            options=columns,
            index=columns.index(preselected_source),
        )

    # Remove source and target columns from list of options.
    columns.remove(st.session_state["target"])
    columns.remove(st.session_state["source"])

    if all([st.session_state["source"] != "", st.session_state["target"] != ""]):
        source = st.session_state["source"]
        target = st.session_state["target"]
        chosen_columns = st.multiselect(
            label="Chose other columns to include.", options=columns, default=columns
        )

        if csv_nodes != None: # When a nodes file is uploaded.
            df_nodes = pd.read_csv(csv_nodes, sep=st.session_state["sep"])
            df_nodes.columns = [i.lower() for i in df_nodes.columns] # Remove capital letters from column names.
            columns = df_nodes.columns.tolist()
            if "label" in columns:
                preselected_label = "label"
            else:
                columns.append("")
                preselected_label = len(columns) - 1
            label_column = st.selectbox(
                label="Which one is the label column in the nodes file?",
                options=columns,
                index=columns.index(preselected_label),
            )
            df_nodes.set_index(label_column, inplace=True)

        else: # If no node file provided.
            nodes = list(set(df[source].tolist() + df[target].tolist()))
            df_nodes = pd.DataFrame(
                nodes, index=range(0, len(nodes)), columns=["labels"]
            )
            df_nodes.set_index("labels", inplace=True)


        # Make empty graph.
        G = nx.MultiDiGraph()
        # Add nodes.
        G = add_nodes(G, df_nodes)
        # Add edges.
        G = add_edges(
            G, df, source=source, target=target, chosen_columns=chosen_columns
        )

        # Turn the graph into a string.
        graph_text = "\n".join([line for line in nx.generate_gexf(G)])
        
        # Download gexf-file.
        gexf_file = "output.gexf"
        st.download_button(
            "Download gexf-file", graph_text, file_name=gexf_file
        )
