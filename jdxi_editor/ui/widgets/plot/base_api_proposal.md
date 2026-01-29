# BasePlotWidget API Development Proposal

## Current Issues

1. **Repetitive Parameter Passing**: Methods require passing `painter`, `left_pad`, `plot_w`, `plot_h`, `top_pad` repeatedly
2. **Manual Tick Drawing**: Custom tick marks and labels require manual drawing code
3. **Manual Grid Drawing**: Custom grid positioning requires manual drawing instead of using `draw_grid()`
4. **Coordinate Conversion**: Manual conversion from data values to pixel coordinates scattered throughout
5. **No Configuration Object**: Padding, colors, fonts hardcoded in multiple places

## Proposed API Improvements

### 1. Plot Context/State Object

Create a `PlotContext` dataclass to hold common state:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class PlotContext:
    """Context object holding plot state for drawing operations."""
    painter: QPainter
    left_pad: int
    plot_w: int
    plot_h: int
    top_pad: int
    y_max: float
    y_min: float
    zero_y: Optional[float] = None
    
    def value_to_x(self, value: float, x_max: float) -> float:
        """Convert X data value to pixel coordinate."""
        return self.left_pad + (value / x_max) * self.plot_w
    
    def value_to_y(self, value: float, zero_at_bottom: bool = False) -> float:
        """Convert Y data value to pixel coordinate."""
        if zero_at_bottom:
            return self.top_pad + self.plot_h - (value / self.y_max) * self.plot_h
        return self.top_pad + ((self.y_max - value) / (self.y_max - self.y_min)) * self.plot_h
```

### 2. Plot Configuration

```python
@dataclass
class PlotConfig:
    """Configuration for plot appearance."""
    top_padding: int = 50
    bottom_padding: int = 80
    left_padding: int = 80
    right_padding: int = 50
    title_font_size: int = 16
    label_font_size: int = 10
    tick_font_size: int = 8
    title_color: QColor = QColor("orange")
    label_color: QColor = QColor("white")
    grid_color: QColor = QColor(Qt.GlobalColor.darkGray)
    envelope_color: QColor = QColor("orange")
    axis_color: QColor = QColor("white")
```

### 3. Enhanced Methods

#### Tick Drawing

```python
def draw_x_axis_ticks(
    self,
    ctx: PlotContext,
    tick_values: list[float],
    tick_labels: Optional[list[str]] = None,
    tick_length: int = 5,
    label_offset: int = 20,
    position: str = "bottom",  # "bottom", "top", or "zero"
) -> None:
    """
    Draw X-axis tick marks and labels.
    
    :param ctx: PlotContext
    :param tick_values: List of X values (in data coordinates) for tick positions
    :param tick_labels: Optional list of label strings (defaults to formatted tick_values)
    :param tick_length: Length of tick marks in pixels
    :param label_offset: Vertical offset for labels
    :param position: Where to draw ticks ("bottom", "top", or "zero" for zero line)
    """
    ...

def draw_y_axis_ticks(
    self,
    ctx: PlotContext,
    tick_values: list[float],
    tick_labels: Optional[list[str]] = None,
    tick_length: int = 5,
    label_offset: int = 45,
    zero_at_bottom: bool = False,
) -> None:
    """
    Draw Y-axis tick marks and labels.
    
    :param ctx: PlotContext
    :param tick_values: List of Y values (in data coordinates) for tick positions
    :param tick_labels: Optional list of label strings
    :param tick_length: Length of tick marks in pixels
    :param label_offset: Horizontal offset for labels
    :param zero_at_bottom: Whether zero is at bottom of plot
    """
    ...
