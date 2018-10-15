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
from oslotest import base

from osc_placement_tree.tests import uuids
from osc_placement_tree import tree


class TestTree(base.BaseTestCase):

    def test_make_rp_tree_empty(self):
        mock_client = mock.Mock()
        mock_client.get.return_value = {
            'resource_providers': []}

        self.assertRaises(
            ValueError,
            tree.make_rp_tree, mock_client, uuids.root_rp_A)
        mock_client.get.assert_any_call(
            '/resource_providers?in_tree=%s' % uuids.root_rp_A)

    def test_make_rp_tree_single_root(self):
        mock_client = mock.Mock()
        mock_client.get.side_effect = [
            # in_tree call
            {'resource_providers': [
                {'uuid': uuids.root_rp_A,
                 'parent_provider_uuid': None},
            ]
            },
            # extending data calls
            {'call1-key': 1},
            {'call2-key': 2},
            {'call3-key': 3}
        ]

        graph = tree.make_rp_tree(mock_client, uuids.root_rp_A)

        self.assertEqual(1, len(graph.nodes))
        rp = graph.nodes[0]
        self.assertEqual(uuids.root_rp_A, rp.data['uuid'])

        self.assertEqual(0, len(graph.edges))
        # assert that extended data has been included
        self.assertEqual(uuids.root_rp_A, graph.nodes[0].data['uuid'])
        self.assertEqual(1, rp.data['call1-key'])
        self.assertEqual(2, rp.data['call2-key'])
        self.assertEqual(3, rp.data['call3-key'])

        mock_client.get.assert_any_call(
            '/resource_providers?in_tree=%s' % uuids.root_rp_A)
        mock_client.get.assert_any_call(
            '/resource_providers/%s/inventories' % uuids.root_rp_A)
        mock_client.get.assert_any_call(
            '/resource_providers/%s/traits' % uuids.root_rp_A)
        mock_client.get.assert_any_call(
            '/resource_providers/%s/aggregates' % uuids.root_rp_A)
        self.assertEqual(4, mock_client.get.call_count)

    def test_make_rp_tree_single_root_drop_fields(self):
        mock_client = mock.Mock()
        mock_client.get.side_effect = [
            # in_tree call
            {'resource_providers': [
                {'uuid': uuids.root_rp_A,
                 'parent_provider_uuid': None,
                 'garbage': 'boo',
                 'not-garbage': 42},
            ]
            },
            # extending data calls
            {'call1-key': 1},
            {'call2-key': 2},
            {'call3-key': 3}
        ]

        graph = tree.make_rp_tree(mock_client, uuids.root_rp_A,
                                  drop_fields=['call2-key', 'garbage'])

        self.assertEqual(1, len(graph.nodes))
        rp = graph.nodes[0]
        self.assertEqual(uuids.root_rp_A, rp.id())

        self.assertEqual(0, len(graph.edges))
        # assert that extended data has been included but drop_fields keys
        # hasn't
        self.assertEqual(1, rp.data['call1-key'])
        self.assertEqual(3, rp.data['call3-key'])
        self.assertEqual(42, rp.data['not-garbage'])
        self.assertNotIn('garbage', rp.data)
        self.assertNotIn('call2-key', rp.data)

        mock_client.get.assert_any_call(
            '/resource_providers?in_tree=%s' % uuids.root_rp_A)
        mock_client.get.assert_any_call(
            '/resource_providers/%s/inventories' % uuids.root_rp_A)
        mock_client.get.assert_any_call(
            '/resource_providers/%s/traits' % uuids.root_rp_A)
        mock_client.get.assert_any_call(
            '/resource_providers/%s/aggregates' % uuids.root_rp_A)
        self.assertEqual(4, mock_client.get.call_count)

    def test_make_rp_tree_multiple_levels(self):
        #        A
        #       / \
        #      C   D
        #     /   / \
        #    E   F   G
        mock_client = mock.Mock()
        mock_client.get.return_value = {
            'resource_providers': [
                {'uuid': uuids.root_rp_A,
                 'parent_provider_uuid': None},
                {'uuid': uuids.child_rp_C,
                 'parent_provider_uuid': uuids.root_rp_A},
                {'uuid': uuids.child_rp_D,
                 'parent_provider_uuid': uuids.root_rp_A},
                {'uuid': uuids.grandchild_rp_E,
                 'parent_provider_uuid': uuids.child_rp_C},
                {'uuid': uuids.grandchild_rp_F,
                 'parent_provider_uuid': uuids.child_rp_D},
                {'uuid': uuids.grandchild_rp_G,
                 'parent_provider_uuid': uuids.child_rp_D},
            ]}

        graph = tree.make_rp_tree(mock_client, uuids.root_rp_A)

        self.assertEqual(6, len(graph.nodes))
        self.assertEqual(
            {uuids.root_rp_A, uuids.child_rp_C, uuids.child_rp_D,
             uuids.grandchild_rp_E, uuids.grandchild_rp_F,
             uuids.grandchild_rp_G},
            {node.id() for node in graph.nodes})

        self.assertEqual(5, len(graph.edges))
        edges = {(e.node1.id(), e.node2.id()) for e in graph.edges}
        self.assertIn((uuids.child_rp_C, uuids.root_rp_A), edges)
        self.assertIn((uuids.child_rp_D, uuids.root_rp_A), edges)
        self.assertIn((uuids.grandchild_rp_E, uuids.child_rp_C), edges)
        self.assertIn((uuids.grandchild_rp_F, uuids.child_rp_D), edges)
        self.assertIn((uuids.grandchild_rp_G, uuids.child_rp_D), edges)

        mock_client.get.assert_any_call(
            '/resource_providers?in_tree=%s' % uuids.root_rp_A)
        for rp in {uuids.root_rp_A, uuids.child_rp_C, uuids.child_rp_D,
                   uuids.grandchild_rp_E, uuids.grandchild_rp_F,
                   uuids.grandchild_rp_G}:
            mock_client.get.assert_any_call(
                '/resource_providers/%s/inventories' % rp)
            mock_client.get.assert_any_call(
                '/resource_providers/%s/traits' % rp)
            mock_client.get.assert_any_call(
                '/resource_providers/%s/aggregates' % rp)
        self.assertEqual(19, mock_client.get.call_count)

    def test_make_rp_trees_two_simple_root(self):
        mock_client = mock.Mock()
        mock_client.get.side_effect = [
            # resource_providers call
            {'resource_providers': [
                {'uuid': uuids.root_rp_A,
                 'parent_provider_uuid': None},
                {'uuid': uuids.root_rp_B,
                 'parent_provider_uuid': None},
            ]
            },
            # extending data calls for root_rp_A
            {'call1-key': 1},
            {'call2-key': 2},
            {'call3-key': 3},
            # extending data calls for root_rp_B
            {'call1-key': 4},
            {'call2-key': 5},
            {'call3-key': 6},
        ]

        graph = tree.make_rp_trees(mock_client)

        self.assertEqual(2, len(graph.nodes))
        self.assertEqual({uuids.root_rp_A, uuids.root_rp_B},
                         {node.id() for node in graph.nodes})
        for node in graph.nodes:
            # assert that extended data has been included
            self.assertTrue(all(node.data[key]
                                for key in ['call1-key', 'call2-key',
                                            'call3-key']))

        mock_client.get.assert_any_call('/resource_providers')

        for uuid in [uuids.root_rp_A, uuids.root_rp_B]:
            mock_client.get.assert_any_call(
                '/resource_providers/%s/inventories' % uuid)
            mock_client.get.assert_any_call(
                '/resource_providers/%s/traits' % uuid)
            mock_client.get.assert_any_call(
                '/resource_providers/%s/aggregates' % uuid)

        self.assertEqual(7, mock_client.get.call_count)
