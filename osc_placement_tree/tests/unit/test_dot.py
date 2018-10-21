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
import mock

from osc_placement_tree import dot
from osc_placement_tree import graph
from osc_placement_tree.tests import base


class TestDot(base.TestBase):
    @mock.patch("graphviz.dot.Dot.edge")
    @mock.patch("graphviz.dot.Dot.node")
    def test_graph_to_dot_walks_nodes_and_edges(
        self, mock_add_node, mock_add_edge
    ):
        grandchild = graph.RpNode({"uuid": "4", "name": "grand"})
        child1 = graph.RpNode({"uuid": "2", "name": "child1"})
        child2 = graph.RpNode({"uuid": "3", "name": "child2"})
        root = graph.RpNode({"uuid": "1", "name": "root"})

        g = graph.Graph(
            nodes=[grandchild, child1, child2, root],
            edges=[
                graph.ParentEdge(node1=child1, node2=root),
                graph.ParentEdge(node1=child2, node2=root),
                graph.ParentEdge(node1=grandchild, node2=child2),
            ],
        )

        dot.graph_to_dot(g)

        some_html = mock.ANY
        self.assertEqual(
            [
                mock.call("4", some_html),
                mock.call("2", some_html),
                mock.call("3", some_html),
                mock.call("1", some_html),
            ],
            mock_add_node.mock_calls,
        )
        self.assertEqual(
            [
                mock.call("1", "2", dir="back", label="parent"),
                mock.call("1", "3", dir="back", label="parent"),
                mock.call("3", "4", dir="back", label="parent"),
            ],
            mock_add_edge.mock_calls,
        )

    @mock.patch("graphviz.dot.Dot.node")
    @mock.patch("osc_placement_tree.html._get_html_key_value")
    def test_graph_to_dot_filters_node_data(
        self, mock_get_html_key_value, mock_add_node
    ):
        mock_get_html_key_value.return_value = ""
        child = graph.RpNode(
            {"uuid": "2", "name": "child", "not_needed_field": 42}
        )
        root = graph.RpNode(
            {"uuid": "1", "name": "root", "not_needed_field": 42}
        )
        g = graph.Graph(
            nodes=[root, child],
            edges=[graph.ParentEdge(node1=child, node2=root)],
        )

        filter = lambda name: name in ["uuid", "name"]
        dot.graph_to_dot(g, field_filter=filter)

        self.assertEqual(
            [
                mock.call("name", "root", filter),
                mock.call("uuid", "1", filter),
                mock.call("name", "child", filter),
                mock.call("uuid", "2", filter),
            ],
            mock_get_html_key_value.mock_calls,
        )
