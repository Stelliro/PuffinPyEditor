# /ui/widgets/splash_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize
import qtawesome as qta


class SplashScreen(QWidget):
    """
    A modern, frameless splash screen that shows loading status and
    fades out smoothly.
    """

    def __init__(self):
        super().__init__()
        # Set window flags for a frameless, top-level splash screen
        self.setWindowFlags(
            Qt.WindowType.SplashScreen |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedSize(320, 200)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Puffin Icon
        # --- FIX: Create an empty QLabel and then set its QPixmap ---
        self.icon_label = QLabel()
        icon = qta.icon('mdi.penguin', color='#83c092')
        pixmap = icon.pixmap(QSize(70, 70))  # Create a pixmap of the desired size
        self.icon_label.setPixmap(pixmap)   # Set the pixmap on the label
        # --- END FIX ---
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.icon_label)

        # Title Label
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        self.title_label = QLabel("PuffinPyEditor")
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        # Spacer
        self.main_layout.addStretch(1)

        # Status Label
        status_font = QFont("Arial", 9)
        self.status_label = QLabel("Initializing...")
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status_label)

        # Apply a nice stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #272e33;
                color: #d3c6aa;
                border-radius: 10px;
            }
        """)

    def set_status(self, message: str):
        """Updates the status message displayed on the splash screen."""
        self.status_label.setText(message)
        # Process events to ensure the UI updates immediately
        QApplication.processEvents()

    def finish(self, main_window):
        """
        Fades out the splash screen and then shows the main application window.
        """
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # When the fade-out is complete, show the main window and close this splash screen
        self.animation.finished.connect(lambda: (
            main_window.show(),
            self.close()
        ))

        self.animation.start()