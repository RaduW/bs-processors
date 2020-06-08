"""
Transforms example files into markdown files

"""
from collections import namedtuple
from enum import Enum
from typing import Mapping, List, Optional
import os
from os import path
from os import walk
import re
import logging

_log = logging.getLogger("bs-processors")

start_markdown = re.compile(r"\s*(\"\"\"|''')\s*")
section_start = re.compile(r"\s*#\s*SECTION_START\s*(?P<name>[^ \t\r\n]+)", re.IGNORECASE)
section_end = re.compile(r"\s*#\s*SECTION_END", re.IGNORECASE)
exclude_start = re.compile(r"\s*#\s*EXCLUDE_START", re.IGNORECASE)
exclude_end = re.compile(r"\s*#\s*EXCLUDE_END", re.IGNORECASE)
inject_file = re.compile(r"\s*{{\s*INJECT_FILE\s+(?P<code_type>[^ \t\r\n]+)\s+(?P<name>[^ \t]+)\s*}}", re.IGNORECASE)
inject_code = re.compile(r"\s*{{\s*INJECT_CODE\s+(?P<name>[^ \t]+)\s*}}", re.IGNORECASE)
no_processing = re.compile(r"(#\s*NO_PROCESSING)|({{\s*NO_PROCESSING\s*}})", re.IGNORECASE)

class ReferenceType(Enum):
    Internal = {'id': "internal"}
    External = {'id': "external"}


CodeReference = namedtuple("CodeReference", "line, type, name, code_type")


def _load_file(directory, file_name) -> List[str]:
    try:
        file_name = path.abspath(path.join(directory, file_name))
        with open(file_name, 'rt') as f:
            return f.readlines()
    except:
        return []


def is_processing(lines: List[str]):
    for line in lines:
        if no_processing.match(line):
            return False
    return True



def extract_example(file_name: str) -> List[str]:
    directory, f_name = path.split(file_name)
    content = _load_file(directory, f_name)
    if not is_processing(content):
        return None
    markdown = get_raw_markdown(content)
    code_segments = get_code_segments(content)
    references = get_references(markdown)
    external_references = load_external_references(directory, references)
    full_markdown = hydrate_markdown(markdown, references, code_segments, external_references)
    return full_markdown


def hydrate_markdown(markdown, references, code_segments, external_references) -> List[str]:
    """

    >>> markdown = ["line 1", "line 2", "{{ INJECT_FILE /abc/def.html }}",
    ... "line 3", "{{ INJECT_CODE code_1}}", "line 4"]
    >>> references = [CodeReference(2, ReferenceType.External, "abc/def.html", 'html'),
    ... CodeReference(4, ReferenceType.Internal, "code1", 'python')]
    >>> code_segments = { 'code1': ["code line 1", "code line 2"]}
    >>> external_refs = { 'abc/def.html': ["html line 1", "html line 2"]}
    >>> hydrate_markdown( markdown, references, code_segments, external_refs)
    ['line 1', 'line 2', '\\n', '```html\\n', '\\n', 'html line 1', 'html line 2', '\\n```\\n', 'line 3', '\\n', \
'```python\\n', '\\n', 'code line 1', 'code line 2', '\\n```\\n', 'line 4']

    """
    if len(references) == 0:
        return markdown  # no reference to replace
    next_reference_idx = 0
    past_last_reference = False
    ret_val = []
    for idx, line in enumerate(markdown):
        if past_last_reference:
            ret_val.append(line)
        elif idx == references[next_reference_idx].line:
            reference = references[next_reference_idx]
            if reference.type == ReferenceType.Internal:
                code = code_segments.get(reference.name, [])
            else:
                code = external_references.get(reference.name, [])
            ret_val += to_code_snippet(code, reference.code_type)

            next_reference_idx += 1
            if next_reference_idx >= len(references):
                past_last_reference = True
        else:
            ret_val.append(line)
    return ret_val


def to_code_snippet(lines: List[str], code_type: Optional[str] = None) -> List[str]:
    ret_val = []
    if len(lines) == 0:
        return ret_val
    code_type = code_type if code_type is not None else ''
    ret_val += ["\n", f"```{code_type}\n", "\n"]
    ret_val += lines
    ret_val.append("\n```\n")
    return ret_val


def load_external_references(directory, references: List[CodeReference]) -> Mapping[str, List[str]]:
    ret_val = {}
    for ref in references:
        if ref.type == ReferenceType.External:
            content = _load_file(directory, ref.name)
            ret_val[ref.name] = content
    return ret_val


