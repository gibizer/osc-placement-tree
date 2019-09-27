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


class TestProviderTree(base.TestBase):
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

    def test_get_uuid_form_name_or_uuid_with_uuid(self):
        client = mock.Mock()
        uuid = "abdc6d98-c2a3-4364-9656-562cfbbb0f3f"

        result = provider_tree._get_uuid_form_name_or_uuid(client, uuid)

        self.assertEqual(uuid, result)
        client.get.assert_not_called()

    def test_get_uuid_form_name_or_uuid_with_name(self):
        client = mock.Mock()
        uuid = "abdc6d98-c2a3-4364-9656-562cfbbb0f3f"
        name = "devstack"
        client.get.return_value = {
            "resource_providers": [
                {"name": name, "uuid": uuid},
                {"name": "another", "uuid": "another-uuid"},
            ]
        }

        result = provider_tree._get_uuid_form_name_or_uuid(client, name)

        self.assertEqual(uuid, result)
        client.get.assert_called_once_with("/resource_providers")

    def test_get_uuid_form_name_or_uuid_with_name_not_exists(self):
        client = mock.Mock()
        name = "devstack"
        client.get.return_value = {
            "resource_providers": [{"name": "another", "uuid": "another-uuid"}]
        }

        self.assertRaises(
            ValueError, provider_tree._get_uuid_form_name_or_uuid, client, name
        )

        client.get.assert_called_once_with("/resource_providers")
