import kivy
kivy.require('2.3.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.utils import platform
from kivy.properties import ObjectProperty

import threading
import os
import yt_dlp
import datetime

class YtdlpLogger:
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(f"YTDLP ERROR: {msg}")

class MainLayout(BoxLayout):
    download_thread = None
    cancel_requested = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_title = ''
    
    def log(self, message):
        print(f"APP_LOG: {message}")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.ids.log_label.text += f"[{timestamp}] {message}\n"
        Clock.schedule_once(self._scroll_to_bottom)

    def _scroll_to_bottom(self, dt):
        self.ids.log_scroll.scroll_y = 0
        
    def fetch_info(self):
        url = self.ids.url_input.text.strip()
        if not url:
            self.log("Please enter a URL first.")
            return
        
        self.ids.status_label.text = "Fetching video info..."
        self.ids.quality_spinner.text = "Loading..."
        self.ids.download_btn.disabled = True
        
        threading.Thread(target=self._fetch_info_thread, args=(url,), daemon=True).start()

    def _fetch_info_thread(self, url):
        ydl_opts = {
            'quiet': True, 
            'no_warnings': True,
            'logger': YtdlpLogger(),
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                qualities = ['Best', '1080p', '720p', '480p', '360p', 'Audio Only']
                
                Clock.schedule_once(lambda dt: self._update_ui(title, qualities))
                
        except Exception as e:
            err = str(e)
            Clock.schedule_once(lambda dt: self._error_ui(f"Fetch failed: {err}"))

    def _update_ui(self, title, qualities):
        self.video_title = title
        self.ids.quality_spinner.values = qualities
        self.ids.quality_spinner.text = 'Best'
        self.ids.download_btn.disabled = False
        self.ids.status_label.text = "READY TO DOWNLOAD"
        self.log(f"Loaded: {title}")

    def start_download(self):
        url = self.ids.url_input.text.strip()
        if not url:
            self.log("Error: Please enter a URL")
            return

        self.cancel_requested = False
        quality = self.ids.quality_spinner.text
        
        self.log(f"Starting download: {quality}")
        self.show_cancel_button()
        
        self.download_thread = threading.Thread(target=self._download_thread, args=(url, quality), daemon=True)
        self.download_thread.start()

    def cancel_download(self):
        self.cancel_requested = True
        self.log("Cancelling download...")
        self.hide_cancel_button()

    def show_cancel_button(self):
        self.ids.cancel_btn.disabled = False
        self.ids.cancel_btn.opacity = 1
        self.ids.download_btn.disabled = True

    def hide_cancel_button(self):
        self.ids.cancel_btn.disabled = True
        self.ids.cancel_btn.opacity = 0
        self.ids.download_btn.disabled = False

    def _download_thread(self, url, quality):
        ydl_opts = {
            'progress_hooks': [self._progress_hook],
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'logger': YtdlpLogger(),
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }

        # Download directory
        if platform == "android":
            from android.storage import primary_external_storage_path
            download_dir = os.path.join(primary_external_storage_path(), 'Download')
        else:
            download_dir = os.getcwd()
            
        ydl_opts['paths'] = {'home': download_dir}

        # Quality settings
        if quality == 'Audio Only':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif quality == 'Best':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            height = quality.replace('p', '')
            ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best'

        try:
            Clock.schedule_once(lambda dt: self.log(f"Saving to: {download_dir}"))
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Video')
                if not self.cancel_requested:
                    Clock.schedule_once(lambda dt: self._success_ui(title))
        except Exception as e:
            if not self.cancel_requested:
                Clock.schedule_once(lambda dt: self._error_ui(str(e)))

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                if 'downloaded_bytes' in d and 'total_bytes' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                else:
                    p_str = d.get('_percent_str', '0%').strip().replace('%', '')
                    progress = float(p_str) if p_str else 0
                
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                
                Clock.schedule_once(lambda dt: self._update_progress(progress, speed, eta))
            except Exception as e:
                print(f"Progress error: {e}")
        elif d['status'] == 'finished':
            Clock.schedule_once(lambda dt: self._update_status("Processing..."))

    def _update_progress(self, progress, speed, eta):
        self.ids.progress_bar.value = progress
        self.ids.status_label.text = f"Downloading: {progress:.1f}%"
        self.log(f"Progress: {progress:.1f}% | Speed: {speed} | ETA: {eta}")

    def _update_status(self, msg):
        self.ids.status_label.text = msg

    def _success_ui(self, title):
        self.ids.progress_bar.value = 100
        self.ids.status_label.text = "✔️ DOWNLOAD COMPLETE"
        self.hide_cancel_button()
        self.log(f"Successfully downloaded: {title}")

    def _error_ui(self, msg):
        self.ids.status_label.text = "Error"
        self.hide_cancel_button()
        self.log(f"Error: {msg}")

class VideoDownloaderApp(App):
    title = "Lastic Video Downloader"
    def build(self):
        from kivy.lang import Builder
        Builder.load_string('''
MainLayout:
    orientation: 'vertical'
    padding: 20
    spacing: 15

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: 80
        spacing: 10

        Label:
            text: 'Lastic Video Downloader'
            font_size: '24sp'
            bold: True
            color: 0.2, 0.6, 1, 1

        TextInput:
            id: url_input
            hint_text: 'Enter video URL here...'
            multiline: False
            size_hint_y: None
            height: 40

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: 50
        spacing: 10

        Button:
            text: 'Get Info'
            on_release: root.fetch_info()

        Spinner:
            id: quality_spinner
            text: 'Select Quality'
            values: []
            size_hint_x: 0.6

        Button:
            id: download_btn
            text: 'Download'
            disabled: True
            on_release: root.start_download()

        Button:
            id: cancel_btn
            text: 'Cancel'
            disabled: True
            opacity: 0
            background_color: 1, 0.2, 0.2, 1
            on_release: root.cancel_download()

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: 60
        spacing: 5

        Label:
            id: status_label
            text: 'Ready'
            font_size: '16sp'
            color: 0.8, 0.8, 0.8, 1

        ProgressBar:
            id: progress_bar
            max: 100
            value: 0
            size_hint_y: None
            height: 10

    ScrollView:
        id: log_scroll
        size_hint_y: None
        height: 200

        Label:
            id: log_label
            text: 'Ready to download videos...\\n'
            text_size: self.width, None
            font_size: '12sp'
            color: 0.7, 0.7, 0.7, 1
        ''')
        return MainLayout()

    def on_start(self):
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.INTERNET,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])

if __name__ == '__main__':
    VideoDownloaderApp().run()
