import re

with open("your_file.py") as f:
    code = f.read()

bad_docstrings = re.findall(r'"""[ \t]*\n[^\n]*\n[^\n]*:param', code)
print(f"Found {len(bad_docstrings)} docstrings missing a blank line")