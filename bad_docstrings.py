import os
import re
import argparse

DOCSTRING_PATTERN = re.compile(
    r'("""[ \t]*\n[^\n]*\n)([^\n]*:(param|return|raises))',
    re.MULTILINE
)


def fix_docstrings_in_file(file_path: str, dry_run: bool = True) -> bool:
    """Fix malformed docstrings in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    fixed_content, count = DOCSTRING_PATTERN.subn(r'\1\n\2', content)

    if count > 0:
        if dry_run:
            print(f"[DRY RUN] Would fix {count} docstring(s) in {file_path}")
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"Fixed {count} docstring(s) in {file_path}")
        return True
    return False


def scan_directory(path: str, dry_run: bool = True):
    """Recursively fix malformed docstrings in Python files."""
    for root, _, files in os.walk(path):
        for filename in files:
            if filename.endswith('.py'):
                full_path = os.path.join(root, filename)
                fix_docstrings_in_file(full_path, dry_run=dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix Sphinx-style docstrings missing blank lines.")
    parser.add_argument("path", help="Path to the source code directory.")
    parser.add_argument("--apply", action="store_true", help="Actually fix the files instead of doing a dry run.")
    args = parser.parse_args()

    scan_directory(args.path, dry_run=not args.apply)
