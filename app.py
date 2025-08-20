# -*- coding: utf-8 -*-

"""
Web 应用后端主文件
使用 FastAPI 构建 Web 服务，提供文件上传和转换 API。
"""

import os
import tempfile
import shutil
import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the core conversion logic
import subtitle_converter
import exceptions

# --- FastAPI App Instance ---
app = FastAPI(
    title="述格 (ScriptGrid) Web API",
    description="提供字幕文件格式转换的 Web API",
    version="1.0.0"
)

# --- 配置 CORS (如果前端和后端部署在不同域) ---
# 允许所有来源，仅用于开发环境。生产环境应严格限制。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 静态文件和模板配置 ---
# 注意：确保 'templates' 和 'static' 目录与本文件在同一目录下
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static" # 可以存放 CSS, JS, 图片等

# 确保 templates 目录存在
if not TEMPLATES_DIR.exists():
    logger.warning(f"Templates directory '{TEMPLATES_DIR}' does not exist. Creating...")
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# 挂载静态文件目录 (如果存在)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    # 提供根路径的index.html
    @app.get("/")
    async def read_root():
        """
        根路径，提供前端主页面 index.html。
        """
        index_file_path = STATIC_DIR / "index.html"
        if not index_file_path.exists():
            logger.error(f"Frontend index.html file not found at {index_file_path}")
            raise HTTPException(status_code=404, detail="前端页面文件未找到。")
        return FileResponse(index_file_path)
else:
    logger.warning(f"Static directory '{STATIC_DIR}' not found. Frontend will not be served.")
    # 如果没有静态文件目录，仍然提供根路径访问templates中的index.html
    @app.get("/")
    async def read_root():
        """
        根路径，提供前端主页面 index.html。
        """
        index_file_path = TEMPLATES_DIR / "index.html"
        if not index_file_path.exists():
            logger.error(f"Frontend index.html file not found at {index_file_path}")
            raise HTTPException(status_code=404, detail="前端页面文件未找到。")
        return FileResponse(index_file_path)

