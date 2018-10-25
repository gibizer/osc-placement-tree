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
import operator


def _get_attr_html(data_dict, field_filter):
    html_str = _get_html_dict(data_dict, field_filter)
    return "<" + html_str + ">"


def _get_html_scalar(scalar):
    return '<TD  ALIGN="LEFT" BALIGN="LEFT">%s</TD>' % scalar


def _get_html_dict(a_dict, field_filter, header=None):
    if not a_dict:
        return "{}"

    attrs = (
        '<TABLE BORDER="0" CELLBORDER="1" '
        'CELLSPACING="0" CELLPADDING="4">\n'
    )
    if header:
        attrs += (
            '<TR BORDER="0" CELLBORDER="0">'
            '<TD ALIGN="LEFT" BALIGN="LEFT" BORDER="0">'
            "{header}"
            "</TD></TR>\n"
        ).format(header=header)
    for key, value in sorted(a_dict.items(), key=operator.itemgetter(0)):
        if field_filter(key):
            attrs += _get_html_key_value(key, value, field_filter)
    attrs += "</TABLE>\n"
    return attrs


def _get_html_value(value, field_filter):
    if isinstance(value, list):
        if not value:
            return _get_html_scalar("[]")

        # assuming that list items are scalars
        return _get_html_scalar("<BR/>".join(value))
    elif isinstance(value, dict):
        return _get_html_scalar(_get_html_dict(value, field_filter))
    else:  # assuming scalar
        return _get_html_scalar(value)


def _get_html_key_value(key, value, field_filter):
    # assuming that the key is scalar
    return (
        "<TR>"
        + _get_html_scalar(key)
        + _get_html_value(value, field_filter)
        + "</TR>\n"
    )
