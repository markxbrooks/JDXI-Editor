from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
    QLabel, QPushButton, QFrame, QMessageBox,
    QInputDialog, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette, QColor
from pathlib import Path
import json
import os

from .style import Style
from ..midi import MIDIHelper

class PatchManager(QDialog):
    patchSelected = Signal(dict)  # Emitted when patch is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Patch Manager")
        self.setFixedSize(600, 400)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Patches section
        patches_frame = self._create_section("Patches", Style.COM_BG)
        self.patches_list = QListWidget()
        self.patches_list.currentRowChanged.connect(self._update_buttons)
        patches_frame.layout().addWidget(self.patches_list)
        layout.addWidget(patches_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self._load_patch)
        button_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_patch)
        button_layout.addWidget(self.save_btn)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self._export_patch)
        button_layout.addWidget(self.export_btn)
        
        self.rename_btn = QPushButton("Rename")
        self.rename_btn.clicked.connect(self._rename_patch)
        button_layout.addWidget(self.rename_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_patch)
        button_layout.addWidget(self.delete_btn)
        
        layout.addLayout(button_layout)
        
        # Load initial patch list
        self._load_patch_list()
        self._update_buttons()
        
    def _create_section(self, title, color):
        """Create a section frame with header"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        
        # Header
        header = QFrame()
        header.setFixedHeight(24)
        header.setAutoFillBackground(True)
        
        palette = header.palette()
        palette.setColor(QPalette.Window, QColor(color))
        header.setPalette(palette)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(6, 0, 6, 0)
        
        label = QLabel(title)
        label.setStyleSheet("color: white; font-weight: bold;")
        header_layout.addWidget(label)
        
        layout.addWidget(header)
        return frame
        
    def _get_patches_dir(self):
        """Get or create patches directory"""
        patches_dir = Path.home() / ".jdxi_manager" / "patches"
        patches_dir.mkdir(parents=True, exist_ok=True)
        return patches_dir
        
    def _load_patch_list(self):
        """Load list of saved patches"""
        self.patches_list.clear()
        patches_dir = self._get_patches_dir()
        
        for patch_file in sorted(patches_dir.glob("*.json")):
            self.patches_list.addItem(patch_file.stem)
            
    def _update_buttons(self):
        """Update button enabled states"""
        has_selection = self.patches_list.currentRow() >= 0
        self.load_btn.setEnabled(has_selection)
        self.export_btn.setEnabled(has_selection)
        self.rename_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        
    def _load_patch(self):
        """Load selected patch"""
        current = self.patches_list.currentItem()
        if not current:
            return
            
        patch_file = self._get_patches_dir() / f"{current.text()}.json"
        try:
            with open(patch_file) as f:
                patch_data = json.load(f)
            self.patchSelected.emit(patch_data)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load patch: {str(e)}")
            
    def _save_patch(self):
        """Save current patch"""
        name, ok = QInputDialog.getText(self, "Save Patch", 
            "Enter patch name:", text="New Patch")
            
        if ok and name:
            patch_file = self._get_patches_dir() / f"{name}.json"
            
            # Check for overwrite
            if patch_file.exists():
                reply = QMessageBox.question(self, "Overwrite",
                    f"Patch '{name}' already exists. Overwrite?",
                    QMessageBox.Yes | QMessageBox.No)
                    
                if reply == QMessageBox.No:
                    return
                    
            try:
                # Get current patch data from parent
                patch_data = self.parent().get_patch_data()
                
                # Save to file
                with open(patch_file, 'w') as f:
                    json.dump(patch_data, f, indent=2)
                    
                self._load_patch_list()
                QMessageBox.information(self, "Success", 
                    f"Patch '{name}' saved successfully")
                    
            except Exception as e:
                QMessageBox.warning(self, "Error",
                    f"Failed to save patch: {str(e)}")
                
    def _export_patch(self):
        """Export patch to file"""
        current = self.patches_list.currentItem()
        if not current:
            return
            
        filename, _ = QFileDialog.getSaveFileName(self,
            "Export Patch", "", "JSON Files (*.json)")
            
        if filename:
            try:
                source = self._get_patches_dir() / f"{current.text()}.json"
                with open(source) as f:
                    patch_data = json.load(f)
                    
                with open(filename, 'w') as f:
                    json.dump(patch_data, f, indent=2)
                    
                QMessageBox.information(self, "Success",
                    f"Patch exported to {filename}")
                    
            except Exception as e:
                QMessageBox.warning(self, "Error",
                    f"Failed to export patch: {str(e)}")
                
    def _rename_patch(self):
        """Rename selected patch"""
        current = self.patches_list.currentItem()
        if not current:
            return
            
        old_name = current.text()
        new_name, ok = QInputDialog.getText(self,
            "Rename Patch", "Enter new name:",
            text=old_name)
            
        if ok and new_name and new_name != old_name:
            try:
                old_file = self._get_patches_dir() / f"{old_name}.json"
                new_file = self._get_patches_dir() / f"{new_name}.json"
                
                if new_file.exists():
                    QMessageBox.warning(self, "Error",
                        f"Patch '{new_name}' already exists")
                    return
                    
                old_file.rename(new_file)
                self._load_patch_list()
                
            except Exception as e:
                QMessageBox.warning(self, "Error",
                    f"Failed to rename patch: {str(e)}")
                
    def _delete_patch(self):
        """Delete selected patch"""
        current = self.patches_list.currentItem()
        if not current:
            return
            
        reply = QMessageBox.question(self, "Delete",
            f"Delete patch '{current.text()}'?",
            QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            try:
                patch_file = self._get_patches_dir() / f"{current.text()}.json"
                os.remove(patch_file)
                self._load_patch_list()
                
            except Exception as e:
                QMessageBox.warning(self, "Error",
                    f"Failed to delete patch: {str(e)}") 