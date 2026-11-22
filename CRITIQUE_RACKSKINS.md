I would make RackSkins declarative by separating the description of a skin from the code that renders it.

At present, I suspect your skin classes are doing some combination of defining colours, configuring gradients, setting widget properties and implementing appearance-specific behaviour.

I would move towards a model where a skin is essentially a collection of immutable design specifications (design tokens), and the rendering layer interprets those specifications.

This would make it considerably easier to introduce new skins, including Brushed70s, classic Roland, modern digital and custom user-defined skins.

1. Separate the skin definition from rendering

I would aim for an architecture like this:

RackSkin

Declarative skin definition

ColourPalette

Colours and gradients

RackTypography

Fonts and text styles

RackGeometry

Padding, spacing and dimensions

ComponentStyles

Knobs, panels, meters and controls

SkinRenderer

Translates specifications into Qt painting and widget properties

The important principle is that Brushed70sSkin should describe what the skin looks like, not how to paint it.

2. Make the components declarative

For example, your gradient class should own its positions as well as its colours.

I would define it like this:

from dataclasses import dataclass
@dataclass(frozen=True)
class GradientStop:
    position: float
    color: str
@dataclass(frozen=True)
class GradientColorStops:
    stops: tuple[GradientStop, ...]
    def __post_init__(self):
        if not self.stops:
            raise ValueError("A gradient requires at least one stop")
        positions = [stop.position for stop in self.stops]
        if any(not 0.0 <= p <= 1.0 for p in positions):
            raise ValueError("Gradient positions must be between 0 and 1")
        if positions != sorted(positions):
            raise ValueError("Gradient stops must be ordered")

This is preferable to:

@dataclass
class GradientColorStops:
    stop1: QColor
    stop2: QColor

The latter assumes exactly two stops. The former supports arbitrary gradients, including multi-stop metallic effects.

For example:

BRUSHED_METAL = GradientColorStops(
    stops=(
        GradientStop(0.00, "#454545"),
        GradientStop(0.15, "#858585"),
        GradientStop(0.35, "#B7B7B7"),
        GradientStop(0.50, "#E2E2E2"),
        GradientStop(0.65, "#929292"),
        GradientStop(0.85, "#C1C1C1"),
        GradientStop(1.00, "#505050"),
    )
)

Your rendering function then becomes completely generic:

def set_gradient_color_stops(
    color_stops: GradientColorStops,
    gradient: QLinearGradient,
) -> None:
    for stop in color_stops.stops:
        gradient.setColorAt(
            stop.position,
            QColor(stop.color),
        )

This is a good example of separating data from implementation.

3. Make RackSkin a composition of specifications

I would use a central dataclass to describe the entire skin.

For example:

@dataclass(frozen=True)
class RackSkin:
    name: str
    description: str
    palette: ColorPalette
    typography: RackTypography
    geometry: RackGeometry
    panels: PanelStyle
    controls: ControlStyle
    meters: MeterStyle
    display: DisplayStyle

Each component is independently declarative.

For example:

@dataclass(frozen=True)
class PanelStyle:
    background: str
    border: str
    border_radius: int
    gradient: GradientColorStops | None = None
@dataclass(frozen=True)
class ControlStyle:
    background: str
    foreground: str
    border: str
    highlight: str
    gradient: GradientColorStops | None = None
@dataclass(frozen=True)
class MeterStyle:
    background: str
    foreground: str
    peak_color: str
    gradient: GradientColorStops | None = None

You can extend these specifications as the design system evolves.

4. Brushed70sSkin becomes a simple declaration

This is where the approach becomes particularly useful.

Instead of implementing a class with multiple styling methods, you define the skin as data.

