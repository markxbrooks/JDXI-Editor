from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal
from jdxi_manager.midi.constants import Waveform
from PIL import Image, ImageDraw
import base64
from io import BytesIO


class WaveformButton(QPushButton):
    """Button for selecting oscillator waveform"""
    
    waveform_selected = Signal(Waveform)  # Emits selected waveform
    
    def __init__(self, waveform: Waveform, style="digital", parent=None):
        """Initialize waveform button
        
        Args:
            waveform: Waveform enum value
            parent: Parent widget
        """
        super().__init__(parent)
        self.waveform = waveform
        self.setText(waveform.display_name)
        self.setCheckable(True)
        self.clicked.connect(self._on_clicked)
        
        # Style
        self.setMinimumWidth(60)
        self.setStyleSheet("""
            QPushButton {
                background-color: #222222;
                color: #CCCCCC;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:checked {
                background-color: #333333;
                color: white;
                border: 1px solid #FF4444;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
    
    def _on_clicked(self):
        """Handle button click"""
        if self.isChecked():
            self.waveform_selected.emit(self.waveform) 

def pwsqu_png(btnfcol, rz):
    # Convert hex color to RGB
    rgb = tuple(int(btnfcol[i:i+2], 16) for i in (1, 3, 5))
    
    # Calculate dimensions and thickness
    x = int(17 * rz)
    y = int(9 * rz)
    th = int(rz + 0.49)
    
    # Create image with transparent background
    im = Image.new('RGBA', (x, y), (255, 255, 255, 0))
    draw = ImageDraw.Draw(im)
    
    # Set line color to white
    white = (255, 255, 255)
    
    # Draw lines
    draw.line([(th * 0.5, y - 1), (th * 0.5, 0)], fill=white, width=th)
    draw.line([(0, th * 0.5), (x * 0.68 - th * 0.5, th * 0.5)], fill=white, width=th)
    draw.line([(x * 0.68, 0), (x * 0.68, y - 1)], fill=white, width=th)
    draw.line([(x * 0.68, y - th * 0.5), (x - 1, y - th * 0.5)], fill=white, width=th)
    draw.line([(x - th * 0.5, y - 1), (x - th * 0.5, 0)], fill=white, width=th)
    draw.line([(x * 0.325 + int(th * 0.5), y * 0.223), (x * 0.325 + int(th * 0.5), y * 0.443)], fill=white, width=th)
    draw.line([(x * 0.325 + int(th * 0.5), y * 0.556), (x * 0.325 + int(th * 0.5), y * 0.776)], fill=white, width=th)
    draw.line([(x * 0.324, y - th * 0.5), (x * 0.400, y - th * 0.5)], fill=white, width=th)
    draw.line([(x * 0.500, y - th * 0.5), (x * 0.580, y - th * 0.5)], fill=white, width=th)
    
    # Save image to a bytes buffer
    buffer = BytesIO()
    im.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_str 

def triangle_png(btnfcol, rz):
    # Convert hex color to RGB
    rgb = tuple(int(btnfcol[i:i+2], 16) for i in (1, 3, 5))
    
    # Calculate dimensions and thickness
    x = int(17 * rz)
    y = int(9 * rz)
    th = int(rz + 0.49)
    
    # Create image with transparent background
    im = Image.new('RGBA', (x, y), (255, 255, 255, 0))
    draw = ImageDraw.Draw(im)
    
    # Set line color to white
    white = (255, 255, 255)
    
    # Draw lines
    draw.line([(0, y * 0.5 - int(rz * 0.5)), (x * 0.25, 0)], fill=white, width=th)
    draw.line([(x * 0.25, 0), (x * 0.75, y - 1)], fill=white, width=th)
    draw.line([(x * 0.75, y - 1), (x, y * 0.5)], fill=white, width=th)
    
    # Save image to a bytes buffer
    buffer = BytesIO()
    im.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_str 

def upsaw_png(btnfcol, rz):
    # Convert hex color to RGB
    rgb = tuple(int(btnfcol[i:i+2], 16) for i in (1, 3, 5))
    
    # Calculate dimensions and thickness
    x = int(17 * rz)
    y = int(9 * rz)
    th = int(rz + 0.49)
    if x % 2 == 0:
        x += 1
    
    # Create image with transparent background
    im = Image.new('RGBA', (x, y), (255, 255, 255, 0))
    draw = ImageDraw.Draw(im)
    
    # Set line color to white
    white = (255, 255, 255)
    
    # Draw lines
    draw.line([(0, y - 1), (x * 0.5, 0)], fill=white, width=th)
    draw.line([(x * 0.5, 0), (x * 0.5, y - 1)], fill=white, width=th)
    draw.line([(x * 0.5, y - 1), (x - 1, 0)], fill=white, width=th)
    draw.line([(x - th * 0.5, 0), (x - th * 0.5, y - 1)], fill=white, width=th)
    
    # Save image to a bytes buffer
    buffer = BytesIO()
    im.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_str 

def square_png(btnfcol, rz):
    # Convert hex color to RGB
    rgb = tuple(int(btnfcol[i:i+2], 16) for i in (1, 3, 5))
    
    # Calculate dimensions and thickness
    x = int(17 * rz)
    y = int(9 * rz)
    th = int(rz + 0.49)
    
    # Create image with transparent background
    im = Image.new('RGBA', (x, y), (255, 255, 255, 0))
    draw = ImageDraw.Draw(im)
    
    # Set line color to white
    white = (255, 255, 255)
    
    # Draw lines
    draw.line([(th * 0.5, y - 1), (th * 0.5, 0)], fill=white, width=th)
    draw.line([(0, th * 0.5), (x * 0.5, th * 0.5)], fill=white, width=th)
    draw.line([(x * 0.5, 0), (x * 0.5, y - 1)], fill=white, width=th)
    draw.line([(x * 0.5, y - th * 0.5), (x - 1, y - th * 0.5)], fill=white, width=th)
    draw.line([(x - th * 0.5, y - 1), (x - th * 0.5, 0)], fill=white, width=th)
    
    # Save image to a bytes buffer
    buffer = BytesIO()
    im.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_str 

def sine_png(btnfcol, rz):
    # Convert hex color to RGB
    rgb = tuple(int(btnfcol[i:i+2], 16) for i in (1, 3, 5))
    
    # Calculate dimensions and thickness
    x = int(17 * rz)
    y = int(9 * rz)
    th = int(rz + 0.49)
    
    # Create image with transparent background
    im = Image.new('RGBA', (x, y), (255, 255, 255, 0))
    draw = ImageDraw.Draw(im)
    
    # Set line color to white
    white = (255, 255, 255)
    
    # Draw arcs
    if rz == 1.75:
        draw.arc([(x * 0.25 - x * 0.25, y * 0.5 - y * 0.5), (x * 0.25 + x * 0.25, y * 0.5 + y * 0.5)], 180, 360, fill=white)
        draw.arc([(x * 0.75 - x * 0.25, y * 0.5 - y * 0.5), (x * 0.75 + x * 0.25, y * 0.5 + y * 0.5)], 0, 180, fill=white)
    elif rz >= 2.75:
        draw.arc([(x * 0.25 - x * 0.25, y * 0.5 - y * 0.5), (x * 0.25 + x * 0.25, y * 0.5 + y * 0.5)], 180, 360, fill=white)
        draw.arc([(x * 0.75 - x * 0.25, y * 0.5 - y * 0.5), (x * 0.75 + x * 0.25, y * 0.5 + y * 0.5)], 0, 180, fill=white)
    else:
        draw.arc([(x * 0.25 - x * 0.25, y * 0.5 - y * 0.5), (x * 0.25 + x * 0.25, y * 0.5 + y * 0.5)], 180, 360, fill=white)
        draw.arc([(x * 0.75 - x * 0.25, y * 0.5 - y * 0.5), (x * 0.75 + x * 0.25, y * 0.5 + y * 0.5)], 0, 180, fill=white)
    
    # Save image to a bytes buffer
    buffer = BytesIO()
    im.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_str 

def noise_png(btnfcol, rz):
    # Convert hex color to RGB
    rgb = tuple(int(btnfcol[i:i+2], 16) for i in (1, 3, 5))
    
    # Calculate dimensions and thickness
    x = int(17 * rz)
    y = int(9 * rz)
    th = int(rz + 0.49)
    
    # Create image with transparent background
    im = Image.new('RGBA', (x, y), (255, 255, 255, 0))
    draw = ImageDraw.Draw(im)
    
    # Set line color to white
    white = (255, 255, 255)
    
    # Draw polyline
    points = [
        (th * 0.5, y - 1), (th * 0.5, 0), (th * 0.5 + x * 0.0588, y * 0.61),
        (th * 0.5 + x * 0.0588 * 2, y * 0.12), (th * 0.5 + x * 0.0588 * 3, y * 0.87),
        (th * 0.5 + x * 0.0588 * 4, y * 0.50), (th * 0.5 + x * 0.0588 * 5, y * 0.99),
        (th * 0.5 + x * 0.0588 * 6, y * 0.01), (th * 0.5 + x * 0.0588 * 7, y * 0.93),
        (th * 0.5 + x * 0.0588 * 8, y * 0.15), (th * 0.5 + x * 0.0588 * 9, y * 0.85),
        (th * 0.5 + x * 0.0588 * 10, y * 0.01), (th * 0.5 + x * 0.0588 * 11, y * 0.92),
        (th * 0.5 + x * 0.0588 * 12, y * 0.23), (th * 0.5 + x * 0.0588 * 13, y * 0.72),
        (th * 0.5 + x * 0.0588 * 14, y * 0.06), (th * 0.5 + x * 0.0588 * 15, y * 0.45),
        (x - th * 0.5, y - 1), (x - th * 0.5, 0)
    ]
    draw.line(points, fill=white, width=th)
    
    # Save image to a bytes buffer
    buffer = BytesIO()
    im.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_str 

def spsaw_png(btnfcol, rz):
    # Convert hex color to RGB
    rgb = tuple(int(btnfcol[i:i+2], 16) for i in (1, 3, 5))
    
    # Calculate dimensions and thickness
    x = int(17 * rz)
    y = int(9 * rz)
    th = int(rz + 0.49)
    
    # Create image with transparent background
    im = Image.new('RGBA', (x, y), (255, 255, 255, 0))
    draw = ImageDraw.Draw(im)
    
    # Set line color to white
    white = (255, 255, 255)
    
    # Draw lines
    draw.line([(0, y * 0.5), (y * 0.5, 0)], fill=white, width=th)
    draw.line([(y * 0.5, 0), (y * 0.5, y - 1)], fill=white, width=th)
    draw.line([(y * 0.5, y - 1), (y * 0.5 + y - int(rz), 0)], fill=white, width=th)
    draw.line([(y * 0.5 + y - int(rz), 0), (y * 0.5 + y - int(rz), y - 1)], fill=white, width=th)
    draw.line([(y * 0.5 + y - int(rz), y - 1), (x - 1, y * 0.5)], fill=white, width=th)
    draw.line([(0, y - 1), (y - 1, 0)], fill=white, width=th)
    draw.line([(y - 1, 0), (y - 1, y - 1)], fill=white, width=th)
    draw.line([(y - 1, y - 1), (x - 1, 0)], fill=white, width=th)
    draw.line([(x - th * 0.5, 0), (x - th * 0.5, y - 1)], fill=white, width=th)
    
    # Save image to a bytes buffer
    buffer = BytesIO()
    im.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_str 


def pcm_png(btnfcol, rz):
    """
    PCM Icon
    """
    line_color = btnfcol
    x = int(17 * rz)
    y = int(9 * rz)
    th = int(rz + 0.49)
    width = x
    height = y

    # Create an image with a black background
    im = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(im)
    
    # Define line positions and heights with reduced spacing
    line_positions = [
        (0.1*width, 0.6*height), (0.2*width, 0.4*height), (0.3*width, 0.8*height), (0.4*width, 0.6*height), (0.5*width, 1.0*height), (0.6*width, 0.8*height), (0.7*width, 0.6*height),
        (0.8*width, 0.4*height), (0.9*width, 1.0*height), (1.0*width, 0.8*height), (1.1*width, 0.6*height), (1.2*width, 0.4*height)
    ]
    
    # Draw lines
    for x, h in line_positions:
        draw.line([(x, height), (x, height - h)], fill=line_color, width=th)
    
    # Save image to a bytes buffer
    buffer = BytesIO()
    im.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_str


def adsr_waveform_icon(btnfcol, rz: float = 1.0):
    # Create an image with a transparent background
    rgb = tuple(int(btnfcol[i:i+2], 16) for i in (1, 3, 5))
    width = int(17 * rz)
    height = int(9 * rz)
    th = int(rz + 0.49)
    line_color = btnfcol
    im = Image.new('RGBA', (width, height), (0, 0, 0, 0))

    draw = ImageDraw.Draw(im)
    
    # Define the ADSR shape
    points = [
        (0.2*width, height*1),  # Start
        (0.3*width, height*0),  # Attack
        (0.5*width, height*0.4),  # Decay
        (0.7*width, height*0.4),  # Sustain
        (0.9*width, height*1)   # Release
    ]
    
    # Draw the ADSR shape
    draw.line(points, fill=line_color, width=3)
    
    # Save image to a bytes buffer
    buffer = BytesIO()
    im.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_str
