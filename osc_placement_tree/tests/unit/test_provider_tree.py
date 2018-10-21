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

from osc_placement_tree.resources import provider_tree
from osc_placement_tree.tests import base


class TestDot(base.TestBase):
    def test_get_field_filter_no_user_input(self):
        parsed_args = mock.Mock()
        parsed_args.fields = None

        f = provider_tree._get_field_filter(parsed_args)

        self.assertTrue(f("foo"))
        self.assertTrue(f("bar"))
        self.assertFalse(f("generation"))
        self.assertFalse(f("resource_provider_generation"))

    def test_get_field_filter_user_input(self):
        parsed_args = mock.Mock()
        parsed_args.fields = "foo,generation"

        f = provider_tree._get_field_filter(parsed_args)

        self.assertTrue(f("foo"))
        self.assertFalse(f("bar"))
        self.assertTrue(f("generation"))
        self.assertFalse(f("resource_provider_generation"))
