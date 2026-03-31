from PySide6.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QTextEdit
from core.base_tool import BaseTool
import yt_dlp
import threading

class DownloaderTool(BaseTool):
    @classmethod
    def get_name(cls):
        return "Asset Downloader"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Target URI (YouTube, HTTP...)")
        
        btn_dl = QPushButton("Execute Fetch Vector")
        btn_dl.clicked.connect(self.start_download)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        layout.addWidget(self.url_input)
        layout.addWidget(btn_dl)
        layout.addWidget(self.log)

    def start_download(self):
        url = self.url_input.text()
        if not url: return
        self.log.append(f"Initializing stream harvest for: {url}")
        threading.Thread(target=self._run_ytdlp, args=(url,), daemon=True).start()

    def _run_ytdlp(self, url):
        ydl_opts = {'outtmpl': './02_Assets/%(title)s.%(ext)s', 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            # Signal handling back to GUI thread omitted for brevity in raw script
        except Exception as e:
            pass