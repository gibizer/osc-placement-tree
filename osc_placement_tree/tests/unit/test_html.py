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

from osc_placement_tree import html
from osc_placement_tree.tests import base


class TestHtml(base.TestBase):
    @mock.patch("osc_placement_tree.html._get_html_key_value")
    def test_get_html_dict_sorts_fields(self, mock_get_html_key_value):
        mock_get_html_key_value.side_effect = ["", "", "", "", ""]
        a_dict = {"foo": 1, "bar": 2, "foobar": 3, "zero": 4, "apple": 5}
        filter = lambda _: True
        html._get_html_dict(a_dict, filter)
        self.assertEqual(
            [
                mock.call("apple", 5, filter),
                mock.call("bar", 2, filter),
                mock.call("foo", 1, filter),
                mock.call("foobar", 3, filter),
                mock.call("zero", 4, filter),
            ],
            mock_get_html_key_value.mock_calls,
        )
