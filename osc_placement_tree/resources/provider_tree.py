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

# These fields are provided by placement but after processing they are
# represented by the model itself so these fields can be dropped from the data
# store
DROP_DATA_FIELDS = [
    "links",  # unused
    "parent_provider_uuid",  # represented by node relationships
    "root_provider_uuid",
]  # unused

# These fields are not included in the generated output if they are not
# explicitly requested by the user
DEFAULT_HIDDEN_FIELDS = [
    "generation",
    "resource_provider_generation",
    "min_unit",
    "max_unit",
    "step_size",
]


class ClientAdapter(object):
    def __init__(self, client):
        self.client = client

    def get(self, url):
        return self.client.request("GET", url).json()


def _get_field_filter(parsed_args):
    if parsed_args.fields:
        fields = parsed_args.fields.split(",")
        return lambda name: name in fields
    else:
        return lambda name: name not in DEFAULT_HIDDEN_FIELDS


# This inherits directly from cliff as it wants to emit other than a simple
# table on the output
class ShowProviderTree(command.Command):
    """Show the tree of resource providers"""

    def get_parser(self, prog_name):
        parser = super(ShowProviderTree, self).get_parser(prog_name)

        parser.add_argument(
            "uuid",
            metavar="<name>",
            help="UUID of one of the provider in the tree to show",
        )
        parser.add_argument(
            "--fields",
            metavar="<fields>",
            help="The coma separated list of field names of the resource "
            "provider to include in the output.",
            default="",
        )
        parser.add_argument(
            "--show_consumers",
            help="Includes consumers in the result",
            nargs="?",
            const=True,
            default=False,
        )
        return parser

    def take_action(self, parsed_args):
        http = self.app.client_manager.placement_tree
        client = ClientAdapter(http)

        graph = tree.make_rp_tree(
            client, parsed_args.uuid, drop_fields=DROP_DATA_FIELDS
        )

        if parsed_args.show_consumers:
            tree.extend_rp_graph_with_consumers(client, graph)

        print(
            dot.graph_to_dot(
                graph, field_filter=_get_field_filter(parsed_args)
            )
        )


class ListProviderTree(command.Command):
    """Show the whole RP graph"""

    def get_parser(self, prog_name):
        parser = super(ListProviderTree, self).get_parser(prog_name)
        parser.add_argument(
            "--fields",
            metavar="<fields>",
            help="The coma separated list of field names of the resource "
            "provider to include in the output.",
            default="",
        )
        parser.add_argument(
            "--show_consumers",
            help="Includes consumers in the result",
            nargs="?",
            const=True,
            default=False,
        )
        return parser

    def take_action(self, parsed_args):
        http = self.app.client_manager.placement_tree
        client = ClientAdapter(http)

        graph = tree.make_rp_trees(client, drop_fields=DROP_DATA_FIELDS)

        if parsed_args.show_consumers:
            tree.extend_rp_graph_with_consumers(client, graph)

        print(
            dot.graph_to_dot(
                graph, field_filter=_get_field_filter(parsed_args)
            )
        )
