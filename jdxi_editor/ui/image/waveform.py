"""
waveform_icons

This module provides functions to generate PNG images representing different waveform icons
using the Python Imaging Library (PIL). Each function returns address base64-encoded string of
the generated image.

Functions:
    generate_waveform_icon(icon_type, foreground_color, icon_scale): Generates address
    - triangle: Generates address triangle waveform icon.
    - upsaw: Generates an upward sawtooth waveform icon.
    - square: Generates address square waveform icon.
    - sine: Generates address sine waveform icon.
    - noise: Generates address noise waveform icon.
    - spsaw: Generates address special sawtooth waveform icon.
    - pcm: Generates address PCM waveform icon.
    - adsr: Generates an ADSR envelope waveform icon.
"""

import base64
import math
from io import BytesIO

from PIL import Image, ImageColor, ImageDraw
from PySide6.QtGui import QPixmap

from jdxi_editor.midi.data.digital.oscillator import WaveformType
from jdxi_editor.ui.image.utils import base64_to_pixmap


def generate_waveform_icon(
    waveform: str, foreground_color: str, icon_scale: float
) -> str:
    """
    Generate address waveform icon as address base64-encoded PNG image

    :param waveform: str
    :param foreground_color: str
    :param icon_scale: float
    :return: icon
    :rtype: str
    """
    x = int(17 * icon_scale)
    y = int(9 * icon_scale)
    th = int(icon_scale + 0.49)
    im = Image.new("RGBA", (x, y), (255, 255, 255, 0))
    draw = ImageDraw.Draw(im)
    color = ImageColor.getrgb(foreground_color)

    half_y = y * 0.5
    quarter_x = x * 0.25
    three_quarters_x = x * 0.75

    if waveform == WaveformType.TRIANGLE:
        draw.line(
            [(0, half_y), (quarter_x, 0), (three_quarters_x, y - 1), (x, half_y)],
            fill=color,
            width=th,
        )
    elif waveform == WaveformType.UPSAW:
        draw.line(
            [(0, y - 1), (x * 0.5, 0), (x * 0.5, y - 1), (x - 1, 0)],
            fill=color,
            width=th,
        )
    elif waveform == WaveformType.SQUARE:
        draw.line(
            [
                (th * 0.5, y - 1),
                (th * 0.5, 0),
                (x * 0.5, 0),
                (x * 0.5, y - 1),
                (x - th * 0.5, y - 1),
                (x - th * 0.5, 0),
            ],
            fill=color,
            width=th,
        )
    elif waveform == WaveformType.SINE:
        # Define the number of points for smoothness
        num_points = 60
        sine_wave = [
            (
                i * x / (num_points - 1),
                half_y + (math.sin(i * 2 * math.pi / (num_points - 1)) * half_y * 0.8),
            )
            for i in range(num_points)
        ]
        draw.line(sine_wave, fill=color, width=th)

    elif waveform == WaveformType.LPF_FILTER:
        """
        Low-pass filter icon:
        Full amplitude on the left, progressively attenuated to the right,
        visually representing a low-pass filter's frequency response.
        """
        num_points = 80
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)  # 0 → 1 across X
            x_pos = t * (x - 1)
            # Sigmoid-style amplitude drop for LPF
            # Left: full height, Right: approaches 0
            # Shifted so the drop starts ~30% from left
            y_pos = half_y + half_y * (1 - 1 / (1 + math.exp(-12 * (t - 0.3))))
            # Flip vertically so 0 is bottom of canvas
            y_pos = y - y_pos
            points.append((x_pos, y_pos))
        draw.line(points, fill=color, width=th)

    elif waveform == WaveformType.HPF_FILTER:
        """
        High-pass filter icon:
        Low amplitude on the left, progressively increasing to full amplitude on the right,
        visually representing a high-pass filter's frequency response.
        """
        num_points = 80
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)  # 0 → 1 across X
            x_pos = t * (x - 1)
            # Sigmoid-style amplitude rise for HPF
            # Left: approaches 0, Right: full height
            # Shifted so the rise starts ~30% from left
            y_pos = half_y + half_y * (1 / (1 + math.exp(-12 * (t - 0.3))))
            # Flip vertically so 0 is bottom of canvas
            y_pos = y - y_pos
            points.append((x_pos, y_pos))
        draw.line(points, fill=color, width=th)

    elif waveform == WaveformType.BPF_FILTER:
        """
        Band-pass filter icon:
        Low frequencies attenuated, middle frequencies pass, high frequencies attenuated.
        Smooth bump in the middle representing the passband.
        """
        num_points = 80
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)  # 0 → 1 across X
            x_pos = t * (x - 1)
            # High-pass sigmoid: rises around 0.2
            hp = 1 / (1 + math.exp(-12 * (t - 0.2)))
            # Low-pass sigmoid: falls around 0.8
            lp = 1 / (1 + math.exp(-12 * (0.8 - t)))
            # Multiply for band-pass effect
            amplitude = hp * lp
            y_pos = half_y + half_y * amplitude
            # Flip vertically so 0 is bottom
            y_pos = y - y_pos
            points.append((x_pos, y_pos))
        draw.line(points, fill=color, width=th)

    elif waveform == WaveformType.BYPASS_FILTER:
        """
        Bypass filter icon:
        A straight horizontal line representing no filtering - signal passes through unchanged.
        The abrupt, flat line visually represents bypass mode.
        """
        # Draw a straight horizontal line at the middle (representing full signal, no attenuation)
        draw.line(
            [(0, half_y), (x - 1, half_y)],
            fill=color,
            width=th,
        )

    elif waveform == WaveformType.FILTER_SINE:
        """
        Low-pass filter icon:
        A waveform whose amplitude decreases from left to right,
        visually representing high-frequency attenuation.
        """
        num_points = 60
        points = []

        for i in range(num_points):
            t = i / (num_points - 1)  # 0 → 1 across X
            x_pos = t * (x - 1)

            # Amplitude rolls off toward the right (LPF effect)
            amplitude = half_y * (1.0 - 0.75 * t)

            # Slightly flattened sine to feel more "filtered"
            y_pos = half_y + math.sin(t * 2.5 * math.pi) * amplitude * 0.9

            points.append((x_pos, y_pos))

        draw.line(points, fill=color, width=th)
    elif waveform == WaveformType.NOISE:
        import random

        points = [
            (th * 0.5 + x * 0.0588 * i, y * (0.5 + random.uniform(-0.4, 0.4)))
            for i in range(16)
        ]
        draw.line(points, fill=color, width=th)
    elif waveform == WaveformType.SPSAW:
        draw.line(
            [(0, half_y), (y * 0.5, 0), (y * 0.5, y - 1), (x - 1, half_y)],
            fill=color,
            width=th,
        )
    elif waveform == WaveformType.PCM:
        for i in range(12):
            draw.line(
                [
                    (x * (0.1 * i), y),
                    (x * (0.1 * i), y - (y * (0.4 + 0.2 * (-1) ** i))),
                ],
                fill=color,
                width=th,
            )
    elif waveform == WaveformType.PWSQU:
        draw.line([(th * 0.5, y - 1), (th * 0.5, 0)], fill=color, width=th)
        draw.line(
            [(0, th * 0.5), (x * 0.68 - th * 0.5, th * 0.5)], fill=color, width=th
        )
        draw.line([(x * 0.68, 0), (x * 0.68, y - 1)], fill=color, width=th)
        draw.line(
            [(x * 0.68, y - th * 0.5), (x - 1, y - th * 0.5)], fill=color, width=th
        )
        draw.line([(x - th * 0.5, y - 1), (x - th * 0.5, 0)], fill=color, width=th)
    elif waveform == WaveformType.ADSR:
        # rgb = tuple(int(foreground_color[i : i + 2], 16) for i in (1, 3, 5))
        width = int(17 * icon_scale)
        height = int(9 * icon_scale)
        # th = int(icon_scale + 0.49)
        line_color = foreground_color
        im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        # Define the ADSR shape
        points = [
            (0.2 * width, height * 1),  # Start
            (0.3 * width, height * 0),  # Attack
            (0.5 * width, height * 0.4),  # Decay
            (0.7 * width, height * 0.4),  # Sustain
            (0.9 * width, height * 1),  # Release
        ]
        # Draw the ADSR shape
        draw.line(points, fill=line_color, width=3)
    buffer = BytesIO()
    im.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def generate_icon_from_waveform(icon_name: str) -> QPixmap:
    """Generate icon from waveform type"""
    # Lazy import to avoid circular dependency
    from jdxi_editor.ui.style import JDXiUIStyle

    icon_base64 = generate_waveform_icon(icon_name, JDXiUIStyle.WHITE, 1.0)
    pixmap = base64_to_pixmap(icon_base64)
    return pixmap
