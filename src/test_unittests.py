import unittest

from htmlnode import *
from textnode import *
from utils import *
from blocks import *
from main import *


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_neq(self):
        node = TextNode("This a text node", TextType.ITALIC, "http://www.google.com")
        node2 = TextNode("This a text node", TextType.CODE, "http://www.google.com")
        self.assertNotEqual(node, node2)
    
    def test_default_url(self):
        node = TextNode("asdfsdaf", TextType.TEXT)
        self.assertIsNone(node.url)

    def test_url(self):
        node = TextNode("asdfds", TextType.ITALIC, "http://www.google.com")
        self.assertIsNotNone(node.url)

    def test_url_neq(self):
        node = TextNode("This a text node", TextType.CODE, "http://www.googles.com")
        node2 = TextNode("This a text node", TextType.CODE, "http://www.google.com")
        self.assertNotEqual(node, node2)

class TestSplitNodes(unittest.TestCase):
    def test_single_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)

        expected_nodes = [
                            TextNode("This is text with a ", TextType.TEXT),
                            TextNode("code block", TextType.CODE),
                            TextNode(" word", TextType.TEXT),
                        ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_unmatched_del(self):
        node = TextNode("This is text with a **bold block` word", TextType.TEXT)
        
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_double_italics(self):
        node = TextNode("This is _text_ with _emphasized words_ to oooh and awww at", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)

        expected_nodes = [
                            TextNode("This is ", TextType.TEXT),
                            TextNode("text", TextType.ITALIC),
                            TextNode(" with ", TextType.TEXT),
                            TextNode("emphasized words", TextType.ITALIC),
                            TextNode(" to oooh and awww at", TextType.TEXT),
                        ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_bold_italics(self):
        node = TextNode("This is _text_ with _emphasized words_ to oooh and awww at", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)

        expected_nodes = [
                            TextNode("This is ", TextType.TEXT),
                            TextNode("text", TextType.ITALIC),
                            TextNode(" with ", TextType.TEXT),
                            TextNode("emphasized words", TextType.ITALIC),
                            TextNode(" to oooh and awww at", TextType.TEXT),
                        ]
        self.assertEqual(new_nodes, expected_nodes)
class TestNodeConversions(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is a BOLD text node", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.to_html(), "<b>This is a BOLD text node</b>")

    def test_link(self):
        node = TextNode("This is a link to something cool", TextType.LINK, "http://www.google.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.to_html(), '<a href="http://www.google.com">This is a link to something cool</a>')

    def test_image(self):
        node = TextNode("neat image here", TextType.IMAGE, "/cool.jpg")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.to_html(), '<img src="/cool.jpg" alt="neat image here"></img>')

    def test_code(self):
        node = TextNode("this is a 1337 code block", TextType.CODE, "/cool.jpg")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.to_html(), '<code>this is a 1337 code block</code>')

class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode("h1", "asdf", [], {})
        node2 = HTMLNode("h1", "asdf", [], {})
        self.assertEqual(node, node2)

    def test_h2p(self):
        props = {
                "href": "https://www.google.com",
                "target": "_blank",
            }
        node = HTMLNode(props=props)
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected)

    def test_default_tag(self):
        node = HTMLNode(value="ASDF", children=[], props={})
        self.assertIsNone(node.tag)

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_link(self):
        props = {
                "href": "https://www.google.com",
                "target": "_blank",
            }
        node = LeafNode("a", "gOOOOOgle", props=props)
        self.assertEqual(node.to_html(), '<a href="https://www.google.com" target="_blank">gOOOOOgle</a>')
    
    def test_leaf_html_b(self):
        node = LeafNode("b", "bold text here")
        self.assertEqual(node.to_html(), "<b>bold text here</b>")

    def test_leaf_html_i(self):
        node = LeafNode("i", "italics text here")
        self.assertEqual(node.to_html(), "<i>italics text here</i>")

    def test_parent_html_i(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        expected = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        self.assertEqual(node.to_html(),expected)

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_children_with_link(self):
        link_node = LeafNode("a", "boot dev", {"href": "https://www.boot.dev"})
        text_node = LeafNode(tag=None, value="Check out this website linked below.")
        parent_node = ParentNode("p",[text_node, link_node])
        self.assertEqual(
            parent_node.to_html(),
            '<p>Check out this website linked below.<a href="https://www.boot.dev">boot dev</a></p>'
        )

class TestExtractions(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
    )
        
    def test_split_links(self):
        node = TextNode(
            "This is text with a link to [bootdev](https://www.boot.dev) and another link to [google](http://www.google.com) and some more padding words.",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link to ", TextType.TEXT),
                TextNode("bootdev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and another link to ", TextType.TEXT),
                TextNode("google", TextType.LINK, "http://www.google.com"),
                TextNode(" and some more padding words.", TextType.TEXT)
            ],
            new_nodes,
    )
        
    def test_text_to_nodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected_nodes = [
                            TextNode("This is ", TextType.TEXT),
                            TextNode("text", TextType.BOLD),
                            TextNode(" with an ", TextType.TEXT),
                            TextNode("italic", TextType.ITALIC),
                            TextNode(" word and a ", TextType.TEXT),
                            TextNode("code block", TextType.CODE),
                            TextNode(" and an ", TextType.TEXT),
                            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                            TextNode(" and a ", TextType.TEXT),
                            TextNode("link", TextType.LINK, "https://boot.dev"),
                        ]
        self.assertEqual(nodes, expected_nodes)   

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line

- This is a list
- with items
            """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_p_block(self):
        block = "asdf  asdf  asdf  asdf  asdf"
        type = block_to_blocktype(block)
        self.assertEqual(type, BlockType.PARAGRAPH)

    def test_ul_block(self):
        block = "- item\n- next item\n- next next item"
        type = block_to_blocktype(block)
        self.assertEqual(type, BlockType.UNORDERED_LIST)

    def test_invalid_ul_block(self):
        block = "- item\n- next item\n3. next next item"
        type = block_to_blocktype(block)
        self.assertNotEqual(type, BlockType.UNORDERED_LIST)

    def test_ol_block(self):
        block = "1. item\n2. next item\n3. next next item\n4. fourth item"
        type = block_to_blocktype(block)
        self.assertEqual(type, BlockType.ORDERED_LIST)

    def test_invalid_ol_block(self):
        block = "1. item\n2. next item\n3. next next item\n4. fourth item\n7. Bad sequence"
        type = block_to_blocktype(block)
        self.assertNotEqual(type, BlockType.ORDERED_LIST)

    def test_code_block(self):
        block = "```\nsome code goes here\n```"
        type = block_to_blocktype(block)
        self.assertEqual(type, BlockType.CODE)

    def test_invalid_code_block(self):
        block = "```\nsome code goes here\n``"
        type = block_to_blocktype(block)
        self.assertNotEqual(type, BlockType.CODE)

    def test_quote_block(self):
        block = "> quote line 1\n> quote line 2\n> quote line 3"
        type = block_to_blocktype(block)
        self.assertEqual(type, BlockType.QUOTE)

    def test_invalid_quote_block(self):
        block = "> quote line 1\n> quote line 2\n> quote line 3\n line 4 without proper marking"
        type = block_to_blocktype(block)
        self.assertNotEqual(type, BlockType.QUOTE)

    def test_heading_block(self):
        block = "# heading 1 \n\n rest of block"
        type = block_to_blocktype(block)
        self.assertEqual(type, BlockType.HEADING)

    def test_invalid_heading_block(self):
        block = "####### heading 7 \n\n seven hashtags is too many!"
        type = block_to_blocktype(block)
        self.assertNotEqual(type, BlockType.HEADING)

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>")

    def test_h1(self):
        md = """
## This is a heading 2
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h2>This is a heading 2</h2></div>")

    def test_code(self):
        md = """
```
def hello_world():
    print("Hello, world!")
    # this is a comment
    return None
```
"""    
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html,
                         "<div><pre><code>def hello_world():\n    print(\"Hello, world!\")\n    # this is a comment\n    return None\n</code></pre></div>")

    def test_quote_block(self):
        md = """
> this is a blockquote
> it can span multiple lines
> and contain **bold** and _italic_ text
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html,
                         "<div><blockquote>this is a blockquote it can span multiple lines and contain <b>bold</b> and <i>italic</i> text</blockquote></div>")

    def test_ul(self):
        md = """
- Item 1
- Item 2 with **bold**
- Item 3 with _italic_
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html,
                         "<div><ul><li>Item 1</li><li>Item 2 with <b>bold</b></li><li>Item 3 with <i>italic</i></li></ul></div>")

    def test_ol(self):
        md = """
1. Item 1
2. Item 2 with **bold**
3. Item 3 with _italic_
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html,
                         "<div><ol><li>Item 1</li><li>Item 2 with <b>bold</b></li><li>Item 3 with <i>italic</i></li></ol></div>")

    def test_extract_title(self):
        md = "# This is my title"
        expected = "This is my title"
        actual = extract_title(md)
        self.assertEqual(actual, expected)

    def test_extract_title_h2(self):
        md = "## This is my h2 title"
        with self.assertRaises(Exception):
            extract_title(md)
            
    def test_extract_title_nonheader(self):
        md = "> This is my list item attempting to be a title"
        with self.assertRaises(Exception):
            extract_title(md)

if __name__ == "__main__":
    unittest.main()

