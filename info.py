# URL to gist files.
node_example = 'https://gist.githubusercontent.com/lasseedfast/1d43f23da417d64c34d304048ff58b70/raw/64b68b32318b18cfb69a509f9285f6fd0cfc4af0/nodes_example.csv'
relations_example = 'https://gist.githubusercontent.com/lasseedfast/c8548d13202d434e6801c3eed70d0586/raw/71da6a4d5a2129c5a55b8a656d53d7dddebb7ae4/relations_example.csv'

# Make links grey/black.
css = """<style>
a:link {color: grey;}
a:visited {color: grey;}
a:hover {color: grey;}
</style>
"""

explainer = f"""
    If you upload only a file with relations the nodes will be created from that one and will only have a label.  
    You can also upload a separate file with nodes and more information about them. If so make sure the nodes correlate 
    to the source/target column in the relations file.  
    If you use *source*, *target* and *label* in your files the process here is almost automatic (see examples).  
    Examples for [relation file]({relations_example}) and [node file]({node_example}).  
    *No data is stored.* Made by [Lasse Edfast](https://lasseedfast.se). 
    """