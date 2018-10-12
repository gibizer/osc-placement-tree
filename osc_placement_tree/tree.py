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


class TreeNode(object):
    """The wrapper for a tree node"""

    def __init__(self, data, children=None):
        """Create a TreeNode

        :param data: the object at the current Tree node
        :param children: the connected Tree nodes
        """
        self.data = data
        self.children = [] if not children else children

    def walk(self, func):
        func(self)
        for child in self.children:
            child.walk(func)


def _build_tree(all_nodes, current_node):
    """Do a recursive breadth-first walk of the tree and build relationships"""
    children = [node for node in all_nodes
                if (node.data['parent_provider_uuid'] ==
                    current_node.data['uuid'])]
    current_node.children = children
    for node in children:
        _build_tree(all_nodes, node)


def _extend_placement_rps(rps, client):
    return [_extend_rp_data(client, rp) for rp in rps]


def _wrap_placement_rps_into_tree_nodes(rps):
    return [TreeNode(data=rp) for rp in rps]


def _get_roots(nodes):
    return [node for node in nodes
            if node.data['parent_provider_uuid'] is None]


def _drop_fields(drop_fields, nodes):
    if drop_fields:
        for node in nodes:
            for field in drop_fields:
                node.data.pop(field)


def make_rp_trees(client, drop_fields=None):
    """Builds the whole RP graph

    :param client: a placement client providing a get(url) call that returns
                   the REST response body as a python object
    :param drop_fields: the list of field names not to include in the result
    :return: a list of TreeNode objects
    """
    url = '/resource_providers'
    rps = client.get(url)['resource_providers']

    rps = _extend_placement_rps(rps, client)
    nodes = _wrap_placement_rps_into_tree_nodes(rps)
    roots = _get_roots(nodes)

    for root in roots:
        _build_tree(nodes, root)

    _drop_fields(drop_fields, nodes)
    return roots


def make_rp_tree(client, in_tree_rp_uuid, drop_fields=None):
    """Builds a tree from TreeNodes containing the RP tree

    :param client: a placement client providing a get(url) call that returns
                   the REST response body as a python object
    :param in_tree_rp_uuid: an RP uuid from the RP tree that is requested
    :param drop_fields: the list of field names not to include in the result
    :return: a TreeNode object that is the root
    """

    url = '/resource_providers?in_tree=%s' % in_tree_rp_uuid
    rps_in_tree = client.get(url)['resource_providers']
    if not rps_in_tree:
        raise ValueError('%s does not exists' % in_tree_rp_uuid)

    rps = _extend_placement_rps(rps_in_tree, client)
    nodes = _wrap_placement_rps_into_tree_nodes(rps)
    root = _get_roots(nodes)[0]

    _build_tree(nodes, root)
    _drop_fields(drop_fields, nodes)
    return root


def _extend_rp_data(client, rp):
    rp.update(client.get('/resource_providers/%s/inventories' % rp['uuid']))
    rp.update(client.get('/resource_providers/%s/traits' % rp['uuid']))
    rp.update(client.get('/resource_providers/%s/aggregates' % rp['uuid']))
    return rp
