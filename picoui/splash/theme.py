from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SplashTheme:
    background: str = "black"
    foreground: str = "white"

    title_font: tuple[str, ...] = (
        "Myriad Pro",
        "Segoe UI",
        "Arial",
    )

    subtitle_font: str = "Calibri"

    title_size: int = 20
    subtitle_size: int = 11