# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import graphviz


def graph_to_dot(graph, field_filter=lambda _: True):
    """Convert a list of Node roots to graphviz dot format

    :param graph: a graph with nodes and edges
    :param field_filter: field name -> bool function that returns True for
                         fields that need to be kept in the dot output
    :return: a dot formatted string
    """
    dot = graphviz.Digraph(node_attr={"shape": "plaintext"})
    graph.add_to_dot(dot, field_filter)
    return dot.source
