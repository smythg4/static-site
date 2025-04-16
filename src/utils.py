from htmlnode import *
from textnode import *
import re

def extract_markdown_images(text: str):
    # ![rick roll](https://i.imgur.com/aKaOqIh.gif)
    alt_text_regex = r"\!\[.*?\]"
    url_regex = r"\(.*?\)"
    alt_texts = list(map(lambda s: s[2:-1],re.findall(alt_text_regex, text)))
    urls = list(map(lambda s: s[1:-1],re.findall(url_regex, text)))
    return list(zip(alt_texts, urls))

def extract_markdown_links(text: str):
    # [to boot dev](https://www.boot.dev)
    desc_regex = r"\[.*?\]"
    url_regex = r"\(.*?\)"
    descs = list(map(lambda s: s[1:-1], re.findall(desc_regex, text)))
    urls = list(map(lambda s: s[1:-1], re.findall(url_regex, text)))
    return list(zip(descs, urls))

def text_node_to_html_node(text_node: TextNode):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
        case _:
            raise Exception("Invalid text type provided")
        
def split_nodes_delimiter(old_nodes: list, delimiter: str, text_type: TextType):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            if delimiter in node.text:
                first_point = node.text.find(delimiter)
                second_point = node.text.find(delimiter, first_point + len(delimiter))
                if second_point == -1:
                    raise Exception("missing trailing delimeter on node")
                new_nodes.append(TextNode(node.text[:first_point], TextType.TEXT))
                new_nodes.append(TextNode(node.text[first_point + len(delimiter):second_point], text_type))
                new_nodes.extend(
                    split_nodes_delimiter([TextNode(node.text[second_point + len(delimiter):], 
                                                    TextType.TEXT)], 
                                                    delimiter, 
                                                    text_type))
            else:
                new_nodes.append(node)
    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if not node.text:
            continue
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        images = extract_markdown_images(node.text)
        if len(images) < 1:
            new_nodes.append(node)
            continue
        alt_text, url = images[0]
        sections = node.text.split(f"![{alt_text}]({url})",1)
        if sections[0]:
            new_nodes.append(TextNode(sections[0], TextType.TEXT))
        new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
        if sections[1]:
            new_nodes.extend(split_nodes_image([TextNode(sections[1], TextType.TEXT)]))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if not node.text:
            continue
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        links = extract_markdown_links(node.text)
        if len(links) < 1:
            new_nodes.append(node)
            continue
        title, url = links[0]
        sections = node.text.split(f"[{title}]({url})",1)
        if sections[0]:
            new_nodes.append(TextNode(sections[0], TextType.TEXT))
        new_nodes.append(TextNode(title, TextType.LINK, url))
        if sections[1]:
            new_nodes.extend(split_nodes_link([TextNode(sections[1], TextType.TEXT)]))
    return new_nodes

def text_to_textnodes(text: str):
    node = TextNode(text, TextType.TEXT)
    nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