```

#### Enhanced Grid Drawing

```python
def draw_grid(
    self,
    ctx: PlotContext,
    x_ticks: Optional[list[float]] = None,
    y_ticks: Optional[list[float]] = None,
    x_max: Optional[float] = None,
    num_vertical_lines: Optional[int] = 6,
    num_horizontal_lines: Optional[int] = 5,
    zero_at_bottom: bool = False,
) -> None:
    """
    Draw grid lines with optional custom tick positions.
    
    :param ctx: PlotContext
    :param x_ticks: Custom X tick positions (in data coordinates), overrides num_vertical_lines
    :param y_ticks: Custom Y tick positions (in data coordinates), overrides num_horizontal_lines
    :param x_max: Maximum X value for scaling (required if x_ticks provided)
    :param num_vertical_lines: Number of vertical grid lines (if x_ticks not provided)
    :param num_horizontal_lines: Number of horizontal grid lines (if y_ticks not provided)
    :param zero_at_bottom: Whether zero is at bottom of plot
    """
    ...
```

#### Coordinate Conversion Helpers

```python
def value_to_x_pixel(self, ctx: PlotContext, value: float, x_max: float) -> float:
    """Convert X data value to pixel coordinate."""
    return ctx.value_to_x(value, x_max)

def value_to_y_pixel(
    self, ctx: PlotContext, value: float, zero_at_bottom: bool = False
) -> float:
    """Convert Y data value to pixel coordinate."""
    return ctx.value_to_y(value, zero_at_bottom)
```

#### Simplified Method Signatures

```python
def draw_title(self, ctx: PlotContext, title: str) -> None:
    """Draw centered title using context."""
    ...

def draw_x_axis_label(self, ctx: PlotContext, label: str) -> None:
    """Draw X-axis label using context."""
    ...

def draw_y_axis_label(self, ctx: PlotContext, label: str) -> None:
    """Draw Y-axis label using context."""
    ...

def draw_axes(
    self,
    ctx: PlotContext,
    zero_at_bottom: bool = False,
) -> PlotContext:
    """
    Draw axes and update context with zero_y.
    
    :param ctx: PlotContext (will be updated with zero_y)
    :param zero_at_bottom: Whether zero line is at bottom
    :return: Updated PlotContext
    """
    ...
```

### 4. Template Method Pattern

```python
def paintEvent(self, event):
    """Template method for painting - subclasses override hook methods."""
    painter = QPainter(self)
    try:
        painter.setRenderHint(QPainter.Antialiasing)
        self.draw_background(painter)
        
        # Get configuration
        config = self.get_plot_config()
        
        # Calculate dimensions
        left_pad, plot_h, plot_w, top_pad = self.plot_dimensions(
            top_padding=config.top_padding,
            bottom_padding=config.bottom_padding,
            left_padding=config.left_padding,
            right_padding=config.right_padding,
        )
        
        # Get Y range
        y_max, y_min = self.get_y_range()
        
        # Create context
        ctx = PlotContext(
            painter=painter,
            left_pad=left_pad,
            plot_w=plot_w,
            plot_h=plot_h,
            top_pad=top_pad,
            y_max=y_max,
            y_min=y_min,
        )
        
        # Draw axes (updates ctx.zero_y)
        ctx = self.draw_axes(ctx, zero_at_bottom=self.zero_at_bottom())
        
        # Hook methods for subclasses
        self.draw_custom_ticks(ctx, config)
        self.draw_labels(ctx, config)
        self.draw_grid(ctx, config)
        self.draw_data(ctx, config)
        
    finally:
        painter.end()

def get_plot_config(self) -> PlotConfig:
    """Override to customize plot configuration."""
    return PlotConfig()

def get_y_range(self) -> tuple[float, float]:
    """Override to provide Y range."""
    return 1.0, 0.0

def zero_at_bottom(self) -> bool:
    """Override to specify if zero is at bottom."""
    return False

def draw_custom_ticks(self, ctx: PlotContext, config: PlotConfig) -> None:
    """Override to draw custom tick marks."""
    pass

def draw_labels(self, ctx: PlotContext, config: PlotConfig) -> None:
    """Override to draw title and axis labels."""
    self.draw_title(ctx, self.get_title())
    self.draw_x_axis_label(ctx, self.get_x_label())
    self.draw_y_axis_label(ctx, self.get_y_label())

