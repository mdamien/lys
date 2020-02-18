from unittest import TestCase

from lys import L, raw, LysException

class Test(TestCase):
    def test_hello_world(self):
        self.assertEqual(str(L.h1 / 'hello world'), '<h1>hello world</h1>')

    def test_attributes(self):
        self.assertEqual(str(L.h1(class_='hello') / 'world'),
            '<h1 class="hello">world</h1>')
        self.assertEqual(str(L.input(id='hello', value='world')),
            '<input id="hello" value="world"/>')
        self.assertEqual(str(L.input(what='')),
            '<input what/>')
        self.assertEqual(str(L.input(what=None)),
            '<input what/>')
        self.assertEqual(str(L.input(data_trigger='666')),
            '<input data-trigger="666"/>')

    def test_escaping(self):
        self.assertEqual(str(L.div(id='hello & ; " \'')),
            '<div id="hello &amp; ; &quot; &#x27;"></div>')
        self.assertEqual(str(L.h1 / '<script>alert("h4x0r")</script>'),
            '<h1>&lt;script&gt;alert(&quot;h4x0r&quot;)&lt;/script&gt;</h1>')
        self.assertEqual(str(L.button(onclick=raw('alert(\'follow the rabbit\')'))),
            '<button onclick="alert(\'follow the rabbit\')"></button>')

    def test_children(self):
        self.assertEqual(str(L.body / (
            L.ul / (
                L.li / 'One',
                None,
                L.li / 'Two',
                L.li / 'Three',
                ''
            )
        )), '<body><ul><li>One</li><li>Two</li><li>Three</li></ul></body>')

    def test_shortcut(self):
        self.assertEqual(str(L.span('.hello')),
            '<span class="hello"></span>')
        self.assertEqual(str(L.span('.hello.world')),
            '<span class="hello world"></span>')
        self.assertEqual(str(L.span('#world.hello')),
            '<span class="hello" id="world"></span>')
        self.assertEqual(str(L.span('#what')),
            '<span id="what"></span>')

    def test_double_division(self):
        self.assertEqual(
            str(L.a / L.b / L.c / L.d),
            '<a><b><c><d></d></c></b></a>'
        )
        self.assertEqual(
            str(L.a / L.b / 'C'),
            '<a><b>C</b></a>'
        )

    def test_raise(self):
        # no children for void tags
        with self.assertRaises(LysException):
            L.br / L.p
        
        # only str or raw() attributes values
        with self.assertRaises(LysException):
            L.button(data_id=123)

        # invalid shortcuts
        with self.assertRaises(LysException):
            L.span('.foo.hello world')
        with self.assertRaises(LysException):
            L.span(',hello')
        
