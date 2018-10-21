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

from osc_placement_tree import graph
from osc_placement_tree.tests import uuids
from osc_placement_tree import tree


class TestTree(base.BaseTestCase):
    def test_make_rp_tree_empty(self):
        mock_client = mock.Mock()
        mock_client.get.return_value = {"resource_providers": []}

        self.assertRaises(
            ValueError, tree.make_rp_tree, mock_client, uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers?in_tree=%s" % uuids.root_rp_A
        )

    def test_make_rp_tree_single_root(self):
        mock_client = mock.Mock()
        mock_client.get.side_effect = [
            # in_tree call
            {
                "resource_providers": [
                    {"uuid": uuids.root_rp_A, "parent_provider_uuid": None}
                ]
            },
            # extending data calls
            {"inventories": {}},
            {"traits": []},
            {"aggregates": []},
            {"usages": {}},
        ]

        graph = tree.make_rp_tree(mock_client, uuids.root_rp_A)

        self.assertEqual(1, len(graph.nodes))
        rp = graph.nodes[0]
        self.assertEqual(uuids.root_rp_A, rp.data["uuid"])

        self.assertEqual(0, len(graph.edges))
        # assert that extended data has been included
        self.assertEqual(uuids.root_rp_A, graph.nodes[0].data["uuid"])
        self.assertEqual({}, rp.data["inventories"])
        self.assertEqual([], rp.data["traits"])
        self.assertEqual([], rp.data["aggregates"])

        mock_client.get.assert_any_call(
            "/resource_providers?in_tree=%s" % uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers/%s/inventories" % uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers/%s/traits" % uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers/%s/aggregates" % uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers/%s/usages" % uuids.root_rp_A
        )
        self.assertEqual(5, mock_client.get.call_count)

    def test_make_rp_tree_single_root_drop_fields(self):
        mock_client = mock.Mock()
        mock_client.get.side_effect = [
            # in_tree call
            {
                "resource_providers": [
                    {
                        "uuid": uuids.root_rp_A,
                        "parent_provider_uuid": None,
                        "garbage": "boo",
                        "not-garbage": 42,
                    }
                ]
            },
            # extending data calls
            {"inventories": {}},
            {"traits": []},
            {"aggregates": []},
            {"usages": {}},
        ]

        graph = tree.make_rp_tree(
            mock_client, uuids.root_rp_A, drop_fields=["traits", "garbage"]
        )

        self.assertEqual(1, len(graph.nodes))
        rp = graph.nodes[0]
        self.assertEqual(uuids.root_rp_A, rp.id())

        self.assertEqual(0, len(graph.edges))
        # assert that extended data has been included but drop_fields keys
        # hasn't
        self.assertEqual({}, rp.data["inventories"])
        self.assertEqual([], rp.data["aggregates"])
        self.assertEqual(42, rp.data["not-garbage"])
        self.assertNotIn("garbage", rp.data)
        self.assertNotIn("traits", rp.data)

        mock_client.get.assert_any_call(
            "/resource_providers?in_tree=%s" % uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers/%s/inventories" % uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers/%s/traits" % uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers/%s/aggregates" % uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers/%s/usages" % uuids.root_rp_A
        )
        self.assertEqual(5, mock_client.get.call_count)

    def test_make_rp_tree_single_root_insert_usages(self):
        mock_client = mock.Mock()
        mock_client.get.side_effect = [
            # in_tree call
            {
                "resource_providers": [
                    {"uuid": uuids.root_rp_A, "parent_provider_uuid": None}
                ]
            },
            # extending data calls
            {"inventories": {"rc1": {"total": 10}, "rc2": {"total": 100}}},
            {"traits": []},
            {"aggregates": []},
            {"usages": {"rc1": 1, "rc2": 10}},
        ]

        graph = tree.make_rp_tree(mock_client, uuids.root_rp_A)

        self.assertEqual(1, len(graph.nodes))
        rp = graph.nodes[0]
        self.assertEqual(uuids.root_rp_A, rp.data["uuid"])

        self.assertEqual(0, len(graph.edges))
        # assert that extended data has been included
        self.assertEqual(uuids.root_rp_A, graph.nodes[0].data["uuid"])
        self.assertEqual(
            {
                "rc1": {"total": 10, "used": 1},
                "rc2": {"total": 100, "used": 10},
            },
            rp.data["inventories"],
        )
        self.assertEqual([], rp.data["traits"])
        self.assertEqual([], rp.data["aggregates"])

        mock_client.get.assert_any_call(
            "/resource_providers?in_tree=%s" % uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers/%s/inventories" % uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers/%s/traits" % uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers/%s/aggregates" % uuids.root_rp_A
        )
        mock_client.get.assert_any_call(
            "/resource_providers/%s/usages" % uuids.root_rp_A
        )
        self.assertEqual(5, mock_client.get.call_count)

    def test_make_rp_tree_multiple_levels(self):
        #        A
        #       / \
        #      C   D
        #     /   / \
        #    E   F   G
        mock_client = mock.Mock()
        in_tree_call = [
            {
                "resource_providers": [
                    {"uuid": uuids.root_rp_A, "parent_provider_uuid": None},
                    {
                        "uuid": uuids.child_rp_C,
                        "parent_provider_uuid": uuids.root_rp_A,
                    },
                    {
                        "uuid": uuids.child_rp_D,
                        "parent_provider_uuid": uuids.root_rp_A,
                    },
                    {
                        "uuid": uuids.grandchild_rp_E,
                        "parent_provider_uuid": uuids.child_rp_C,
                    },
                    {
                        "uuid": uuids.grandchild_rp_F,
                        "parent_provider_uuid": uuids.child_rp_D,
                    },
                    {
                        "uuid": uuids.grandchild_rp_G,
                        "parent_provider_uuid": uuids.child_rp_D,
                    },
                ]
            }
        ]
        data_extension_calls = [
            # extending data calls
            {"inventories": {}},
            {"traits": []},
            {"aggregates": []},
            {"usages": {}},
        ] * 6  # for each node
        mock_client.get.side_effect = in_tree_call + data_extension_calls

        graph = tree.make_rp_tree(mock_client, uuids.root_rp_A)

        self.assertEqual(6, len(graph.nodes))
        self.assertEqual(
            {
                uuids.root_rp_A,
                uuids.child_rp_C,
                uuids.child_rp_D,
                uuids.grandchild_rp_E,
                uuids.grandchild_rp_F,
                uuids.grandchild_rp_G,
            },
            {node.id() for node in graph.nodes},
        )

        self.assertEqual(5, len(graph.edges))
        edges = {(e.node1.id(), e.node2.id()) for e in graph.edges}
        self.assertIn((uuids.child_rp_C, uuids.root_rp_A), edges)
        self.assertIn((uuids.child_rp_D, uuids.root_rp_A), edges)
        self.assertIn((uuids.grandchild_rp_E, uuids.child_rp_C), edges)
        self.assertIn((uuids.grandchild_rp_F, uuids.child_rp_D), edges)
        self.assertIn((uuids.grandchild_rp_G, uuids.child_rp_D), edges)

        mock_client.get.assert_any_call(
            "/resource_providers?in_tree=%s" % uuids.root_rp_A
        )
        for rp in {
            uuids.root_rp_A,
            uuids.child_rp_C,
            uuids.child_rp_D,
            uuids.grandchild_rp_E,
            uuids.grandchild_rp_F,
            uuids.grandchild_rp_G,
        }:
            mock_client.get.assert_any_call(
                "/resource_providers/%s/inventories" % rp
            )
            mock_client.get.assert_any_call(
                "/resource_providers/%s/traits" % rp
            )
            mock_client.get.assert_any_call(
                "/resource_providers/%s/aggregates" % rp
            )
            mock_client.get.assert_any_call(
                "/resource_providers/%s/usages" % rp
            )
        self.assertEqual(1 + 6 * 4, mock_client.get.call_count)

    def test_make_rp_trees_two_simple_root(self):
        mock_client = mock.Mock()
        mock_client.get.side_effect = [
            # resource_providers call
            {
                "resource_providers": [
                    {"uuid": uuids.root_rp_A, "parent_provider_uuid": None},
                    {"uuid": uuids.root_rp_B, "parent_provider_uuid": None},
                ]
            },
            # extending data calls for root_rp_A
            {"inventories": {}},
            {"traits": []},
            {"aggregates": []},
            {"usages": {}},
            # extending data calls for root_rp_B
            {"inventories": {}},
            {"traits": []},
            {"aggregates": []},
            {"usages": {}},
        ]

        graph = tree.make_rp_trees(mock_client)

        self.assertEqual(2, len(graph.nodes))
        self.assertEqual(
            {uuids.root_rp_A, uuids.root_rp_B},
            {node.id() for node in graph.nodes},
        )
        for node in graph.nodes:
            # assert that extended data has been included
            self.assertTrue(
                all(
                    key in node.data
                    for key in ["inventories", "traits", "aggregates"]
                )
            )

        mock_client.get.assert_any_call("/resource_providers")

        for uuid in [uuids.root_rp_A, uuids.root_rp_B]:
            mock_client.get.assert_any_call(
                "/resource_providers/%s/inventories" % uuid
            )
            mock_client.get.assert_any_call(
                "/resource_providers/%s/traits" % uuid
            )
            mock_client.get.assert_any_call(
                "/resource_providers/%s/aggregates" % uuid
            )
            mock_client.get.assert_any_call(
                "/resource_providers/%s/usages" % uuid
            )

        self.assertEqual(9, mock_client.get.call_count)

    @mock.patch("osc_placement_tree.tree._add_consumers_to_the_graph")
    @mock.patch("osc_placement_tree.tree._get_consumer_nodes")
    def test_extend_rp_graph_with_consumers_uses_rps_from_the_graph(
        self, mock_get_consumers, mock_add_consumers
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
        mock_get_consumers.return_value = mock.sentinel.consumers

        tree.extend_rp_graph_with_consumers(mock.sentinel.client, g)

        mock_get_consumers.assert_called_once_with(
            mock.sentinel.client, ["4", "2", "3", "1"]
        )
        mock_add_consumers.assert_called_once_with(g, mock.sentinel.consumers)

    def test_get_consumer_nodes_collects_from_every_rp(self):
        mock_client = mock.Mock()
        mock_client.get.side_effect = [
            # first it will get allocations from each rp uuid
            # rp1
            {
                "allocations": {
                    uuids.consumer1: {"resources": {}},
                    uuids.consumer2: {"resources": {}},
                }
            },
            # rp2, consumer2 allocates from both rp1 and rp2
            {
                "allocations": {
                    uuids.consumer2: {"resources": {}},
                    uuids.consumer3: {"resources": {}},
                }
            },
            # then get every discovered consumers
            # consumer1
            {
                "allocations": {
                    uuids.rp1: {"generation": 2, "resources": {"DISK_GB": 5}}
                },
                "project_id": "7e67cbf7-7c38-4a32-b85b-0739c690991a",
                "user_id": "067f691e-725a-451a-83e2-5c3d13e1dffc",
            },
            # consumer2
            {
                "allocations": {
                    uuids.rp1: {"generation": 2, "resources": {"DISK_GB": 5}},
                    uuids.rp2: {"generation": 2, "resources": {"DISK_GB": 5}},
                },
                "project_id": "7e67cbf7-7c38-4a32-b85b-0739c690991a",
                "user_id": "067f691e-725a-451a-83e2-5c3d13e1dffc",
            },
            # consumer3
            {
                "allocations": {
                    uuids.rp2: {"generation": 2, "resources": {"DISK_GB": 5}}
                },
                "project_id": "7e67cbf7-7c38-4a32-b85b-0739c690991a",
                "user_id": "067f691e-725a-451a-83e2-5c3d13e1dffc",
            },
        ]

        consumers = tree._get_consumer_nodes(
            mock_client, [uuids.rp1, uuids.rp2]
        )

        self.assertEqual(
            [
                # first it will get allocations from each rp uuid
                mock.call("/resource_providers/%s/allocations" % uuids.rp1),
                mock.call("/resource_providers/%s/allocations" % uuids.rp2),
            ],
            # the rest is in undefined order due to sets used internally
            mock_client.get.mock_calls[0:2],
        )

        consumer_calls = mock_client.get.mock_calls[2:]
        self.assertEqual(3, len(consumer_calls))
        self.assertIn(
            mock.call("/allocations/%s" % uuids.consumer1), consumer_calls
        )
        self.assertIn(
            mock.call("/allocations/%s" % uuids.consumer2), consumer_calls
        )
        self.assertIn(
            mock.call("/allocations/%s" % uuids.consumer3), consumer_calls
        )

        self.assertEqual(3, len(consumers))
        self.assertEqual(
            {uuids.consumer1, uuids.consumer2, uuids.consumer3},
            {c.id() for c in consumers},
        )

    def test_add_consumers_to_the_graph(self):
        grandchild = graph.RpNode(
            {"uuid": uuids.grandchild_rp, "name": "grand"}
        )
        child1 = graph.RpNode({"uuid": uuids.child1_rp, "name": "child1"})
        child2 = graph.RpNode({"uuid": uuids.child2_rp, "name": "child2"})
        root = graph.RpNode({"uuid": uuids.root_rp, "name": "root"})

        g = graph.Graph(
            nodes=[grandchild, child1, child2, root],
            edges=[
                graph.ParentEdge(node1=child1, node2=root),
                graph.ParentEdge(node1=child2, node2=root),
                graph.ParentEdge(node1=grandchild, node2=child2),
            ],
        )
        consumer_nodes = [
            graph.ConsumerNode(
                {
                    "consumer_uuid": uuids.consumer1,
                    "allocations": {uuids.root_rp: {}, uuids.child1_rp: {}},
                }
            ),
            graph.ConsumerNode(
                {
                    "consumer_uuid": uuids.consumer2,
                    "allocations": {
                        uuids.grandchild_rp: {},
                        uuids.child2_rp: {},
                    },
                }
            ),
        ]
        tree._add_consumers_to_the_graph(g, consumer_nodes)

        for consumer_node in consumer_nodes:
            self.assertIn(consumer_node, g.nodes)

        self.assertIn(
            graph.AllocationEdge(
                g.get_node_by_id(uuids.consumer1),
                g.get_node_by_id(uuids.root_rp),
            ),
            g.edges,
        )
        self.assertIn(
            graph.AllocationEdge(
                g.get_node_by_id(uuids.consumer1),
                g.get_node_by_id(uuids.child1_rp),
            ),
            g.edges,
        )
        self.assertIn(
            graph.AllocationEdge(
                g.get_node_by_id(uuids.consumer2),
                g.get_node_by_id(uuids.grandchild_rp),
            ),
            g.edges,
        )
        self.assertIn(
            graph.AllocationEdge(
                g.get_node_by_id(uuids.consumer2),
                g.get_node_by_id(uuids.child2_rp),
            ),
            g.edges,
        )
