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

    if destpath.exists() and destpath == 'public':
        shutil.rmtree(destpath)
        print(f"Deleting and recreating directory and contents of: {destpath}")
        destpath.mkdir()

    elif not destpath.exists() and not sourcepath.is_file():
        destpath.mkdir()
        #os.mkdir(destpath)
        
    if sourcepath.is_file():
        print(f"Found file at path: {sourcepath}")
        print(f"Copying it to: {destpath}")
        shutil.copy(sourcepath, destpath)
    else:
        child_paths = sourcepath.iterdir()
        for path in child_paths:
            new_source_path = sourcepath / path.name
            new_dest_path = destpath / path.name
            print(f"Child Path: {path}")
            print(f"New Source Path: {new_source_path}")
            print(f"New Dest Path: {new_dest_path}")
            if not new_source_path.is_file():
                new_dest_path.mkdir()
            clean_and_copy(new_source_path, new_dest_path)

def extract_title(markdown: str):
    assert get_heading_block_tag(markdown) == "h1", "title must be of type <h1>"
    return extract_heading_content(markdown)

def generate_page(from_path: str, template_path: str, dest_path: str, basepath: str):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path,"r") as source:
        source_text = source.read()
    with open(template_path,"r") as template:
        template_text = template.read()
    source_html = markdown_to_html_node(source_text).to_html()
    page_title = extract_title(source_text)
    
    page_html = template_text.replace('{{ Title }}', page_title).replace('{{ Content }}',source_html)
    final_html = page_html.replace('href="/',f'href="{basepath}/').replace('src="/',f'src="{basepath}/')
    if os.path.isfile(dest_path):
        print(f"{dest_path} file already exists.")
    else:
        print(f"{dest_path} isn't a file. Creating it now...")
        with open(dest_path, "w") as file:
            file.write(final_html)
        print(f"{dest_path} file created.")

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
        return Path(sys.argv[1])
    else:
        return Path(default)

def main():
    base_path = get_sys_args()
    print(f"Base Path: {base_path.name}")
    clean_and_copy(base_path/'static',base_path/'public')
    #generate_page('content/index.md', 'template.html', 'public/index.html')
    generate_page_recursive('content/', 'template.html', 'public/', base_path)

main()