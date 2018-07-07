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

import graphviz


def to_dot(tree_root, id_selector):
    """Convert a TreeNode to graphviz dot format

    :param tree_root: the root of the tree
    :param id_selector: TreeNode -> scalar function that selects provides the
                        unique id of the node
    :return: a dot formatted string
    """
    dot = graphviz.Digraph(node_attr={'shape': 'plaintext'})

    def add_node(node):
        dot.node(id_selector(node), _get_attr_html(node.data))

    def add_edges(node):
        for child in node.children:
            dot.edge(id_selector(node), id_selector(child))

    tree_root.walk(add_node)
    tree_root.walk(add_edges)
    return dot.source


def _get_attr_html(data_dict):
    html_str = _get_html_dict(data_dict)
    return '<' + html_str + '>'


def _get_html_scalar(scalar):
    return '<TD  ALIGN="LEFT">%s</TD>' % scalar


def _get_html_dict(a_dict):
    if not a_dict:
        return '{}'

    attrs = ('<TABLE BORDER="0" CELLBORDER="1" '
             'CELLSPACING="0" CELLPADDING="4">\n')
    for key, value in a_dict.items():
        attrs += _get_html_key_value(key, value)
    attrs += '</TABLE>\n'
    return attrs


def _get_html_value(value):
    if isinstance(value, list):
        if not value:
            return _get_html_scalar('[]')

        # assuming that list items are scalars
        return _get_html_scalar('<BR/>'.join(value))
    elif isinstance(value, dict):
        return _get_html_scalar(_get_html_dict(value))
    else:  # assuming scalar
        return _get_html_scalar(value)


def _get_html_key_value(key, value):
    # assuming that the key is scalar
    return '<TR>' + _get_html_scalar(key) + _get_html_value(value) + '</TR>\n'
