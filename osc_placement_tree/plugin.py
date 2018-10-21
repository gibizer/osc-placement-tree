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

"OpenStackClient plugin for advanced CLI for Placement service"

import logging

from osc_lib import utils

LOG = logging.getLogger(__name__)

# needs something different than placement not to conflict with osc-placement
API_NAME = "placement_tree"
# this is needed by OSC to be defined even if this plugin does not provide
# such option for the end user
API_VERSION_OPTION = ""
# 1.14 is needed for reading nested RPs with in_tree query
MINIMUM_PLACEMENT_VERSION = "1.14"


def make_client(instance):
    client_class = utils.get_client_class(
        API_NAME,
        MINIMUM_PLACEMENT_VERSION,
        {MINIMUM_PLACEMENT_VERSION: "osc_placement_tree.http.SessionClient"},
    )

    ks_filter = {
        "service_type": "placement",
        "region_name": instance._region_name,
        "interface": instance.interface,
    }

    LOG.debug(
        "Instantiating placement client for placement_tree: %s", client_class
    )
    return client_class(
        session=instance.session,
        ks_filter=ks_filter,
        api_version=MINIMUM_PLACEMENT_VERSION,
    )


def build_option_parser(parser):
    return parser
