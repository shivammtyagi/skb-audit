import re

_SYMBOL_RE = re.compile(
    r"""(?:add_action|add_filter|apply_filters|do_action)\(\s*['"]([a-zA-Z0-9_\/]+)['"]"""
    r"""|function\s+([a-zA-Z0-9_]+)\s*\(""",
    re.VERBOSE,
)

def extract_symbols(code_blocks):
    names = set()
    for block in code_blocks or []:
        for m in _SYMBOL_RE.finditer(block):
            names.update(g for g in m.groups() if g)
    return sorted(names)
