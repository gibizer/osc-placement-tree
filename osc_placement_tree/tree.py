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


def make_rp_tree(client, in_tree_rp_uuid, drop_fields=None):
    """Builds a tree from TreeNodes containing the RP tree

    :param client: a placement client providing a get(url) call that returns
                   the REST response body as a python object
    :param in_tree_rp_uuid: an RP uuid from the RP tree that is requested
    :return: a TreeNode object that is the root
    """

    url = '/resource_providers?in_tree=%s' % in_tree_rp_uuid
    rps_in_tree = client.get(url)['resource_providers']
    if not rps_in_tree:
        return None

    nodes = [TreeNode(data=_extend_rp_data(client, rp, drop_fields))
             for rp in rps_in_tree]
    root = [node for node in nodes
            if node.data['parent_provider_uuid'] is None][0]

    def build_tree(all_nodes, current_node):
        # do a recursive breadth-first walk of the tree
        children = filter(
            lambda node: (node.data['parent_provider_uuid'] ==
                          current_node.data['uuid']),
            all_nodes)

        current_node.children = children
        for node in children:
            build_tree(all_nodes, node)

    build_tree(nodes, root)
    return root


def _extend_rp_data(client, rp, drop_fields):
    rp.update(client.get('/resource_providers/%s/inventories' % rp['uuid']))
    rp.update(client.get('/resource_providers/%s/traits' % rp['uuid']))
    rp.update(client.get('/resource_providers/%s/aggregates' % rp['uuid']))
    if drop_fields:
        for field in drop_fields:
            rp.pop(field)
    return rp