BRUSHED_70S = RackSkin(
    name="Brushed 70s",
    description="Vintage brushed aluminium synthesizer",
    palette=ColorPalette(
        background="#242424",
        foreground="#E8E8E8",
        accent="#D69A43",
        secondary="#8C8C8C",
    ),
    typography=RackTypography(
        primary="Eurostile",
        secondary="Arial",
    ),
    geometry=RackGeometry(
        padding=12,
        spacing=8,
    ),
    panels=PanelStyle(
        background="#555555",
        border="#999999",
        border_radius=3,
        gradient=BRUSHED_METAL,
    ),
    controls=ControlStyle(
        background="#333333",
        foreground="#E5E5E5",
        border="#AAAAAA",
        highlight="#D69A43",
    ),
    meters=MeterStyle(
        background="#111111",
        foreground="#40C878",
        peak_color="#E34B38",
    ),
    display=DisplayStyle(
        background="#101810",
        foreground="#9BDAA0",
    ),
)

The actual colour values here are illustrative, but the architecture is what I would recommend.

5. Introduce a SkinRenderer

The renderer should be responsible for translating the specifications into Qt objects.

For example:

class SkinRenderer:
    def __init__(self, skin: RackSkin):
        self.skin = skin
    def create_panel_gradient(self) -> QLinearGradient:
        gradient = QLinearGradient(0, 0, 0, 200)
        set_gradient_color_stops(
            self.skin.panels.gradient,
            gradient,
        )
        return gradient
    def panel_stylesheet(self) -> str:
        style = self.skin.panels
        return (
            f"background-color: {style.background};"
            f"border: 1px solid {style.border};"
            f"border-radius: {style.border_radius}px;"
        )

In production, I would also have separate renderers or rendering strategies for more complex components, particularly knobs, meters and displays.

One important distinction: not every visual effect should be forced into a stylesheet. Gradients, brushed-metal textures, VU meters and oscilloscopes are better handled by dedicated painting or OpenGL rendering components.

6. What I would do with the existing RackSkins hierarchy

I would move towards this package structure:

rack_skins/
│
├── __init__.py
│
├── models/
│   ├── skin.py
│   ├── palette.py
│   ├── gradients.py
│   ├── typography.py
│   ├── geometry.py
│   └── components.py
│
├── definitions/
│   ├── brushed_70s.py
│   ├── roland_classic.py
│   ├── roland_modern.py
│   └── digital.py
│
├── renderers/
│   ├── skin_renderer.py
│   ├── panel_renderer.py
│   ├── control_renderer.py
│   ├── meter_renderer.py
│   └── display_renderer.py
│
└── registry.py

A SkinRegistry could then register and retrieve skins by identifier.

7. One additional recommendation: distinguish design tokens from component styles

I would avoid making every component independently specify its colours.

For example, a panel should ideally reference a palette token rather than duplicate a hex colour.

You could eventually support:

@dataclass(frozen=True)
class ColorPalette:
    background: str
    surface: str
    surface_highlight: str
    foreground: str
    muted: str
    accent: str
    border: str

This gives you consistency across the entire application.

It also makes it possible to implement user customisation, theme inheritance and light/dark variants without changing rendering code.

My recommendation

I would make three architectural decisions:

* Immutable specifications: RackSkin, GradientColorStops, PanelStyle, MeterStyle, etc. should be frozen dataclasses.
* Composition rather than inheritance: Brushed70sSkin should be an instance of RackSkin, not a subclass with its own rendering methods.
* Rendering separated from definitions: a renderer interprets the skin specification and creates Qt styles, gradients and painting instructions.

In particular, I would avoid a large inheritance hierarchy such as:

RackSkin
    ├── MetallicSkin
    │     ├── Brushed70sSkin
    │     └── ModernMetalSkin
    └── DigitalSkin
          ├── RolandDigitalSkin
          └── LCDSkin

Composition is much more flexible. A brushed-metal skin could use the same VU meter design as a digital skin, for example.

The ultimate objective: adding a new RackSkin should require defining a configuration, not writing new rendering code.

That is the test I would use to determine whether your architecture has become genuinely declarative.