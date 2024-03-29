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

def find_columns(column, columns):

    if column in columns:
        selected = column
    else:
        columns.append('')
        selected = ''

    # Let user select target.
    selected = st.selectbox(
        label = f"Which one is the {column} column?",
        options=columns,
        format_func=lambda x: 'Select an option' if x == '' else x,
        index=columns.index(selected),
        key=column
    )

    return selected


# Set oage config and CSS.
st.set_page_config(page_title='CSV→Gephi', page_icon='🎭')
st.markdown(info.css, unsafe_allow_html=True)
# Print title.
st.title("Make :green[Gephi] from :red[CSV]")

# Print tagline.
st.markdown(
    """*Upload your data as CSV to make it into a GraphML-file compatible 
    with Gephi and [Gephi Light](https://gephi.org/gephi-lite/).*"""
)

#try:
# Print explainer.
expl = st.expander(label="More info")
with expl:
    st.write(info.explainer)



# Ask for nodes file.
csv_nodes = st.file_uploader(
    label="Upload file with **nodes** (if you have one).", key="nodes", help=f'[Example]({info.node_example})'
)

# Ask for relations file.
csv_edges = st.file_uploader(label="Upload file with **edges/relations**.", key="relations", help=f'[Example]({info.relations_example})')

col1, col2 = st.columns([1,2])

# Chose separator
with col1:
    # Set standard separator.
    st.session_state["sep"] = ','

    # Ask for separator.
    separators = {'comma ( , )': ',', 'semicolon ( ; )': ';', 'tab ( \u21E5 )': '\t', 'pipe (|)': '|', 'space ( )': ' ', '':''}
    sep = st.radio(
        'Separator in your files:', 
        options=['comma ( , )', 'semicolon ( ; )', 'tab ( \u21E5 )', 'pipe (|)', 'space ( )', 'custom'], 
        help='What are the values in your files separated with?'
        )
    if sep == 'custom':
        sep = st.text_input('Custom delimiter:')
        separators[sep] = sep
    
    st.session_state["sep"] = separators[sep]

# Preview file
with col2: 
    preview = st.button('Preview file.')
    if preview:
        try:
            st.dataframe(pd.read_csv(csv_edges, sep=st.session_state["sep"]), use_container_width=True)
        except pd.errors.ParserError:
            st.markdown(':red[Have you selected a correct separator?]')


files_uploaded = st.button('Done', 'files_uploaded')

if files_uploaded or 'files_already_uploaded' in st.session_state:
    st.session_state['files_already_uploaded'] = True

    if csv_edges == None:
        st.markdown(':red[You need to upload a file with relations.]')
        st.stop()

    try:
        df = pd.read_csv(csv_edges, sep=st.session_state["sep"])
    except pd.errors.EmptyDataError:
        st.markdown(':red[Have you chosen the right kind of separator?]')
        st.stop()
        
    df.rename({'type': 'relation_type'}, inplace=True, axis=1) # 'type' can't be used as attribute.
    df.columns = [i.lower() for i in df.columns] # Remove capital letters from column names.

        
    # Find and store target column.
    target = find_columns('target', df.columns.tolist())

    # Find and store source column.
    source = find_columns('source', df.columns.tolist())
    
    # Remove source and target columns from list of options.
    columns = df.columns.tolist()
    columns.remove(st.session_state["target"])
    columns.remove(st.session_state["source"])
    
    if all([st.session_state["source"] != "", st.session_state["target"] != ""]):

        source = st.session_state["source"]
        target = st.session_state["target"]

        # Let the user chose what columns that should be included.
        chosen_columns = st.multiselect(
            label="Chose other columns to include.", options=columns, default=columns
        )

        if csv_nodes != None: # When a nodes file is uploaded.
            df_nodes = pd.read_csv(csv_nodes, sep=st.session_state["sep"])
            df_nodes.columns = [i.lower() for i in df_nodes.columns] # Remove capital letters from column names.


            st.session_state['label_column'] = find_columns('label', df_nodes.columns.tolist())
            
            if st.session_state['label_column'] != '':
                df_nodes.set_index(st.session_state['label_column'], inplace=True)

        else: # If no node file provided.
            nodes = list(set(df[source].tolist() + df[target].tolist()))
            df_nodes = pd.DataFrame(
                nodes, index=range(0, len(nodes)), columns=["labels"]
            )

            st.session_state['label_column'] = 'labels'
        
        if st.session_state['label_column'] != '' and df_nodes.index.name != st.session_state['label_column']:
            df_nodes.set_index(st.session_state['label_column'], inplace=True)
            

        # Make empty graph.
        G = nx.MultiDiGraph()
        # Add nodes.
        G = add_nodes(G, df_nodes)
        # Add edges.
        G = add_edges(
            G, df, source=source, target=target, chosen_columns=chosen_columns
        )

        # Turn the graph into a string.
        graph_text = "\n".join([line for line in nx.generate_graphml(G)])
        
        # Download graphml-file.
        graphml_file = "output.graphml"
        st.download_button(
            "Download grampml-file", graph_text, file_name=graphml_file
        )
        st.write('Import the file to Gephi/Gephi Light, or try [Gephisto](https://jacomyma.github.io/gephisto/) to get an idea of the network.')

# except:
#     st.markdown(':red[Something went wrong, please try again or [write to me](https://twitter.com/lasseedfast).]')