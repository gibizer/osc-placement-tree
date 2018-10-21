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
from osc_placement_tree import graph


def _drop_fields(drop_fields, nodes):
    if drop_fields:
        for node in nodes:
            for field in drop_fields:
                node.pop(field)


def _get_node_by_id(id, nodes):
    for node in nodes:
        if node.id() == id:
            return node
    raise ValueError("Node %s not found" % id)


def _get_parent_edges_between_rp_nodes(nodes):
    edges = []
    for node in nodes:
        if node.data["parent_provider_uuid"]:
            parent_node = _get_node_by_id(
                node.data["parent_provider_uuid"], nodes
            )
            edges.append(graph.ParentEdge(node, parent_node))
    return edges


def _make_graph_from_rps(rps, drop_fields):
    nodes = [graph.RpNode(rp) for rp in rps]
    parent_edges = _get_parent_edges_between_rp_nodes(nodes)
    # TODO(gibi) handle consumer nodes and edges here

    # this is done late so we can drop parent_provider_uuid as well that is
    # still used above but not any more
    _drop_fields(drop_fields, rps)
    return graph.Graph(nodes=nodes, edges=parent_edges)


def make_rp_trees(client, drop_fields=None):
    """Builds the whole RP graph

    :param client: a placement client providing a get(url) call that returns
                   the REST response body as a python object
    :param drop_fields: the list of field names not to include in the result
    :return: a list of Node objects
    """
    url = "/resource_providers"
    rps = client.get(url)["resource_providers"]
    rps = _extend_placement_rps(rps, client)
    return _make_graph_from_rps(rps, drop_fields)


def make_rp_tree(client, in_tree_rp_uuid, drop_fields=None):
    """Builds a tree from TreeNodes containing the RP tree

    :param client: a placement client providing a get(url) call that returns
                   the REST response body as a python object
    :param in_tree_rp_uuid: an RP uuid from the RP tree that is requested
    :param drop_fields: the list of field names not to include in the result
    :return: a Node object that is the root
    """

    url = "/resource_providers?in_tree=%s" % in_tree_rp_uuid
    rps_in_tree = client.get(url)["resource_providers"]
    if not rps_in_tree:
        raise ValueError("%s does not exists" % in_tree_rp_uuid)
    rps = _extend_placement_rps(rps_in_tree, client)
    return _make_graph_from_rps(rps, drop_fields)


def _extend_placement_rps(rps, client):
    return [_extend_rp_data(client, rp) for rp in rps]


def _extend_rp_data(client, rp):
    rp.update(client.get("/resource_providers/%s/inventories" % rp["uuid"]))
    rp.update(client.get("/resource_providers/%s/traits" % rp["uuid"]))
    rp.update(client.get("/resource_providers/%s/aggregates" % rp["uuid"]))

    usages = client.get("/resource_providers/%s/usages" % rp["uuid"])
    for rc in rp["inventories"]:
        rp["inventories"][rc]["used"] = usages["usages"][rc]

    return rp


def _get_consumer_nodes(client, rp_uuids):
    """Return every consumer that allocates from the given rp_uuids

        :returns: a list of ConsumerNode objects
    """
    # need to get all the consumers from every RP and merged them as a single
    # consumer might allocate from more than one RP and placement doesn't have
    # a standalone consumer endpoint
    consumer_uuids = set()
    for rp_uuid in rp_uuids:
        consumers = client.get("/resource_providers/%s/allocations" % rp_uuid)[
            "allocations"
        ].keys()
        consumer_uuids = consumer_uuids.union(consumers)
    # now get consumers one by one
    consumers = {}
    for consumer_uuid in consumer_uuids:
        consumers[consumer_uuid] = client.get(
            "/allocations/%s" % consumer_uuid
        )
        # extend that data with its own id
        consumers[consumer_uuid]["consumer_uuid"] = consumer_uuid
    return [
        graph.ConsumerNode(data=consumer) for consumer in consumers.values()
    ]


def _add_consumers_to_the_graph(g, consumer_nodes):
    """Extends the graph with the consumer nodes by connecting them to the RPs

    :param g: the current Graph object containing RPs, this will be extended
              with consumers
    :param consumer_nodes: a list of ConsumerNode objects allocating from the
                           RPs in the graph
    """
    g.nodes.extend(consumer_nodes)
    for consumer_node in consumer_nodes:
        for rp_uuid in consumer_node.data["allocations"].keys():
            rp_node = g.get_node_by_id(rp_uuid)
            g.edges.append(graph.AllocationEdge(consumer_node, rp_node))


def extend_rp_graph_with_consumers(client, g):
    rp_uuids = [rp_node.id() for rp_node in g.rp_nodes]
    consumers = _get_consumer_nodes(client, rp_uuids)
    _add_consumers_to_the_graph(g, consumers)
