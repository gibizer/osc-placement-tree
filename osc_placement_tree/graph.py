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
from osc_placement_tree import html


class Node(object):
    """The wrapper for a node"""

    def __init__(self, data):
        """Create a Node

        :param data: the object at the current node
        """
        self.data = data

    def add_to_dot(self, dot, field_filter):
        raise NotImplemented()

    def id(self):
        raise NotImplemented()


class RpNode(Node):
    def add_to_dot(self, dot, field_filter):
        dot.node(
            self.id(),
            html._get_attr_html(self.data, field_filter))

    def id(self):
        return self.data['uuid']


class Edge(object):
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2

    def add_to_dot(self, dot):
        raise NotImplemented()

    def __eq__(self, other):
        if other and isinstance(other, Edge):
            return self.node1 == other.node1 and self.node2 == other.node2
        else:
            return False


class ParentEdge(Edge):
    """A child -> parent edge

    node1 should be the child
    node2 should be the parent
    """
    def add_to_dot(self, dot):
        # To layout the graph in the dot from parent on top to child below it
        # we need to add a parent -> child edge with reversed arrow
        dot.edge(self.node2.id(), self.node1.id(), dir='back', label='parent')


class Graph(object):
    def __init__(self, nodes, edges):
        """Represents a graph

        :param nodes: A list of objects (dicts?) representing the nodes
        :param edges: A list of two tuples of objects (dicts?) representing a
                      relationship between two nodes
        """
        self.nodes = nodes
        self.edges = edges

    def add_to_dot(self, dot, node_field_filter):
        for node in self.nodes:
            node.add_to_dot(dot, node_field_filter)
        for edge in self.edges:
            edge.add_to_dot(dot)
