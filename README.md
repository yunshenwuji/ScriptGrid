# 述格 (ScriptGrid)

![Python Version](https://img.shields.io/badge/Python-3.13+-blue.svg)![Framework](https://img.shields.io/badge/Framework-FastAPI-green.svg)
![Deployment](https://img.shields.io/badge/Deploy-Docker-blue.svg)
![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)**专为口述影像创作者打造的、轻量级在线口述稿格式转换工具。**

[**在线体验 (Live Demo)**](#-在线体验) | [**部署指南**](#-本地部署与开发)

---

## 📖 项目简介 (About The Project)在团队协作中，口述影像稿经常需要在**易于撰写和计时的字幕格式（如 .ass, .srt）**与**便于审阅、批注和管理的表格格式（.xlsx）**之间来回切换。手动转换不仅效率低下，还容易出错，影响创作流程。**述格 (ScriptGrid)** 正是为了解决这一痛点而生。它是一个基于 Web 的工具，旨在帮助口述影像创作者、译者和团队成员，轻松、快速地在不同格式的口述稿之间进行转换，从而极大地提升协同创作的效率。

## ✨ 主要功能 (Features)

述格 (ScriptGrid) 提供了简洁直观的操作界面和强大的核心转换功能：

-   **🔄 多向文件转换:** -   **字幕转表格**: 支持将 `.ass` 和 `.srt` 格式的口述稿转换为结构化的 `.xlsx` 表格。
    - **表格转字幕**: 支持将标准格式的 `.xlsx` 表格稿件转换回 `.srt` 格式，便于后期制作。 - **字幕格式互转**: 支持将 `.ass` 格式转换为更通用的 `.srt` 格式。-   **⚙️ 智能识别与提取:**
    -   自动、精确地提取字幕文件中的**序号、开始时间、结束时间、字幕内容**等关键信息。    - 支持从 `.ass` 文件中剥离特效标签，仅保留纯净的文本内容。

-   **🌐 现代 Web 体验:**    -   **无需安装**:通过浏览器即可直接访问使用，免去下载和安装桌面应用的烦恼。
    -   **响应式设计**: 界面自动适配桌面、平板和手机等不同尺寸的设备。 -   **动态交互**:上传文件后，系统会自动识别文件类型，并动态提供支持的转换选项。

-   **♿ 无障碍访问 (Accessibility):** - 界面完全支持键盘操作（Tab 切换，Enter/Space 激活）。
    -   为屏幕阅读器提供完整支持，确保所有用户都能顺畅使用。

## 🚀 在线体验 (Live Demo)

您可以直接访问下面的网址，立即开始使用：

**[https://sg.kadaiad.fun:4680/](https://sg.kadaiad.fun:4680/)**

## 🛠️ 技术架构 (Architecture & Tech Stack)

本项目采用前后端分离的现代化 Web 架构，并通过 Docker 进行容器化部署，确保了服务的可维护性、扩展性和部署的便捷性。-   **后端 (Backend):**
    -   **语言:** Python 3.13+
    -   **框架:** [FastAPI](https://fastapi.tiangolo.com/) -一个高性能的异步 Web 框架。
    - **服务器:** [Uvicorn](https://www.uvicorn.org/) - ASGI服务器，用于运行 FastAPI 应用。 -   **核心库:** [openpyxl](https://openpyxl.readthedocs.io/en/stable/) - 用于处理 `.xlsx` 文件的读写。-   **前端 (Frontend):** -   **基础:** HTML5, CSS3, JavaScript (ES6+)    - **UI 框架:** [Bootstrap 5](https://getbootstrap.com/) - 用于快速构建响应式和无障碍的界面。-   **部署 (Deployment):**    -   **容器化:** [Docker](https://www.docker.com/) - 将整个应用（包括环境和依赖）打包成一个独立的镜像，实现一键部署和运行。

## 🏡本地部署与开发 (Local Deployment & Development)您可以轻松地在本地或您自己的服务器上部署本项目。

### 先决条件 (Prerequisites)

-   Python 3.13 或更高版本
-   Pip (Python 包管理器)-   Docker (用于容器化部署)

### 方法一：直接通过 Python 运行 (适合开发)

1.  **克隆仓库**
    ```sh
    git clone https://github.com/yunshenwuji/scriptgrid.git
    cd scriptgrid    ```

2. **(推荐) 创建并激活虚拟环境**    ```sh    python -m venv venv # Windows
    .\venv\Scripts\activate # macOS/Linux
    source venv/bin/activate ```

3.  **安装依赖**    ```sh    pip install -r requirements.txt
    ```

4. **启动服务**    ```sh
    python -m uvicorn app:app --host 0.0.0.0 --port8000 --reload ```
    `--reload` 参数会使服务在代码变动后自动重启，非常适合开发环境。5.  **访问应用** 打开浏览器，访问 `http://127.0.0.1:8000`，即可看到应用界面。

### 方法二：通过 Docker 部署 (适合生产)

1. **克隆仓库** (如果尚未克隆) ```sh git clone https://github.com/yunshenwuji/scriptgrid.git
    cd scriptgrid    ```

2.  **构建 Docker 镜像** ```sh
    docker build -t scriptgrid:latest .    ```

3.  **查看本地镜像** (可选) ```sh docker images ```    您应该能看到名为 `scriptgrid` 且标签为 `latest` 的镜像。

4.  **运行 Docker 容器**
    ```sh    docker run -d -p 8000:8000 --name scriptgrid-app scriptgrid:latest ```
    - `-d`: 后台运行容器。 -   `-p 8000:8000`: 将主机的 8000 端口映射到容器的8000 端口。    -   `--name scriptgrid-app`:为容器指定一个友好的名称。

5.  **查看运行中的容器** (可选)    ```sh
    docker ps
    ```

6.  **访问应用**    同样地，打开浏览器访问 `http://127.0.0.1:8000` 即可使用。## 🤝 如何贡献 (Contributing)

我们非常欢迎社区的贡献！如果您有任何好的想法或发现了 Bug，请通过以下方式参与项目：

1. **Fork**本仓库。
2. 创建一个新的分支 (`git checkout -b feature/AmazingFeature`)。3.  提交您的代码 (`git commit -m 'Add some AmazingFeature'`)。
4. 将您的分支推送到远程仓库 (`git push origin feature/AmazingFeature`)。5.  提交一个 **Pull Request**。

在提交代码前，请先创建一个 Issue 来讨论您想要做的改动。

## 📄 许可证 (License)本项目基于 MIT 许可证。详情请见 `LICENSE` 文件。

---