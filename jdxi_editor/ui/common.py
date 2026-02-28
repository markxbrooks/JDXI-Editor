"""
Common UI imports for JDXi Editor.

Re-exports frequently used Qt widgets and JDXi to reduce duplication
across UI modules.
"""

from PySide6.QtWidgets import QVBoxLayout, QWidget

from jdxi_editor.core.jdxi import JDXi

__all__ = ["JDXi", "QVBoxLayout", "QWidget"]
