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
import html, types, keyword


__all__ = ['L', 'raw']


VOID_TAGS = 'area', 'base', 'br', 'col', 'embed', 'hr', \
    'img', 'input', 'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr'


def render(node):
    if node is None:
        return ''

    if type(node) is RawNode:
        return node.content

    if type(node) in (tuple, list, types.GeneratorType):
        return ''.join(render(child) for child in node)

    if type(node) == str:
        return html.escape(node)

    children_rendered = ''
    if node.children:
        children_rendered = render(node.children)

    attrs_rendered = ''
    if node.attrs:
        def render_attr(key, value):
            assert key
            assert ' ' not in key
            key = key.replace('class_', 'class')
            if value:
                if type(value) is not RawNode:
                    value = html.escape(value)
                else:
                    value = str(value)
                return key + '="' + value + '"'
            return key
        attrs_rendered = ' ' + ' '.join(render_attr(k, node.attrs[k]) for k in sorted(node.attrs))

    if node.tag in VOID_TAGS:
        assert not node.children
        return '<{tag}{attrs}/>'.format(tag=node.tag, attrs=attrs_rendered)

    return '<{tag}{attrs}>{children}</{tag}>'.format(
        tag=node.tag, children=children_rendered, attrs=attrs_rendered)


class Node:
    """An HTML element"""
    def __init__(self, tag, attrs=None, children=None):
        assert tag
        self.tag = tag
        self.attrs = attrs
        self.children = children

    def __call__(self, _shortcut=None, **attrs):
        """
        Return a new node with the same tag but new attributes
        """
        def clean(k):
            # allow to use reserved keywords as: class_, for_,..
            if k[-1] == '_' and k[:-1] in keyword.kwlist:
                k = k[:-1]
            # replace all '_' with '-'
            return k.replace('_', '-')
        attrs = {clean(k): v for k, v in attrs.items()}

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

    def __truediv__(self, children):
        """
        Mark a list or one node as the children of this node
        """
        assert self.tag not in VOID_TAGS
        if type(children) not in (tuple, list):
            children = (children,)
        self.children = children
        return self

    def __str__(self):
        return render(self)


class RawNode:
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
