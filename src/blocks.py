from enum import Enum
import re
from textnode import *
from htmlnode import *
from utils import *

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def check_all_lines(pattern: str):
    def checker(block: str):
        lines = block.split('\n')
        return all(re.match(pattern, line) for line in lines)
    return checker

def is_quote(block: str):
    quote_re = r"^>.*"
    return check_all_lines(quote_re)(block)

def is_ul(block: str):
    ul_re = r"^-\s.*"
    return check_all_lines(ul_re)(block)

def is_heading(block: str):
    headers_re = r"^\#{1,6}\s.*"
    return re.match(headers_re, block) is not None

def is_code(block: str):
    lines = block.split('\n')
    return len(lines) >= 2 and lines[0] == "```" and lines[-1] == "```"

def is_ol(block: str):
    lines = block.split('\n')
    for i, line in enumerate(lines):
        expected = i+1
        if not line.startswith(f"{expected}. "):
            return False
    return True

def block_to_blocktype(block: str):
    if is_heading(block):
        return BlockType.HEADING
    elif is_code(block):
        return BlockType.CODE
    elif is_quote(block):
        return BlockType.QUOTE
    elif is_ol(block):
        return BlockType.ORDERED_LIST
    elif is_ul(block):
        return BlockType.UNORDERED_LIST
    else:
        return BlockType.PARAGRAPH
    
def markdown_to_blocks(markdown: str):
    blocks = markdown.split('\n\n')
    new_blocks = []
    for block in blocks:
        block = block.strip()
        if block:
            new_blocks.append(block)
    return new_blocks

def extract_heading_content(block: str):
    pattern = r'^#+\s+(.*)'
    match = re.match(pattern, block)
    if match:
        return match.group(1)
    return block

def extract_code_content(block: str):
    assert block_to_blocktype(block) == BlockType.CODE, "Must be a code block to get code content"
    return "\n".join(block.split('\n')[1:-1]) + '\n'

def extract_quote_content(block: str):
    assert block_to_blocktype(block) == BlockType.QUOTE, "Must be a quote block to get quote content"
    lines = block.split('\n')
    result = []
    for line in lines:
        result.append(line[2:].strip())
    return ' '.join(result)

def extract_ul_nodes(block: str):
    assert block_to_blocktype(block) == BlockType.UNORDERED_LIST, "Must be an unordered list block to get li items"
    list_items = []
    lines = block.split('\n')

    for line in lines:
        if not line.strip():
            continue

        content = line.strip()[2:].strip() # remove leading "- "
        child_nodes = text_to_children(content)
        li_node = ParentNode(tag="li", children=child_nodes)
        list_items.append(li_node)

    return list_items

def extract_ol_nodes(block: str):
    assert block_to_blocktype(block) == BlockType.ORDERED_LIST, "Must be an ordered list block to get li items"
    list_items = []
    lines = block.split('\n')

    for line in lines:
        if not line.strip():
            continue

        content = line.strip()[3:].strip() # remove leading "1. "
        child_nodes = text_to_children(content)
        li_node = ParentNode(tag="li", children=child_nodes)
        list_items.append(li_node)

    return list_items

def get_heading_block_tag(block: str):
    assert block_to_blocktype(block) == BlockType.HEADING, "Must be heading block to get heading tag"
    pattern = r'^(#+)'
    match = re.match(pattern, block)
    num = 1
    if match:
        num = len(match.group(1))
    return f"h{num}"

def text_to_children(text: str):
    text_nodes = text_to_textnodes(text)
    html_nodes = []
    for tnode in text_nodes:
        html_nodes.append( text_node_to_html_node(tnode) )
    return html_nodes

def markdown_to_html_node(markdown: str):
    blocks = markdown_to_blocks(markdown)
    nodes = []
    for block in blocks:
        block_type = block_to_blocktype(block)
        match block_type:
            case BlockType.PARAGRAPH:
                clean_block = block.replace('\n',' ')
                child_nodes = text_to_children(clean_block)
                this_node = ParentNode(tag="p",children=child_nodes)
                nodes.append(this_node)
            case BlockType.HEADING:
                tag = get_heading_block_tag(block)
                child_nodes = text_to_children(extract_heading_content(block))
                this_node = ParentNode(tag=tag, children=child_nodes)
                nodes.append(this_node)
            case BlockType.CODE:
                content = extract_code_content(block)
                code_node = LeafNode("code", content)
                pre_node = ParentNode(tag="pre", children=[code_node])
                nodes.append(pre_node)
            case BlockType.QUOTE:
                quote_content = extract_quote_content(block)
                child_nodes = text_to_children(quote_content)
                this_node = ParentNode(tag="blockquote", children=child_nodes)
                nodes.append(this_node)
            case BlockType.UNORDERED_LIST:
                li_nodes = extract_ul_nodes(block)
                ul_node = ParentNode(tag="ul", children=li_nodes)
                nodes.append(ul_node)
            case BlockType.ORDERED_LIST:
                li_nodes = extract_ol_nodes(block)
                ol_node = ParentNode(tag="ol", children=li_nodes)
                nodes.append(ol_node)
            case _:
                raise Exception("invalid block type")
    return ParentNode(tag="div", children=nodes)