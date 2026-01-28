# 🎬 Lastic Video Downloader

A clean, simple video downloader for Android and desktop that supports multiple platforms including YouTube, Twitter/X, Instagram, and more.

## ✨ Features
- **Multi-Platform Support**: YouTube, Twitter/X, Instagram, TikTok, Facebook
- **Quality Options**: Best, 1080p, 720p, 480p, 360p, Audio Only (MP3)
- **Clean UI**: Simple, intuitive interface
- **Cancel Downloads**: Stop downloads anytime
- **Cross-Platform**: Works on Android and Desktop

## 🚀 Quick Start

### Desktop
```bash
pip install -r requirements.txt
python main.py
```

### Android (Build with GitHub Actions)
1. Push to GitHub
2. Actions will automatically build APK
3. Download and install APK

## 📱 Android Features
- **Storage Permissions**: Automatically requests needed permissions
- **Download Folder**: Saves to Android/Download folder
- **Touch Optimized**: Designed for mobile interaction
- **Progress Tracking**: Real-time download progress

## 🛠️ Built With
- **Kivy**: Cross-platform UI framework
- **yt-dlp**: Powerful video downloader backend
- **Python**: Core programming language
- **Buildozer**: Android packaging tool

## 📋 Requirements
- Python 3.8+
- For Android: Android API 21+
- FFmpeg (for audio processing)

## 🎯 Usage
1. Enter video URL
2. Click "Get Info"
3. Select quality
4. Click "Download"
5. Enjoy your video!

## 🔧 Build Android APK
```bash
# Requires Linux environment
buildozer android debug
```

## 📄 License
MIT License