def get_references(text: List[str]) -> List[CodeReference]:
    """
    Extracts references from markdown lines
    >>> text = [
    ... " some random text",
    ... " {{ inject_file html samples/some_file_name.html }} ",
    ... " some more random text {{ INJECT garbage }} ",
    ... " {{ INJECT_code main_code_example }}  ",
    ... " {{ INJECT_NONSENSE nonsense }}",
    ... ]
    >>> refs = get_references( text)
    >>> [ (r.line, r.type.value['id'], r.name) for r in refs]
    [(1, 'external', 'samples/some_file_name.html'), (3, 'internal', 'main_code_example')]

    """
    ret_val = []
    if text is None:
        return ret_val
    for line_idx, line in enumerate(text):
        for (ref_type, regex) in [(ReferenceType.External, inject_file), (ReferenceType.Internal, inject_code)]:
            match = regex.match(line)
            if match is not None:
                if ref_type == ReferenceType.External:
                    code_type = match.group('code_type')
                else:
                    code_type = 'python'

                ret_val.append(CodeReference(line=line_idx, type=ref_type, name=match.group('name'),
                                             code_type=code_type))
                continue

    return ret_val


def get_raw_markdown(file_content: List[str]) -> List[str]:
    """

    >>> file_content = ["'''","Some markdown","And another line","'''","Not markdown" ]
    >>> get_raw_markdown(file_content)
    ['Some markdown', 'And another line']

    """
    start = False
    markdown = []
    stop_marker = None
    for line in file_content:
        if stop_marker is not None and stop_marker in line:
            return markdown
        if start == True:
            markdown.append(line)
        if start_markdown.match(line):
            start = True
            stop_marker = line.strip()


class ParseMode(Enum):
    InitialMarkdown = 1
    LookingForCodeSegment = 2
    InsideCodeSegment = 3
    InsideExcludedCode = 4


def get_code_segments(file_content: List[str]) -> Mapping[str, List[str]]:
    """

    >>> lines = [
    ... "'''", "md1", "'''", "code1", "# SECTION_StarT xxx", "code 2", "code 3",
    ... "# EXCluDE_START" , "code 4", " # SECTION_START yyy", "code 5" , "# EXCLUDE_START", "code 7",
    ... "# exclude_end", 'code 8', '# SECTION_END', 'code 9', '# EXCLUDE_START', 'code 10'
    ... ]
    >>> segments = get_code_segments(lines)
    >>> len(segments)
    2
    >>> segments['xxx']
    ['code 2', 'code 3']
    >>> segments['yyy']
    ['code 5', 'code 8']
    """
    mode = ParseMode.InitialMarkdown
    code_segments = {}
    current_code_segment = []
    current_code_name = None
    matched_markdown_markers = 0
    for line in file_content:
        if mode == ParseMode.InitialMarkdown:
            if start_markdown.match(line):
                matched_markdown_markers += 1
            if matched_markdown_markers == 2:
                mode = ParseMode.LookingForCodeSegment
        elif mode == ParseMode.LookingForCodeSegment:
            match = section_start.match(line)
            if match is not None:
                current_code_name = match.group('name')
                mode = ParseMode.InsideCodeSegment
        elif mode == ParseMode.InsideCodeSegment:
            match = section_end.match(line)
            if match is not None:
                code_segments[current_code_name] = current_code_segment
                current_code_segment = []
                current_code_name = None
                mode = ParseMode.LookingForCodeSegment
                continue
            match = exclude_start.match(line)
            if match is not None:
                mode = ParseMode.InsideExcludedCode
                continue
            match = section_start.match(line)
            if match is not None:
                code_segments[current_code_name] = current_code_segment
                current_code_segment = []
                current_code_name = match.group('name')
                continue
            current_code_segment.append(line)
        elif mode == ParseMode.InsideExcludedCode:
            match = exclude_end.match(line)
            if match is not None:
                if current_code_name is not None:
                    mode = ParseMode.InsideCodeSegment
                else:
                    mode = ParseMode.LookingForCodeSegment
                continue
            match = section_start.match(line)
            if match is not None:
                if current_code_name is not None:
                    code_segments[current_code_name] = current_code_segment
                    current_code_segment = []
                    current_code_name = match.group('name')
                mode = ParseMode.InsideCodeSegment
            continue
    if current_code_name is not None:
        code_segments[current_code_name] = current_code_segment

    return code_segments


def markdown_generator(input_dir, output_dir):
    input_dir = path.abspath(input_dir)

    for dirpath, dirnames, filenames in walk(input_dir):
        rel_path = dirpath[len(input_dir):]
        cur_output_dir = path.join(output_dir, rel_path)

        if not path.isdir(cur_output_dir):
            os.mkdir(cur_output_dir)

        for file_name in filenames:
            try:
                input_path = path.join(dirpath, file_name)
                name, ext = path.splitext(file_name)
                output_path = path.join(cur_output_dir, name + ".md")
                if ext != '.py':
                    continue
                markdown = extract_example(input_path)

                if markdown is not None:
                    with open(output_path, "wt") as f:
                        f.writelines(markdown)
            except:
                _log.error(f"Error while processing file: {file_name}", exc_info=True)

if __name__ == '__main__':
    bs_processors_dir = path.abspath(path.join(__file__, '../../..'))
    example_dir = path.abspath(path.join(bs_processors_dir, 'examples/src'))
    doc_example_dir = path.abspath(path.join(bs_processors_dir, 'docs/examples'))
    print(example_dir)
    markdown_generator(example_dir, doc_example_dir)
