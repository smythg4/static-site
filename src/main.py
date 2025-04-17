from textnode import *
from htmlnode import *
from utils import *
from blocks import *
import os
import shutil
from pathlib import Path
import sys

def clean_and_copy(sourcepath: Path, destpath: Path):
    assert sourcepath.exists(), f"Source path {sourcepath} does not exist"

    # see if the destination path exists, if not, make it along with parent dirs
    if not destpath.exists():
        destpath.mkdir(parents=True)
        
    if sourcepath.is_file():
        print(f"Copying file: {sourcepath} -> {destpath}")
        shutil.copy(sourcepath, destpath)
    else:
        print(f"Copying directory contents: {sourcepath} -> {destpath}")
        child_paths = sourcepath.iterdir()
        for path in child_paths:
            new_source_path = sourcepath / path.name
            new_dest_path = destpath / path.name
            if new_source_path.is_dir():
                # for directories, ensure directory exists
                if not new_dest_path.exists():
                    new_dest_path.mkdir()
                clean_and_copy(new_source_path, new_dest_path)
            else:
                # for files, copy them directly
                shutil.copy(new_source_path, new_dest_path)

def extract_title(markdown: str):
    assert get_heading_block_tag(markdown) == "h1", "title must be of type <h1>"
    return extract_heading_content(markdown)

def generate_page(from_path: str, template_path: str, dest_path: str, basepath: str):
    print(f"Generating page {from_path} -> {dest_path} using {template_path}")
    with open(from_path,"r") as source:
        source_text = source.read()
    with open(template_path,"r") as template:
        template_text = template.read()
    source_html = markdown_to_html_node(source_text).to_html()
    page_title = extract_title(source_text)
    
    page_html = template_text.replace('{{ Title }}', page_title).replace('{{ Content }}',source_html)
    
    basepath = basepath.rstrip('/')
    if basepath and basepath != '/':
        final_html = page_html.replace('href="/',f'href="{basepath}/').replace('src="/',f'src="{basepath}/')
    else:
        final_html = page_html
        
    if os.path.isfile(dest_path):
        print(f"{dest_path} file already exists.")
    else:
        print(f"{dest_path} isn't a file. Creating it now...")

    with open(dest_path, "w") as file:
        file.write(final_html)

def generate_page_recursive(dir_path_content, template_path, dest_dir_path, basepath: str):
    content_path = Path(dir_path_content)
    temp_path = Path(template_path)
    dest_path = Path(dest_dir_path)

    for path in content_path.iterdir():
        new_dest_path = dest_path / path.name
        if path.is_dir():
            print(f"Path: {path}")
            print(f"Parent Path: {path.parent}")
            print(f"Making Dest Path: {new_dest_path}")
            new_dest_path.mkdir()
            print(new_dest_path.exists())
            generate_page_recursive(path, template_path, new_dest_path, basepath)
        elif path.is_file() and str(path).endswith('.md'):
            print(f"Found markdown file: {path}")
            dest_filepath = new_dest_path.parent / (new_dest_path.stem + '.html')
            print(f"Generating new file: {dest_filepath}")
            generate_page(path, temp_path, dest_filepath, basepath)

def get_sys_args(default='/'):
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        return default

def main():
    base_path = get_sys_args()
    print(f"Base Path: {base_path}")
    output_dir = Path('docs')

    # make sure output directory exists
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    # copy static files
    static_dir = Path('static')
    if static_dir.exists():
        clean_and_copy(static_dir, output_dir/'static')

    generate_page_recursive('content', 'template.html', output_dir, base_path)

main()