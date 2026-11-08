"""JDXI-inspired splash screen stylesheet fragments."""

SPLASH_STYLESHEET = """
QWidget#SplashRoot {
    background-color: #111111;
    border: 1px solid #2c2c2c;
}
QLabel#TitleLabel {
    color: #f3f3f3;
    font-size: 28px;
    font-weight: 600;
    letter-spacing: 1px;
}
QLabel#SubtitleLabel {
    color: #bbbbbb;
    font-size: 14px;
}
QLabel#StatusLabel {
    color: #88ccff;
    font-size: 18px;
    font-style: italic;
    font-weight: 500;
}
QLabel#CreditLabel {
    color: #888888;
    font-size: 10px;
}
QFrame#Card {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #1c1c1c, stop:1 #0f0f0f
    );
    border-radius: 14px;
    border: 1px solid #2a2a2a;
}
QProgressBar {
    background: #2a2a2a;
    border-radius: 6px;
    height: 14px;
    text-align: center;
    color: #cccccc;
    font-size: 10px;
}
QProgressBar::chunk {
    border-radius: 6px;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #7ac1ff, stop:1 #3b8fe8
    );
}
"""

SPLASH_CONTENT_MARGINS = (28, 28, 28, 28)
SPLASH_CONTENT_SPACING = 16
SPLASH_TITLE_GEOMETRY = (48, 48, 400, 44)
SPLASH_PROGRESS_WIDTH_INSET = 56

# Legacy alias kept for callers that still import the old name.
JDXI_SPLASH_STYLESHEET = SPLASH_STYLESHEET
