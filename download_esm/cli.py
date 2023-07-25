import click
import httpx
import pathlib
import re


@click.command()
@click.version_option()
@click.argument("package")
# Optional location argument
@click.argument("location", required=False, default=".")
def cli(package, location):
    """
    Download ESM modules from npm and jsdelivr

    Usage:

        download-esm '@observablehq/plot'

    This will download the ESM module for that npm library plus
    all of its dependencies and save them to the current directory.

    To save them to a different directory, pass that as an argument:

        download-esm '@observablehq/plot' ./js

    This will create the ./js directory if it does not already exist.
    """
    root = pathlib.Path(location)
    if not root.exists():
        root.mkdir(parents=True)
    if package.startswith("https://"):
        response = httpx.get(package)
        response.raise_for_status()
        code = response.text
    else:
        code = fetch_code(package)
    original_file = extract_original_file(code)
    path = simplify_path(original_file)
    # Rewrite code and save to path
    rewritten_code, captured_paths = rewrite_code(code)
    open(root / path, "w").write(rewritten_code)
    click.echo(path, err=True)
    # Do the same thing for all the captured paths, recursively
    to_fetch = set(tuple(p) for p in captured_paths.items())
    while to_fetch:
        path, simplified_path = to_fetch.pop()
        code = httpx.get("https://cdn.jsdelivr.net" + path).text
        rewritten_code, more_captured_paths = rewrite_code(code)
        open(root / simplified_path, "w").write(rewritten_code)
        click.echo(simplified_path, err=True)
        to_fetch.update(tuple(p) for p in more_captured_paths.items())


def fetch_code(package):
    url = f"https://cdn.jsdelivr.net/npm/{package}/+esm"
    response = httpx.get(url)
    response.raise_for_status()
    return response.text


def extract_original_file(content):
    #  Looks for Original file: /npm/@observablehq/plot@0.6.6/src/index.js
    pattern = r"Original file: (\/npm\/[^\s]+)"
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    else:
        raise Exception("Could not find original file")


def simplify_path(path):
    package_name, *version = path.split("/npm/")[1].rsplit("@", 1)
    version = "".join(version)
    version = version.split("/")[0]
    version = version.replace(".", "-")
    simplified_name = f"{package_name}-{version}.js"
    return simplified_name.replace("@", "").replace("/", "-")


def rewrite_code(code):
    pattern = r'(?P<keyword>import|export)\s*(?P<imports>\{?[^}]+?\}?)\s*from\s*"(?P<path>\/npm\/[^"]+)"'
    captured_paths = {}

    def replace_import(match):
        imports = match.group("imports")
        path = match.group("path")
        keyword = match.group("keyword")
        simplified_path = simplify_path(match.group("path"))
        captured_paths[path] = simplified_path
        return f'{keyword} {imports} from "./{simplified_path}";'

    rewritten_code = re.sub(pattern, replace_import, code)
    rewritten_code = remove_source_mapping_comments(rewritten_code)
    return rewritten_code, captured_paths


def remove_source_mapping_comments(code):
    pattern = r"\/\/#\s*sourceMappingURL=.*?\.map"
    cleaned_code = re.sub(pattern, "", code)
    return cleaned_code
