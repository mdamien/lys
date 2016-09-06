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
import html, types, keyword, sys

if sys.version_info >= (3,):
    unicode = str


__all__ = ['L', 'raw', 'LysExcept']


VOID_TAGS = 'area', 'base', 'br', 'col', 'embed', 'hr', \
    'img', 'input', 'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr'


class LyxException(Exception):
    pass


def render(node):
    if node is None:
        return ''

    if type(node) is RawNode:
        return node.content

    if type(node) in (tuple, list, types.GeneratorType):
        return ''.join(render(child) for child in node)

    if type(node) in (str, unicode):
        return html.escape(node)

    children_rendered = ''
    if node.children:
        children_rendered = render(node.children)

    attrs_rendered = ''
    if node.attrs:
        def render_attr(key, value):
            if not key or ' ' in key:
                raise LyxException('Invalid attribute name "{}"'.format(key))
            key = key.replace('class_', 'class')
            if value:
                if type(value) is RawNode:
                    value = str(value)
                else:
                    value = html.escape(value)
                return key + '="' + value + '"'
            return key
        attrs_rendered = ' ' + ' '.join(render_attr(k, node.attrs[k]) for k in sorted(node.attrs))

    if node.tag in VOID_TAGS:
        return '<{tag}{attrs}/>'.format(tag=node.tag, attrs=attrs_rendered)

    return '<{tag}{attrs}>{children}</{tag}>'.format(
        tag=node.tag, children=children_rendered, attrs=attrs_rendered)


class Node(object):
    """An HTML element"""
    def __init__(self, tag, attrs=None, children=None):
        self.tag = tag
        self.attrs = attrs
        self.children = children

    def __call__(self, _shortcut=None, **attrs):
        """
        Return a new node with the same tag but new attributes
        """
        def clean(k, v):
            if type(v) not in (str, unicode, RawNode):
                raise LyxException('Invalid attribute value "{}"'
                    ' for key "{}"'.format(v, k))
            # allow to use reserved keywords as: class_, for_,..
            if k[-1] == '_' and k[:-1] in keyword.kwlist:
                k = k[:-1]
            # replace all '_' with '-'
            return k.replace('_', '-')
        attrs = {clean(k, v): v for k, v in attrs.items()}

        if _shortcut:
            classes = _shortcut.split('.')
            # add #id if there is one
            if classes[0] and classes[0][0] == '#':
                attrs['id'] = classes[0][1:]
                classes = classes[1:]
            # add classes to the current class
            current_classes = attrs.get('class', '').split(' ')
            new_classes = [klass for klass in current_classes + classes if klass]
            if new_classes:
                attrs['class'] = ' '.join(new_classes)

        return Node(self.tag, attrs)

    # python 2 compat
    def __div__(self, children):
        return self.__truediv__(children)

    def __truediv__(self, children):
        """
        Mark a list or one node as the children of this node
        """
        if self.children is not None:
            # Block assigning two times the children to a node because
            # doing `a / b / c` is a counter-intuive and an easy-to-miss error
            # that is gonna assign two times the children of `a`
            raise LyxException('Can\'t re-assign the children of a node via /,'
                ' you have to use node.children instead.')
        if self.tag in VOID_TAGS:
            raise LyxException('<{}> can\'t have children nodes'.format(self.tag))
        if type(children) not in (tuple, list):
            children = (children,)
        self.children = children
        return self

    def __str__(self):
        return render(self)


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
