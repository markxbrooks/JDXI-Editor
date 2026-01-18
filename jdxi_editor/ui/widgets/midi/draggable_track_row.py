"""
Draggable track row widget for MIDI track viewer.

This widget wraps a track row and enables drag-and-drop reordering.
"""

from PySide6.QtCore import QMimeData, Qt, Signal
from PySide6.QtGui import QDrag, QPainter
from PySide6.QtWidgets import QHBoxLayout, QWidget


class DraggableTrackRow(QWidget):
    """
    A draggable widget that wraps a track row, allowing drag-and-drop reordering.
    """
    
    # Signal emitted when a track is moved
    track_moved = Signal(int, int)  # from_index, to_index
    
    def __init__(self, track_index: int, content_widget: QHBoxLayout, parent=None):
        """
        Initialize the draggable track row.
        
        :param track_index: The index of the track in the MIDI file
        :param content_widget: The widget containing the track controls
        :param parent: Parent widget
        """
        super().__init__(parent)
        self.track_index = track_index
        self.drag_start_position = None
        self.setAcceptDrops(True)
        
        # Set up the layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add a drag handle indicator
        self.drag_handle = QWidget(self)
        self.drag_handle.setFixedWidth(10)
        self.drag_handle.setStyleSheet("""
            QWidget {
                background-color: #666;
                border: 1px solid #888;
            }
            QWidget:hover {
                background-color: #888;
            }
        """)
        layout.addWidget(self.drag_handle)
        
        # Add the content widget
        layout.addLayout(content_widget)
        
        # Set minimum height for better drag visibility
        self.setMinimumHeight(40)
        
        # Style the row
        self.setStyleSheet("""
            DraggableTrackRow {
                border: 1px solid transparent;
                background-color: transparent;
            }
            DraggableTrackRow:hover {
                border: 1px solid #888;
                background-color: rgba(128, 128, 128, 0.1);
            }
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse press to start drag operation."""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move to initiate drag operation."""
        if not (event.buttons() & Qt.LeftButton):
            return
        
        if self.drag_start_position is None:
            return
        
        # Check if mouse has moved enough to start drag
        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < 10:
            return
        
        # Create drag object
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Store track index in mime data
        mime_data.setText(str(self.track_index))
        drag.setMimeData(mime_data)
        
        # Create drag pixmap (semi-transparent preview)
        pixmap = self.grab()
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), Qt.GlobalColor.white)
        painter.setOpacity(0.7)
        painter.fillRect(pixmap.rect(), Qt.GlobalColor.white)
        painter.end()
        drag.setPixmap(pixmap)
        
        # Execute drag
        drag.exec(Qt.MoveAction)
    
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasText():
            try:
                source_index = int(event.mimeData().text())
                if source_index != self.track_index:
                    event.acceptProposedAction()
                    self.setStyleSheet("""
                        DraggableTrackRow {
                            border: 2px solid #4CAF50;
                            background-color: rgba(76, 175, 80, 0.2);
                        }
                    """)
            except ValueError:
                pass
        super().dragEnterEvent(event)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event."""
        self.setStyleSheet("""
            DraggableTrackRow {
                border: 1px solid transparent;
                background-color: transparent;
            }
            DraggableTrackRow:hover {
                border: 1px solid #888;
                background-color: rgba(128, 128, 128, 0.1);
            }
        """)
        super().dragLeaveEvent(event)
    
    def dropEvent(self, event):
        """Handle drop event to reorder tracks."""
        if event.mimeData().hasText():
            try:
                source_index = int(event.mimeData().text())
                target_index = self.track_index
                
                if source_index != target_index:
                    # Emit signal to move track
                    self.track_moved.emit(source_index, target_index)
                
                event.acceptProposedAction()
            except ValueError:
                pass
        
        # Reset style
        self.setStyleSheet("""
            DraggableTrackRow {
                border: 1px solid transparent;
                background-color: transparent;
            }
            DraggableTrackRow:hover {
                border: 1px solid #888;
                background-color: rgba(128, 128, 128, 0.1);
            }
        """)
        super().dropEvent(event)
