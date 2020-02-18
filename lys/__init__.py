"""HTML templating with no shame

>>> from lys import L
>>> str(L.h1 / 'hello world')
'<h1>hello world</h1>'
>>> str(L.hr('.thick')))
'<hr class='thick'/>'
>>> str(L.button(onclick='reverse_entropy()'))
'<button onclick='reverse_entropy()'/>'
>>> str(L.ul / (
    L.li / 'One',
    L.li / 'Two',
))
'<ul><li>One</li><li>Two</li></ul>'
"""
from __future__ import unicode_literals
import html, types, keyword, sys, re


__all__ = [
    'L',
    'LysException',
    'raw',
    'render',
    'Node',
]


VOID_TAGS = [
    'area', 'base', 'br', 'col', 'embed', 'hr',
    'img', 'input', 'keygen', 'link', 'meta',
    'param', 'source', 'track', 'wbr'
]


class LysException(Exception):
    """Base exception class for all Lys related errors"""


def render_attr(key, value):
    if not key or ' ' in key:
        raise LysException('Invalid attribute name "{}"'.format(key))
    key = key.replace('class_', 'class')
    if value:
        if type(value) is RawNode:
            value = str(value)
        else:
            value = html.escape(value)
        return key + '="' + value + '"'
    return key


def render(node):
    """Render a node or a node list to HTML"""
    if node is None:
        return ''

    if type(node) is RawNode:
        return node.content

    if type(node) in (tuple, list, types.GeneratorType):
        return ''.join(render(child) for child in node)

    if type(node) is str:
        return html.escape(node)

    children_rendered = ''
    if node.children:
        children_rendered = render(node.children)

    attrs_rendered = ''
    if node.attrs:
        attrs_rendered = ' ' + ' '.join(
            render_attr(k, node.attrs[k]) for k in sorted(node.attrs)
        )

    if node.tag in VOID_TAGS:
        return '<{tag}{attrs}/>'.format(tag=node.tag, attrs=attrs_rendered)

    return '<{tag}{attrs}>{children}</{tag}>'.format(
        tag=node.tag, children=children_rendered, attrs=attrs_rendered)


class Node(object):
    """An HTML node"""
    def __init__(self, tag, attrs=None, children=None):
        self.tag = tag
        self.attrs = attrs
        self.children = children

    def __call__(self, _shortcut=None, **attrs):
        """Return a new node with the same tag but new attributes"""
        def clean(k, v):
            if v and type(v) not in (str, RawNode):
                raise LysException('Invalid attribute value "{}"'
                    ' for key "{}"'.format(v, k))
            # allow to use reserved keywords as: class_, for_,..
            if k[-1] == '_' and k[:-1] in keyword.kwlist:
                k = k[:-1]
            # replace all '_' with '-'
            return k.replace('_', '-')
        attrs = {clean(k, v): v for k, v in attrs.items()}

        # process given shorcut strings like '#my_id.a_class.another_class'
        if _shortcut:
            def raise_if_bad_name(name, type='class'):
                # TODO: regex to verify if valid class name
                if ' ' in name or '.' in name or ',' in name:
                    raise LysException('"{}" is an invalid {} name'.format(name, type))
                return name
            classes = _shortcut.split('.')
            # add #id if there is one
            if classes[0] and classes[0][0] == '#':
                attrs['id'] = raise_if_bad_name(classes[0][1:], 'id')
                classes = classes[1:]
            # add classes to the current class
            current_classes = attrs.get('class', '').split(' ')
            new_classes = [raise_if_bad_name(klass) for klass in current_classes + classes if klass]
            if new_classes:
                attrs['class'] = ' '.join(new_classes)

        return Node(self.tag, attrs)

    # python 2 compat
    def __div__(self, children):
        return self.__truediv__(children)

    def __truediv__(self, children):
        """Mark a list or one node as the children of this node"""
        if self.tag in VOID_TAGS:
            raise LysException('<{}> can\'t have children nodes'.format(self.tag))
        if self.children and len(self.children) == 1:
            self.children = (self.children[0] / children,)
        else:
            if type(children) not in (tuple, list):
                children = (children,)
            self.children = children
        return self

    def __str__(self):
        return render(self)

    def __repr__(self):
        return 'Node(tag={}, attrs={}, children={})'.format(self.tag,
                    self.attrs, self.children)


class RawNode(object):
    """Node marked as already escaped"""
    def __init__(self, content):
        self.content = content

    def __str__(self):
        return self.content


def raw(content):
    """Mark a string as already escaped"""
    return RawNode(content)


class _L:
    def __getattr__(self, tag):
        return Node(tag)
L = _L()
