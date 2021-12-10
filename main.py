import pydotplus
import os
import yaml
import webbrowser

from pyvis.network import Network
import graph_utils as graph_utils
import streamlit as st
import streamlit.components.v1 as components

__this_dir__ = os.path.join(os.path.abspath(os.path.dirname(__file__)))
graph_configuration = yaml.load(open(os.path.join(__this_dir__, "graph_config.yaml")), Loader=yaml.SafeLoader)
type_configuration = yaml.load(open(os.path.join(__this_dir__, "type_label_values_dict.yaml")), Loader=yaml.SafeLoader)

# -- Set page config
apptitle = 'Graph Quickview'

st.set_page_config(page_title=apptitle, page_icon=":eyeglasses:", layout="wide")
st.title('Graph Quick-Look')


def stream_graph():
    dot_fn = 'graph_data/graph.dot'
    html_fn = 'graph_data/graph.html'

    pydot_graph = pydotplus.graph_from_dot_file(dot_fn)
    net = Network(
        height='750px', width='100%',
    )

    for node in pydot_graph.get_nodes():
        id_node = graph_utils.get_id_node(node)
        if id_node is not None:
            type_node = type_configuration[id_node]
            node_configuration = graph_configuration.get(type_node,
                                                         graph_configuration['Default'])
            node_value = node_configuration.get('value', graph_configuration['Default']['value'])
            hidden = False
            if type_node.startswith('CommandOutput') or type_node.startswith('CommandInput'):
                hidden = True
            net.add_node(node.get_name(),
                         label=type_node,
                         color=node_configuration['color'],
                         shape=node_configuration['shape'],
                         value=node_value,
                         hidden=hidden)

    # list of edges and simple color change
    for edge in pydot_graph.get_edge_list():
        edge_label = graph_utils.get_edge_label(edge)
        source_node = edge.get_source()
        dest_node = edge.get_destination()
        hidden = False
        node_id = (source_node + '_' + dest_node)
        if edge_label.startswith('isInputOf') or edge_label.startswith('hasOutputs'):
            hidden = True
        if source_node is not None and dest_node is not None:
            net.add_edge(source_node, dest_node,
                         id=node_id,
                         title=edge_label,
                         hidden=hidden)

    # to tweak physics related options
    # net.show_buttons(filter_=['physics'])
    net.write_html(html_fn)

    graph_utils.add_js_click_functionality(net, html_fn)

    # webbrowser.open('graph_data/graph.html')
    st.components.v1.html(open(html_fn).read(), width=1200, height=800)
    st.markdown("***")


if __name__ == '__main__':
    stream_graph()

