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

        tree_root = tree.make_rp_tree(mock_client, uuids.root_rp_A)
        self.assertEqual(None, tree_root)
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

        tree_root = tree.make_rp_tree(mock_client, uuids.root_rp_A)

        self.assertEqual(uuids.root_rp_A, tree_root.data['uuid'])
        self.assertEqual(0, len(tree_root.children))
        # assert that extended data has been included
        self.assertEqual(1, tree_root.data['call1-key'])
        self.assertEqual(2, tree_root.data['call2-key'])
        self.assertEqual(3, tree_root.data['call3-key'])

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

        tree_root = tree.make_rp_tree(mock_client, uuids.root_rp_A,
                                      drop_fields=['call2-key', 'garbage'])

        self.assertEqual(uuids.root_rp_A, tree_root.data['uuid'])
        self.assertEqual(0, len(tree_root.children))
        # assert that extended data has been included but drop_fields keys
        # hasn't
        self.assertEqual(1, tree_root.data['call1-key'])
        self.assertEqual(3, tree_root.data['call3-key'])
        self.assertEqual(42, tree_root.data['not-garbage'])
        self.assertNotIn('garbage', tree_root.data)
        self.assertNotIn('call2-key', tree_root.data)

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

        tree_root = tree.make_rp_tree(mock_client, uuids.root_rp_A)

        self.assertEqual(uuids.root_rp_A, tree_root.data['uuid'])
        self.assertEqual(2, len(tree_root.children))
        self.assertEqual({uuids.child_rp_C, uuids.child_rp_D},
                         {child.data['uuid'] for child in tree_root.children})

        def assert_relations(node):
            if node.data['uuid'] == uuids.child_rp_C:
                self.assertEqual(1, len(node.children))
                self.assertEqual({uuids.grandchild_rp_E},
                                 {child.data['uuid']
                                  for child in node.children})
            if node.data['uuid'] == uuids.child_rp_D:
                self.assertEqual(2, len(node.children))
                self.assertEqual({uuids.grandchild_rp_F,
                                  uuids.grandchild_rp_G},
                                 {child.data['uuid']
                                  for child in node.children})
            if node in {uuids.grandchild_rp_E, uuids.grandchild_rp_F,
                        uuids.grandchild_rp_G}:
                self.assertEqual(0, len(node.children))

        tree_root.walk(assert_relations)

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
