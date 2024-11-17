import sys
import os
import requests
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout, QPushButton,
                             QMainWindow, QWidget, QLabel, QSlider, QFrame, QComboBox, QScrollArea, QGroupBox, QTabWidget, QSizePolicy, QSpinBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify API credentials
SPOTIPY_CLIENT_ID = '..........'
SPOTIPY_CLIENT_SECRET = '..................'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback/'
SCOPE = 'user-read-playback-state user-modify-playback-state user-read-currently-playing user-library-read user-read-recently-played'

# Icon download URLs
ICON_URLS = {
    "shuffle_on": "https://img.icons8.com/ios-filled/50/1DB954/shuffle.png",
    "shuffle_off": "https://img.icons8.com/ios/50/ffffff/shuffle.png",
    "prev": "https://img.icons8.com/ios-filled/50/ffffff/rewind.png",
    "play": "https://img.icons8.com/ios-filled/100/ffffff/play.png",
    "pause": "https://img.icons8.com/ios-filled/100/ffffff/pause.png",
    "next": "https://img.icons8.com/ios-filled/50/ffffff/fast-forward.png",
    "repeat_on": "https://img.icons8.com/ios-filled/50/1DB954/repeat.png",
    "repeat_off": "https://img.icons8.com/ios/50/ffffff/repeat.png",
    "volume": "https://img.icons8.com/ios-filled/50/ffffff/medium-volume.png",
    "close": "https://img.icons8.com/ios-filled/50/ffffff/delete-sign.png",
    "minimize": "https://img.icons8.com/ios-filled/50/ffffff/minimize-window.png",
    "spotify": "https://img.icons8.com/ios-filled/50/1DB954/spotify.png"
}

# Download icons if they are not already available locally
def download_icons():
    if not os.path.exists("icons"):
        os.makedirs("icons")
    for name, url in ICON_URLS.items():
        icon_path = f"icons/{name}.png"
        if not os.path.exists(icon_path):
            response = requests.get(url)
            if response.status_code == 200:
                with open(icon_path, 'wb') as f:
                    f.write(response.content)
            else:
                print(f"Kon de icoon niet downloaden: {name} vanaf {url}")

download_icons()

# Spotify client setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE,
    cache_path='spotify_token.txt'
))

class SpotifyStyleWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.update_track_info()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_track_info)
        self.timer.start(1000)  # Update every second

    def init_ui(self):
        self.setWindowTitle("Spotify Widget")
        self.setGeometry(100, 100, 450, 600)
        self.setStyleSheet("""
            background-color: #121212;
            border-radius: 20px;
        """)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # Header Layout
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(10)
        self.spotify_logo = QLabel(self)
        self.spotify_logo.setPixmap(QIcon("icons/spotify.png").pixmap(25, 25))
        self.header_layout.addWidget(self.spotify_logo)
        self.header_title = QLabel("Spotify")
        self.header_title.setFont(QFont("Arial", 14, QFont.Bold))
        self.header_title.setStyleSheet("color: #FFFFFF;")
        self.header_layout.addWidget(self.header_title)
        self.header_layout.addStretch()
        self.minimize_button = self.create_icon_button("icons/minimize.png", icon_only=True)
        self.minimize_button.clicked.connect(self.showMinimized)
        self.header_layout.addWidget(self.minimize_button)
        self.close_button = self.create_icon_button("icons/close.png", icon_only=True)
        self.close_button.clicked.connect(self.close)
        self.header_layout.addWidget(self.close_button)
        
        # Track Info Layout
        self.track_info_layout = QHBoxLayout()

        # Album Art
        self.album_art = QLabel(self)
        self.album_art.setFixedSize(100, 100)
        self.album_art.setStyleSheet("border-radius: 15px; background-color: #282828;")
        self.track_info_layout.addWidget(self.album_art)

        # Track and Artist Info
        self.track_info = QVBoxLayout()
        self.track_label = QLabel("Geen nummer speelt")
        self.track_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.track_label.setStyleSheet("color: #FFFFFF;")
        self.artist_label = QLabel("Geen artiest")
        self.artist_label.setFont(QFont("Arial", 12))
        self.artist_label.setStyleSheet("color: #B3B3B3;")
        self.track_info.addWidget(self.track_label)
        self.track_info.addWidget(self.artist_label)
        self.track_info_layout.addLayout(self.track_info)

        # Progress Slider
        self.progress_layout = QHBoxLayout()
        self.current_time_label = QLabel("0:00")
        self.current_time_label.setStyleSheet("color: #B3B3B3;")
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #404040;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #1DB954;
                border: none;
                width: 12px;
                height: 12px;
                margin: -5px 0;
                border-radius: 6px;
            }
        """)
        self.end_time_label = QLabel("0:00")
        self.end_time_label.setStyleSheet("color: #B3B3B3;")
        self.progress_layout.addWidget(self.current_time_label)
        self.progress_layout.addWidget(self.progress_slider)
        self.progress_layout.addWidget(self.end_time_label)

        # Media Controls Layout
        self.control_layout = QHBoxLayout()
        self.control_layout.setSpacing(20)

        # Shuffle Button
        self.shuffle_button = self.create_icon_button("icons/shuffle_off.png")
        self.control_layout.addWidget(self.shuffle_button)

        # Previous Button
        self.prev_button = self.create_icon_button("icons/prev.png")
        self.control_layout.addWidget(self.prev_button)

        # Play/Pause Button
        self.play_pause_button = self.create_icon_button("icons/play.png", round_button=True)
        self.control_layout.addWidget(self.play_pause_button)

        # Next Button
        self.next_button = self.create_icon_button("icons/next.png")
        self.control_layout.addWidget(self.next_button)

        # Repeat Button
        self.repeat_button = self.create_icon_button("icons/repeat_off.png")
        self.control_layout.addWidget(self.repeat_button)

        # Volume Slider
        self.volume_layout = QHBoxLayout()
        self.volume_layout.setSpacing(10)
        self.volume_icon = QLabel(self)
        self.volume_icon.setPixmap(QIcon("icons/volume.png").pixmap(30, 30))
        self.volume_layout.addWidget(self.volume_icon)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #404040;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #1DB954;
                border: none;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)
        self.volume_layout.addWidget(self.volume_slider)

        # Recent Played & Queue Layout
        self.extra_layout = QVBoxLayout()
        self.recently_played_label = QLabel("Recent gespeeld:")
        self.recently_played_label.setFont(QFont("Arial", 14))
        self.recently_played_label.setStyleSheet("color: #FFFFFF;")
        self.extra_layout.addWidget(self.recently_played_label)

        self.recently_played_list = QComboBox()
        self.recently_played_list.setStyleSheet("background-color: #282828; color: #FFFFFF; border-radius: 5px;")
        self.update_recently_played()
        self.extra_layout.addWidget(self.recently_played_list)

        self.queue_label = QLabel("Volgende nummer in wachtrij:")
        self.queue_label.setFont(QFont("Arial", 14))
        self.queue_label.setStyleSheet("color: #FFFFFF;")
        self.extra_layout.addWidget(self.queue_label)

        self.queue_track_label = QLabel("Geen wachtrij")
        self.queue_track_label.setFont(QFont("Arial", 12))
        self.queue_track_label.setStyleSheet("color: #B3B3B3;")
        self.extra_layout.addWidget(self.queue_track_label)

        # Scale Adjustment Layout
        self.scale_layout = QVBoxLayout()
        self.scale_label = QLabel("Aanpassen grootte widget:")
        self.scale_label.setFont(QFont("Arial", 14))
        self.scale_label.setStyleSheet("color: #FFFFFF;")
        self.scale_layout.addWidget(self.scale_label)

        self.scale_spinbox = QSpinBox()
        self.scale_spinbox.setMinimum(300)
        self.scale_spinbox.setMaximum(800)
        self.scale_spinbox.setValue(450)
        self.scale_spinbox.setSuffix(" px")
        self.scale_spinbox.setStyleSheet("background-color: #282828; color: #FFFFFF; border-radius: 5px;")
        self.scale_spinbox.valueChanged.connect(self.adjust_size)
        self.scale_layout.addWidget(self.scale_spinbox)

        # Add layouts to main layout
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addLayout(self.track_info_layout)
        self.main_layout.addLayout(self.progress_layout)
        self.main_layout.addLayout(self.control_layout)
        self.main_layout.addLayout(self.volume_layout)
        self.main_layout.addLayout(self.extra_layout)
        self.main_layout.addLayout(self.scale_layout)

        # Connect buttons to functions
        self.prev_button.clicked.connect(self.previous_track)
        self.play_pause_button.clicked.connect(self.toggle_playback)
        self.next_button.clicked.connect(self.next_track)
        self.shuffle_button.clicked.connect(self.toggle_shuffle)
        self.repeat_button.clicked.connect(self.toggle_repeat)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.recently_played_list.currentIndexChanged.connect(self.play_recently_played)

    def create_icon_button(self, icon_path, round_button=False, icon_only=False):
        button = QPushButton()
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
        button_style = """
        QPushButton {
            background-color: #282828;
            border: none;
            color: white;
            border-radius: 15px;
        }
        QPushButton:hover {
            background-color: #3C3C3C;
        }
        """
        if round_button:
            button_style += """
            QPushButton {
                width: 70px;
                height: 70px;
                border-radius: 35px;
                background-color: #1DB954;
            }
            QPushButton:hover {
                background-color: #1ED760;
            }
            """
        if icon_only:
            button.setFixedSize(25, 25)
        else:
            button.setFixedSize(70, 70 if round_button else 40)
        button.setStyleSheet(button_style)
        return button

    def update_track_info(self):
        try:
            current_track = sp.current_playback()
            if current_track and current_track['is_playing']:
                track_name = current_track['item']['name']
                artist_name = ', '.join(artist['name'] for artist in current_track['item']['artists'])
                album_images = current_track['item']['album']['images']
                progress_ms = current_track['progress_ms']
                duration_ms = current_track['item']['duration_ms']

                # Update track and artist labels
                self.track_label.setText(track_name)
                self.artist_label.setText(artist_name)

                # Update progress slider and time labels
                self.progress_slider.setMaximum(duration_ms)
                self.progress_slider.setValue(progress_ms)
                self.current_time_label.setText(self.ms_to_time(progress_ms))
                self.end_time_label.setText(self.ms_to_time(duration_ms))

                # Update album art with requests
                if album_images:
                    album_art_url = album_images[0]['url']
                    response = requests.get(album_art_url)
                    if response.status_code == 200:
                        pixmap = QPixmap()
                        pixmap.loadFromData(response.content)
                        self.album_art.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

                # Update shuffle and repeat button states
                shuffle_state = current_track['shuffle_state']
                repeat_state = current_track['repeat_state']
                if shuffle_state:
                    self.shuffle_button.setIcon(QIcon("icons/shuffle_on.png"))
                else:
                    self.shuffle_button.setIcon(QIcon("icons/shuffle_off.png"))

                if repeat_state == "off":
                    self.repeat_button.setIcon(QIcon("icons/repeat_off.png"))
                else:
                    self.repeat_button.setIcon(QIcon("icons/repeat_on.png"))

                # Update next track in queue if available
                queue = sp.queue()
                if queue and queue['queue']:
                    next_track = queue['queue'][0]['name'] + " - " + ', '.join(artist['name'] for artist in queue['queue'][0]['artists'])
                    self.queue_track_label.setText(next_track)
                else:
                    self.queue_track_label.setText("Geen wachtrij")

            else:
                self.track_label.setText("Geen nummer speelt")
                self.artist_label.setText("Geen artiest")
                self.progress_slider.setValue(0)
                self.current_time_label.setText("0:00")
                self.end_time_label.setText("0:00")
        except Exception as e:
            self.track_label.setText("Fout bij ophalen track")
            self.artist_label.setText(str(e))

    def ms_to_time(self, ms):
        seconds = int((ms / 1000) % 60)
        minutes = int((ms / (1000 * 60)) % 60)
        return f"{minutes}:{seconds:02}"

    def toggle_playback(self):
        try:
            current_track = sp.current_playback()
            if current_track and current_track['is_playing']:
                sp.pause_playback()
                self.play_pause_button.setIcon(QIcon("icons/play.png"))
            else:
                sp.start_playback()
                self.play_pause_button.setIcon(QIcon("icons/pause.png"))
        except Exception as e:
            self.track_label.setText("Fout bij afspelen")

    def next_track(self):
        try:
            sp.next_track()
            self.update_track_info()
        except Exception as e:
            self.track_label.setText("Fout bij volgende track")

    def previous_track(self):
        try:
            sp.previous_track()
            self.update_track_info()
        except Exception as e:
            self.track_label.setText("Fout bij vorige track")

    def toggle_shuffle(self):
        try:
            current_shuffle_state = sp.current_playback()['shuffle_state']
            sp.shuffle(not current_shuffle_state)
            self.update_track_info()
        except Exception as e:
            self.track_label.setText("Fout bij shuffle")

    def toggle_repeat(self):
        try:
            current_repeat_state = sp.current_playback()['repeat_state']
            if current_repeat_state == "off":
                sp.repeat("context")
            elif current_repeat_state == "context":
                sp.repeat("track")
            else:
                sp.repeat("off")
            self.update_track_info()
        except Exception as e:
            self.track_label.setText("Fout bij repeat")

    def set_volume(self):
        try:
            volume = self.volume_slider.value()
            sp.volume(volume)
        except Exception as e:
            self.track_label.setText("Fout bij volume aanpassen")

    def update_recently_played(self):
        try:
            recently_played = sp.current_user_recently_played(limit=10)
            self.recently_played_list.clear()
            for item in recently_played['items']:
                track_name = item['track']['name']
                artist_name = ', '.join(artist['name'] for artist in item['track']['artists'])
                self.recently_played_list.addItem(f"{track_name} - {artist_name}")
        except Exception as e:
            self.track_label.setText("Fout bij ophalen recent gespeeld")

    def play_recently_played(self):
        try:
            selected_index = self.recently_played_list.currentIndex()
            if selected_index >= 0:
                recently_played = sp.current_user_recently_played(limit=10)
                track_uri = recently_played['items'][selected_index]['track']['uri']
                sp.start_playback(uris=[track_uri])
                self.update_track_info()
        except Exception as e:
            self.track_label.setText("Fout bij afspelen recent gespeeld")

    def adjust_size(self):
        new_size = self.scale_spinbox.value()
        self.setGeometry(100, 100, new_size, 600)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set up main window
    window = SpotifyStyleWidget()
    window.show()

    # Execute the application
    sys.exit(app.exec_())
