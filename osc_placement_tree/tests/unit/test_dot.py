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
from osc_placement_tree.tests import base
from osc_placement_tree import tree


class TestDot(base.TestBase):

    @mock.patch('graphviz.dot.Dot.edge')
    @mock.patch('graphviz.dot.Dot.node')
    def test_tree_to_dot_walks_nodes_and_edges(
            self, mock_add_node, mock_add_edge):
        grandchild = tree.TreeNode(
            {'id': '4', 'name': 'grand'},
            children=[])
        child1 = tree.TreeNode(
            {'id': '2', 'name': 'child1'},
            children=[])
        child2 = tree.TreeNode(
            {'id': '3', 'name': 'child2'},
            children=[grandchild])
        root = tree.TreeNode(
            {'id': '1', 'name': 'root'},
            children=[child1, child2])

        dot.tree_to_dot(root, id_selector=lambda n: n.data['id'])

        some_html = mock.ANY
        self.assertEqual(
            [mock.call('1', some_html),
             mock.call('2', some_html),
             mock.call('3', some_html),
             mock.call('4', some_html)],
            mock_add_node.mock_calls)
        self.assertEqual(
            [mock.call('1', '2', dir='back'),
             mock.call('1', '3', dir='back'),
             mock.call('3', '4', dir='back')],
            mock_add_edge.mock_calls)

    @mock.patch('graphviz.dot.Dot.node')
    @mock.patch('osc_placement_tree.dot._get_attr_html')
    def test_tree_to_dot_filters_node_data(
            self, mock_get_attr_html, mock_add_node):
        child = tree.TreeNode(
            {'id': '2', 'name': 'child', 'not_needed_field': 42},
            children=[])
        root = tree.TreeNode(
            {'id': '1', 'name': 'root', 'not_needed_field': 42},
            children=[child])

        dot.tree_to_dot(
            root,
            id_selector=lambda n: n.data['id'],
            field_filter=lambda name: name in ['id', 'name'])

        self.assertEqual(
            [mock.call({'id': '1', 'name': 'root'}),
             mock.call({'id': '2', 'name': 'child'})],
            mock_get_attr_html.mock_calls)
