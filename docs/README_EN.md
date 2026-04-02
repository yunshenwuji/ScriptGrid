# ScriptGrid

English | [中文](../README.md)

![Python Version](https://img.shields.io/badge/Python-3.13+-blue.svg)
![Framework](https://img.shields.io/badge/Framework-FastAPI-green.svg)
![Deployment](https://img.shields.io/badge/Deploy-Docker-blue.svg)
![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)

**A lightweight online format conversion tool for audio description creators.**

[**Live Demo**](#-live-demo) | [**Quick Start**](#-quick-start) | [**Deployment Guide**](#-local-deployment--development)

---

## 📖 Project Overview

In audio description creation team collaboration, there is often a need to convert between **subtitle formats (such as .ass, .srt)** and **spreadsheet formats (.xlsx)**. Manual conversion is not only inefficient but also error-prone, affecting the creative workflow.

**ScriptGrid** is a web-based format conversion tool designed to help audio description creators, translators, and team members easily and quickly convert between different formats of descriptive scripts, thereby greatly improving collaborative creation efficiency.

### Core Advantages

- 🌐 **No Installation Required** - Use directly through your browser
- ⚡ **Fast Conversion** - Efficient conversion engine for lightning-fast conversion experience
- 🎯 **Professional Customization** - Designed specifically for audio description creation scenarios
- ♿ **Accessibility Friendly** - Full support for keyboard operation and screen readers
- 🔒 **Privacy Protection** - Files are immediately destroyed by the server after processing, with no risk of leakage

## ✨ Main Features

### 🔄 Multi-directional File Conversion

- **Subtitle to Spreadsheet**: Convert `.ass` and `.srt` formats to structured `.xlsx` spreadsheets
- **Spreadsheet to Subtitle**: Convert standard format `.xlsx` spreadsheets to `.srt` format
- **Subtitle Format Interchange**: Convert `.ass` format to the more universal `.srt` format
- **SUP PGS Support**: Convert `.sup` format image subtitles to `.srt` or `.xlsx` formats
- **Auto Narration Timing**: Automatically analyzes dialogue subtitle files (SRT/ASS/SUP) to identify gaps without dialogue, generating narration subtitle timeline templates for audio description professionals

### ⚙️ Intelligent Recognition and Extraction

- Automatically recognize file types and dynamically display available conversion options
- Precisely extract key information such as **sequence number, start time, end time, subtitle content** from subtitle files
- Support for stripping effect tags from `.ass` files, preserving clean text content
- **SUP Image Recognition**: Automatically recognize image subtitles in SUP format using TorchfreeEasyOCR + ONNX Runtime technology
- **Intelligent Language Detection**: Automatically detect subtitle language (Chinese/English/Mixed) to optimize OCR recognition

### 🌐 Modern Web Experience

- **Responsive Design**: Interface adapts to different devices like desktop, tablet, and mobile
- **Intuitive Operation**: Drag and drop file upload, one-click conversion
- **Real-time Feedback**: Conversion progress prompts and result preview

## 🚀 Live Demo

You can directly visit the website below to start using immediately:

**[https://sg.kadaiad.fun:4680/](https://sg.kadaiad.fun:4680/)**

## 🏃 Quick Start

### Usage Steps

1. **Select File**: Click the "Select Subtitle File" button to upload your file (supports .ass, .srt, .xlsx, .sup formats)
2. **Choose Conversion Type**: The system will automatically recognize the file type and display available conversion options
3. **Start Conversion**: Click the "Start Conversion" button
4. **Download Result**: After conversion is complete, the file will automatically download to your device

### Supported Conversion Types

| Input Format | Output Format | Description |
|-------------|---------------|-------------|
| .ass | .srt | ASS subtitle to SRT format |
| .ass | .xlsx | ASS subtitle to Excel spreadsheet |
| .srt | .xlsx | SRT subtitle to Excel spreadsheet |
| .xlsx | .srt | Excel spreadsheet to SRT subtitle |
| .sup | .srt | SUP PGS subtitle to SRT format |
| .sup | .xlsx | SUP PGS subtitle to Excel spreadsheet |
| .srt/.ass/.sup | .srt | Auto Narration Timing - generates narration subtitle with placeholder text |

### Auto Narration Timing

**Usage:**
1. Upload dialogue subtitle file (supports SRT/ASS/SUP formats)
2. Select "Auto Narration Timing"
3. Automatically generates SRT narration subtitle with placeholder text

**Technical Details:**
- 500ms gap between narration and adjacent dialogue
- Minimum 1-second duration per narration entry, with no maximum limit

## 🛠️ Technical Architecture

This project adopts a modern web architecture with front-end and back-end separation, deployed through Docker containerization.

### Technology Stack

**Backend**
- **Language**: Python 3.13+
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance asynchronous web framework
- **Server**: [Uvicorn](https://www.uvicorn.org/) - ASGI server
- **Core Library**: [openpyxl](https://openpyxl.readthedocs.io/) - Excel file processing
- **OCR Recognition**: [TorchfreeEasyOCR](https://github.com/SeldonHZ/TorchfreeEasyOCR) + ONNX Runtime - High-performance image text recognition

**Frontend**
- **Foundation**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: [Bootstrap 5](https://getbootstrap.com/) - Responsive interface framework

**Deployment**
- **Containerization**: [Docker](https://www.docker.com/) - One-click deployment and operation

### Project Structure

```
ScriptGrid/
├── app.py                 # FastAPI main program entry
├── constants.py           # Global constants definition
├── exceptions.py          # Unified exception handling
├── parsers.py            # Subtitle file parsers
├── writers.py            # File writers
├── subtitle_converter.py # Core conversion logic
├── pgsreader.py          # SUP PGS file parser
├── imagemaker.py         # Image processing module
├── static/               # Static resources
│   └── index.html        # Frontend page
├── templates/            # Template files
├── Dockerfile            # Docker build file
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## 🏡 Local Deployment & Development

### Environment Requirements

- Python 3.13 or higher
- pip (Python package manager)
- Docker (optional, for containerized deployment)

### Method 1: Direct Python Execution (Development Environment)

1. **Clone Repository**
   ```bash
   git clone https://github.com/yunshenwuji/scriptgrid.git
   cd scriptgrid
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Service**
   ```bash
   python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   > The `--reload` parameter makes the service automatically restart after code changes, suitable for development environment

5. **Access Application**
   
   Open your browser and visit `http://127.0.0.1:8000`

### Method 2: Docker Deployment (Production Environment)

1. **Clone Repository** (if not already cloned)
   ```bash
   git clone https://github.com/yunshenwuji/scriptgrid.git
   cd scriptgrid
   ```

2. **Build Docker Image**
   ```bash
   docker build -t scriptgrid:latest .
   ```

3. **Run Docker Container**
   ```bash
   docker run -d -p 8000:8000 --name scriptgrid-app scriptgrid:latest
   ```
   
   Parameter explanation:
   - `-d`: Run container in background
   - `-p 8000:8000`: Port mapping (host:container)
   - `--name scriptgrid-app`: Container name

4. **Check Running Status**
   ```bash
   docker ps
   ```

5. **Access Application**
   
   Open your browser and visit `http://127.0.0.1:8000`

### Stop Service

**Python Method**: Press `Ctrl+C` in terminal

**Docker Method**:
```bash
# Stop container
docker stop scriptgrid-app

# Remove container
docker rm scriptgrid-app
```

## 🤝 Contributing Guide

We welcome community contributions! If you have good ideas or discover issues, please participate through the following ways:

### Report Issues

If you encounter problems during use, please:
1. Search in [GitHub Issues](https://github.com/yunshenwuji/scriptgrid/issues) to see if there are related issues
2. If not, please create a new Issue with detailed description of the problem and reproduction steps

### Submit Code

1. **Fork** this repository to your GitHub account
2. Create a feature branch: `git checkout -b feature/AmazingFeature`
3. Commit code: `git commit -m 'Add some AmazingFeature'`
4. Push branch: `git push origin feature/AmazingFeature`
5. Submit **Pull Request**

### Development Suggestions

- Before submitting code, please create an Issue to discuss your ideas
- Follow existing code style and naming conventions
- Add corresponding tests for new features
- Update relevant documentation

## 📝 Changelog

### v1.1.0 (Latest)
- ✨ Added SUP PGS subtitle format support
- ✨ Integrated TorchfreeEasyOCR technology for image subtitle recognition
- ✨ Automatic language detection to optimize Chinese and English subtitle recognition
- ✨ Support for .sup to .srt and .sup to .xlsx format conversion

### v1.0.0
- ✨ Support .ass/.srt to .xlsx format conversion
- ✨ Support .xlsx to .srt format conversion
- ✨ Support .ass to .srt format conversion
- 🌐 Responsive web interface
- ♿ Accessibility support
- 🐳 Docker containerized deployment

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 💬 Contact Us

- Project Homepage: [https://github.com/yunshenwuji/scriptgrid](https://github.com/yunshenwuji/scriptgrid)
- Issue Feedback: [GitHub Issues](https://github.com/yunshenwuji/scriptgrid/issues)
- Live Demo: [https://sg.kadaiad.fun:4680/](https://sg.kadaiad.fun:4680/)

## 💰 Support the Project

If you like ScriptGrid, donations are welcome  
Scan with Alipay or WeChat to buy me a coffee

<div align="center">
  <img src="../static/PayQrcode.png" alt="Alipay WeChat Payment QR Code" width="200">
</div>

---

⭐ If this project helps you, please give us a star!