# --- 静态文件路由 ---

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    提供 favicon.ico 文件。
    """
    favicon_path = STATIC_DIR / "favicon.ico"
    if not favicon_path.exists():
        logger.warning(f"Favicon file not found at {favicon_path}")
        raise HTTPException(status_code=404, detail="Favicon not found.")
    return FileResponse(favicon_path)

# --- API 路由 ---

@app.post("/api/convert")
async def convert_subtitle_file(
    file: UploadFile = File(...),
    conversion_type: str = Form(...),
    background_tasks: BackgroundTasks = None  # FastAPI 特殊注入类型
):
    """
    接收上传的字幕文件和转换类型，执行转换，并返回转换后的文件。
    
    Args:
        file (UploadFile): 用户上传的文件。
        conversion_type (str): 转换类型 ('subtitle_to_excel', 'ass_to_srt', 'xlsx_to_srt')。
        background_tasks (BackgroundTasks): FastAPI 的后台任务对象，用于延迟清理。
        
    Returns:
        FileResponse: 转换后的文件。
        
    Raises:
        HTTPException: 如果文件类型不支持、转换失败或发生其他错误。
    """
    logger.info(f"Received conversion request: type={conversion_type}, filename={file.filename}")
    
    # 1. 验证文件和转换类型
    if not file:
        logger.error("No file provided in the request.")
        raise HTTPException(status_code=400, detail="未提供文件。")

    if not conversion_type:
        logger.error("No conversion type provided in the request.")
        raise HTTPException(status_code=400, detail="未提供转换类型。")
        
    if conversion_type not in ['subtitle_to_excel', 'ass_to_srt', 'xlsx_to_srt']:
        logger.error(f"Unsupported conversion type provided: {conversion_type}")
        raise HTTPException(status_code=400, detail=f"不支持的转换类型: {conversion_type}")

    # 检查文件扩展名是否与转换类型精确匹配
    original_filename = file.filename
    original_stem = Path(original_filename).stem
    file_extension = Path(original_filename).suffix.lower()
    
    if conversion_type == 'subtitle_to_excel' and file_extension not in ['.ass', '.srt']:
        logger.error(f"File extension '{file_extension}' not supported for 'subtitle_to_excel'.")
        raise HTTPException(status_code=400, detail="字幕转表格功能仅支持 .ass 和 .srt 文件。")

    if conversion_type == 'ass_to_srt' and file_extension != '.ass':
        logger.error(f"File extension '{file_extension}' is invalid for 'ass_to_srt'.")
        raise HTTPException(status_code=400, detail="ASS 转 SRT 功能仅支持 .ass 文件。")

    if conversion_type == 'xlsx_to_srt' and file_extension != '.xlsx':
        logger.error(f"File extension '{file_extension}' is invalid for 'xlsx_to_srt'.")
        raise HTTPException(status_code=400, detail="表格转字幕功能仅支持 .xlsx 文件。")

    # 2. 创建临时目录用于存放上传和输出文件
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # 3. 保存上传的文件（使用安全的文件名）
        # 使用随机生成的安全文件名在服务器上保存文件
        secure_filename = f"{uuid.uuid4()}{file_extension}"
        input_file_path = temp_dir / secure_filename
        with input_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File saved to temporary location: {input_file_path}")

        # 4. 确定输出文件路径（使用原始文件名的词干）
        if conversion_type == 'subtitle_to_excel':
            output_file_name = f"{original_stem}.xlsx"
        else: # 'ass_to_srt' or 'xlsx_to_srt'
            output_file_name = f"{original_stem}.srt"
        
        output_file_path = temp_dir / output_file_name
        logger.info(f"Output file will be saved to: {output_file_path}")

        # 5. 调用核心转换逻辑
        subtitle_converter.convert(str(input_file_path), str(output_file_path), conversion_type)
        logger.info("Conversion completed successfully by core logic.")

        # 6. 检查输出文件是否存在
        if not output_file_path.exists():
            raise HTTPException(status_code=500, detail="转换过程未能生成输出文件。")

        # 7. 返回文件响应
        # 使用 FileResponse 直接返回文件，让浏览器处理下载
        # media_type 根据文件扩展名自动推断
        logger.info("Returning converted file for download.")
        
        # 将清理临时目录的任务添加到后台任务中
        # 这样可以确保文件被成功发送后再删除
        background_tasks.add_task(shutil.rmtree, temp_dir)
        logger.info(f"Scheduled cleanup for temporary directory: {temp_dir}")

        return FileResponse(
            path=str(output_file_path),
            filename=output_file_name,
            media_type='application/octet-stream' # 通用二进制流，浏览器通常会触发下载
        )

    except Exception as e:
        # 捕获所有可能的异常
        # 确保在任何失败的情况下都清理临时目录
        logger.error(f"An error occurred during conversion, cleaning up temp dir: {temp_dir}. Error: {e}")
        try:
            shutil.rmtree(temp_dir)
        except Exception as cleanup_error:
            logger.error(f"Failed to clean up temporary directory {temp_dir}: {cleanup_error}")
        
        # 根据异常类型，重新抛出合适的 HTTP 异常
        if isinstance(e, HTTPException):
            raise e
        if isinstance(e, exceptions.SubtitleConverterError):
            raise HTTPException(status_code=400, detail=f"转换失败: {str(e)}")
        
        raise HTTPException(status_code=500, detail=f"处理请求时发生未预期的错误: {str(e)}")



# --- 应用启动配置 ---
# 这部分代码在直接运行此脚本时生效 (例如: `uvicorn app:app --reload`)
# 如果使用 `if __name__ == "__main__":` 和 `uvicorn.run`，则需要额外的配置。
# 通常，我们会通过命令行 `uvicorn app:app --host 0.0.0.0 --port 8000` 来启动。
# 因此，这里不包含 `if __name__ == "__main__":` 块。