def draw_grid(self, ctx: PlotContext, config: PlotConfig) -> None:
    """Override to draw custom grid."""
    self.draw_grid(ctx)  # Use default grid

def draw_data(self, ctx: PlotContext, config: PlotConfig) -> None:
    """Override to draw plot data (envelope, curve, etc.)."""
    pass

def get_title(self) -> str:
    """Override to provide plot title."""
    return ""

def get_x_label(self) -> str:
    """Override to provide X-axis label."""
    return ""

def get_y_label(self) -> str:
    """Override to provide Y-axis label."""
    return ""
```

### 5. Usage Example (DrumPitchEnvPlot)

```python
class DrumPitchEnvPlot(BasePlotWidget):
    def get_plot_config(self) -> PlotConfig:
        return PlotConfig(
            top_padding=50,
            bottom_padding=80,
            left_padding=80,
            right_padding=50,
        )
    
    def get_y_range(self) -> tuple[float, float]:
        return 80.0, -80.0
    
    def zero_at_bottom(self) -> bool:
        return False
    
    def get_title(self) -> str:
        return "Drum Pitch Envelope"
    
    def get_x_label(self) -> str:
        return "Time (s)"
    
    def get_y_label(self) -> str:
        return "Pitch"
    
    def draw_custom_ticks(self, ctx: PlotContext, config: PlotConfig) -> None:
        # X-axis ticks (time)
        total_time = self._calculate_total_time()
        x_ticks = [(i / 6) * total_time for i in range(7)]
        x_labels = [f"{t:.1f}" for t in x_ticks]
        self.draw_x_axis_ticks(
            ctx, x_ticks, x_labels, position="zero", tick_length=5
        )
        
        # Y-axis ticks (pitch)
        y_ticks = [i * 20 for i in range(-4, 5)]
        y_labels = [f"{y:+d}" for y in y_ticks]
        self.draw_y_axis_ticks(ctx, y_ticks, y_labels)
    
    def draw_grid(self, ctx: PlotContext, config: PlotConfig) -> None:
        # Custom grid using tick positions
        total_time = self._calculate_total_time()
        x_ticks = [(i / 6) * total_time for i in range(1, 6)]
        y_ticks = [i * 20 for i in range(-3, 4) if i != 0]
        self.draw_grid(ctx, x_ticks=x_ticks, y_ticks=y_ticks, x_max=total_time)
    
    def draw_data(self, ctx: PlotContext, config: PlotConfig) -> None:
        if not self.enabled:
            return
        
        envelope_curve, total_time = self._generate_envelope_curve()
        if not envelope_curve:
            return
        
        # Draw envelope curve
        path = QPainterPath()
        sample_rate = self.sample_rate
        num_points = min(500, len(envelope_curve))
        indices = np.linspace(0, len(envelope_curve) - 1, num_points).astype(int)
        
        for i in indices:
            if i >= len(envelope_curve):
                continue
            t = i / sample_rate
            x = ctx.value_to_x(t, total_time)
            y = ctx.value_to_y(envelope_curve[i])
            if i == indices[0]:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        
        painter = ctx.painter
        painter.setPen(QPen(config.envelope_color, 2))
        painter.drawPath(path)
        
        # Draw level points
        self._draw_level_points(ctx, config, total_time)
```

## Benefits

1. **Reduced Parameter Passing**: Context object eliminates repetitive parameters
2. **Type Safety**: Dataclasses provide better type hints and IDE support
3. **Easier Customization**: Configuration object centralizes appearance settings
4. **Reusable Helpers**: Tick drawing and coordinate conversion become reusable
5. **Template Pattern**: Clear structure for paintEvent with override points
6. **Less Boilerplate**: Common operations become one-liners
7. **Better Maintainability**: Changes to common behavior happen in one place

## Migration Path

1. Add new methods alongside existing ones (backward compatible)
2. Gradually migrate existing plots to use new API
3. Deprecate old methods after migration complete
4. Remove old methods in future version
