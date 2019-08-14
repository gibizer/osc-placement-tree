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
from osc_placement_tree import dot
from osc_placement_tree.resources import provider_tree
from osc_placement_tree import tree

DROP_DATA_FIELDS = provider_tree.DROP_DATA_FIELDS


class PlacementFixtureAsClientWrapper(object):
    """Adapter for the placement fixture used in the nova functional tests"""

    def __init__(self, placement_fixture_api):
        """Wraps a nova.tests.functional.fixtures.PlacementApiClient instance

        :param placement_fixture_api: placement client
        :type placement_fixture_api:
            nova.tests.functional.fixtures.PlacementApiClient
        """
        self.client = placement_fixture_api

    def get(self, url):
        return self.client.get(url, version="latest").body


class PlacementDirectAsClientWrapper(object):
    """Adapter for the PlacementDirect based clients"""

    def __init__(self, placement_direct):
        """Wraps a placement.direct.PlacementDirect instance

        :param placement_direct: a placement client
        :type placement_direct: placement.direct.PlacementDirect
        """
        self.client = placement_direct

    def get(self, url):
        return self.client.get(url).json()


def dump_placement_db_to_dot(placement_client, out_file, hidden_fields=()):
    """Export the placement db content to a dot file

    Usage in nova functional test env:

        from osc_placement_tree import utils as placement_visual

        placement_visual.dump_placement_db_to_dot(
            placement_visual.PlacementFixtureAsClientWrapper(
                self.placement_api),
            '/tmp/dump.dot')

    Usage in placement functional env:

        from osc_placement_tree import utils as placement_visual
        from placement import direct

        with direct.PlacementDirect(
                self.conf_fixture.conf, latest_microversion=True) as client:
            placement_visual.dump_placement_db_to_dot(
                placement_visual.PlacementDirectAsClientWrapper(client),
                '/tmp/dump.dot')


    :param placement_client: A placement client wrapper to call the placement
        service. Use PlacementFixtureAsClientWrapper or
        PlacementDirectAsClientWrapper depending on your environment.
    :param out_file: The file path to store the dot file
    :param hidden_fields: The list of the name of the resource provider fields
        not to include in the output
    """

    graph = tree.make_rp_trees(placement_client, drop_fields=DROP_DATA_FIELDS)
    tree.extend_rp_graph_with_consumers(placement_client, graph)

    with open(out_file, "w") as f:
        f.write(
            dot.graph_to_dot(
                graph, field_filter=lambda name: name not in hidden_fields
            )
        )
