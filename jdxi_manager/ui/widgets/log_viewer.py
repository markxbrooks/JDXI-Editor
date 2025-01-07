from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QLabel, QSpinBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor, QColor, QTextCharFormat, QFont
from pathlib import Path
import logging

class LogViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer")
        self.setMinimumSize(800, 600)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Controls
        controls = QHBoxLayout()
        
        # Level filter
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.currentTextChanged.connect(self._filter_log)
        level_layout.addWidget(self.level_combo)
        controls.addLayout(level_layout)
        
        # Auto-refresh
        refresh_layout = QHBoxLayout()
        refresh_layout.addWidget(QLabel("Auto-refresh:"))
        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(0, 60)
        self.refresh_spin.setValue(5)
        self.refresh_spin.setSuffix(" sec")
        self.refresh_spin.valueChanged.connect(self._update_refresh_timer)
        refresh_layout.addWidget(self.refresh_spin)
        controls.addLayout(refresh_layout)
        
        # Buttons
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._load_log)
        controls.addWidget(self.refresh_btn)
        
        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.clicked.connect(self._clear_log)
        controls.addWidget(self.clear_btn)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Log display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        font = QFont(self.font().family(), 10)
        self.log_text.setFont(font)
        layout.addWidget(self.log_text)
        
        # Status bar
        self.status_label = QLabel()
        layout.addWidget(self.status_label)
        
        # Set up refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._load_log)
        self._update_refresh_timer()
        
        # Load initial log
        self._load_log()
        
    def _get_log_file(self):
        """Get path to current log file"""
        return Path.home() / ".jdxi_manager" / "logs" / "jdxi_manager.log"
        
    def _load_log(self):
        """Load and display log file"""
        try:
            log_file = self._get_log_file()
            if not log_file.exists():
                self.status_label.setText("Log file not found")
                return
                
            with open(log_file) as f:
                content = f.readlines()
                
            self.log_text.clear()
            cursor = self.log_text.textCursor()
            
            # Define formats for different log levels
            formats = {
                'DEBUG': QTextCharFormat(),
                'INFO': QTextCharFormat(),
                'WARNING': QTextCharFormat(),
                'ERROR': QTextCharFormat(),
                'CRITICAL': QTextCharFormat()
            }
            formats['DEBUG'].setForeground(QColor("#808080"))  # Gray
            formats['INFO'].setForeground(QColor("#000000"))   # Black
            formats['WARNING'].setForeground(QColor("#FFA500")) # Orange
            formats['ERROR'].setForeground(QColor("#FF0000"))   # Red
            formats['CRITICAL'].setForeground(QColor("#8B0000")) # Dark Red
            
            # Filter level
            filter_level = self.level_combo.currentText()
            if filter_level == "ALL":
                filtered_content = content
            else:
                filtered_content = [line for line in content if filter_level in line]
            
            # Display log with colors
            for line in filtered_content:
                for level, fmt in formats.items():
                    if level in line:
                        cursor.insertText(line, fmt)
                        break
                else:
                    cursor.insertText(line)
                    
            # Scroll to bottom
            cursor.movePosition(QTextCursor.End)
            self.log_text.setTextCursor(cursor)
            
            self.status_label.setText(f"Loaded {len(filtered_content)} lines")
            
        except Exception as e:
            self.status_label.setText(f"Error loading log: {str(e)}")
            
    def _clear_log(self):
        """Clear the log file"""
        try:
            log_file = self._get_log_file()
            with open(log_file, 'w') as f:
                f.write("")
            self._load_log()
            self.status_label.setText("Log cleared")
        except Exception as e:
            self.status_label.setText(f"Error clearing log: {str(e)}")
            
    def _filter_log(self):
        """Reload log with current filter"""
        self._load_log()
        
    def _update_refresh_timer(self):
        """Update auto-refresh timer"""
        interval = self.refresh_spin.value() * 1000  # Convert to milliseconds
        if interval > 0:
            self.refresh_timer.start(interval)
        else:
            self.refresh_timer.stop()
            
    def closeEvent(self, event):
        """Stop timer when closing"""
        self.refresh_timer.stop()
        super().closeEvent(event) 