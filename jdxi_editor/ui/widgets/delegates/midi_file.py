from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionButton, QStyle, QWidget, QFileDialog


class MidiFileDelegate(QStyledItemDelegate):
    """Delegate for MIDI file selection with file dialog."""

    # Class-level flag to ensure only one dialog is open at a time
    _dialog_open = False

    def __init__(self, table_widget=None, parent=None):
        super().__init__(parent)
        self.table_widget = table_widget

    def paint(self, painter, option, index):
        """Paint the cell with a button-like appearance."""
        # Get the file path
        if self.table_widget:
            item = self.table_widget.item(index.row(), index.column())
            file_path = item.text() if item else None
        else:
            file_path = index.data(Qt.ItemDataRole.EditRole)

        if file_path:
            import os

            text = os.path.basename(file_path)
        else:
            text = "Select MIDI File..."

        # Draw button-like appearance
        button = QStyleOptionButton()
        button.rect = option.rect
        button.text = text
        button.state = QStyle.StateFlag.State_Enabled
        if option.state & QStyle.StateFlag.State_Selected:
            button.state |= QStyle.StateFlag.State_HasFocus

        if self.table_widget:
            self.table_widget.style().drawControl(
                QStyle.ControlElement.CE_PushButton, button, painter
            )
        else:
            QWidget().style().drawControl(
                QStyle.ControlElement.CE_PushButton, button, painter
            )

    def editorEvent(self, event, model, option, index):
        """Handle mouse clicks to open file dialog."""
        if event.type() == event.Type.MouseButtonPress:
            if option.rect.contains(event.pos()):
                # Check if dialog is already open (singleton)
                if MidiFileDelegate._dialog_open:
                    return True  # Ignore click if dialog is already open

                # Open file dialog
                if self.table_widget:
                    try:
                        MidiFileDelegate._dialog_open = True
                        file_path, _ = QFileDialog.getOpenFileName(
                            self.table_widget,
                            "Select MIDI File",
                            "",
                            "MIDI Files (*.mid *.midi);;All Files (*)",
                        )
                        if file_path:
                            # Update the table item directly
                            item = self.table_widget.item(index.row(), index.column())
                            if item:
                                item.setText(file_path)
                                # Trigger itemChanged signal to save to database
                                self.table_widget.itemChanged.emit(item)
                    finally:
                        MidiFileDelegate._dialog_open = False
                return True
        return super().editorEvent(event, model, option, index)

    def sizeHint(self, option, index):
        """Return appropriate size for the button."""
        return QSize(150, 30)
