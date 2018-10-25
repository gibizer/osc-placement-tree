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
        dot.node(self.id(), html._get_attr_html(self.data, field_filter))

    def id(self):
        return self.data["uuid"]


class ConsumerNode(Node):
    def _get_node_data(self):
        import copy

        data = copy.deepcopy(self.data)
        data.pop("allocations")
        return data

    def add_to_dot(self, dot, field_filter):
        dot.node(
            self.id(),
            html._get_attr_html(self._get_node_data(), lambda _: True),
        )

    def id(self):
        return self.data["consumer_uuid"]


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
        dot.edge(self.node2.id(), self.node1.id(), dir="back", label="parent")


class AllocationEdge(Edge):
    """A consumer -> rp edge representing an allocation

    node1 should be the ConsumerNode
    node2 should be the RpNode
    """

    def add_to_dot(self, dot):
        resources = self.node1.data["allocations"][self.node2.id()][
            "resources"
        ]
        # To layout the graph in the dot from RPs on the top and consumers
        # below we need to add the edge reversed
        dot.edge(
            self.node2.id(),
            self.node1.id(),
            dir="back",
            label="<{html}>".format(
                html=html._get_html_dict(
                    resources, lambda _: True, header="consumes"
                )
            ),
            decorate="true",  # connect the label to the edge
            minlen="2",  # make sure there is space for the label
            style="dashed",
        )


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

    @property
    def rp_nodes(self):
        # isintance is ugly, alternatively we could store RpNodes in a separate
        # list internally.
        return [node for node in self.nodes if isinstance(node, RpNode)]

    def get_node_by_id(self, id):
        for node in self.nodes:
            if node.id() == id:
                return node
        raise ValueError("Node with id %s not found in the graph" % id)
