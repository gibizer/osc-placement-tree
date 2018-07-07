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

from cliff import command
from osc_placement_tree import dot
from osc_placement_tree import tree


class ClientAdapter(object):
    def __init__(self, client):
        self.client = client

    def get(self, url):
        return self.client.request('GET', url).json()


# This inherits directly from cliff as it wants to emit other than a simple
# table on the output
class ShowProviderTree(command.Command):
    """Show the tree of resource providers"""

    def get_parser(self, prog_name):
        parser = super(ShowProviderTree, self).get_parser(prog_name)

        parser.add_argument(
            'uuid',
            metavar='<name>',
            help='UUID of one of the provider in the tree to show'
        )

        return parser

    def take_action(self, parsed_args):
        http = self.app.client_manager.placement_tree

        tree_root = tree.make_rp_tree(
            ClientAdapter(http),
            parsed_args.uuid,
            drop_fields=['links', 'resource_provider_generation'])

        print(
            dot.to_dot(tree_root,
                       id_selector=lambda node: node.data['uuid']))
