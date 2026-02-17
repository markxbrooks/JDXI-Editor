"""
Oscillator Widgets
"""


class OscillatorWidgetTypes:
    """Base class for Oscillator Widgets"""
    PWM: str = "pwm_widget"
    PITCH_ENV: str = "pitch_env_widget"

    """
    for reference
    waveform_buttons: dict[Any, QWidget] | None = None
    osc_pitch_coarse_slider: QWidget | None = None
    osc_pitch_fine_slider: QWidget | None = None
    pitch_env_widget: PitchEnvWidget | None = None
    pwm_widget: PWMWidget | None = None
    switches: list[QWidget] | None = field(default_factory=list)
    tuning: list[QWidget] | None = field(default_factory=list)
    env: list[QWidget] | None = field(default_factory=list)
    """