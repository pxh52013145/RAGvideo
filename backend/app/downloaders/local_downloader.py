import os
import shutil
import subprocess
import uuid
from abc import ABC
from typing import Optional

from app.downloaders.base import Downloader
from app.enmus.note_enums import DownloadQuality
from app.models.audio_model import AudioDownloadResult
from app.utils.video_helper import save_cover_to_static
from app.utils.paths import backend_root, uploads_dir as get_uploads_dir


class LocalDownloader(Downloader, ABC):
    def __init__(self):

        super().__init__()

    @staticmethod
    def _needs_safe_path(input_path: str) -> bool:
        file_name = os.path.basename(input_path)
        try:
            file_name.encode("ascii")
            return False
        except UnicodeEncodeError:
            return True

    @staticmethod
    def _copy_to_safe_path(input_path: str) -> str:
        ext = os.path.splitext(input_path)[1] or ".mp4"
        safe_dir = get_uploads_dir() / "_safe"
        safe_dir.mkdir(parents=True, exist_ok=True)
        safe_path = safe_dir / f"{uuid.uuid4().hex}{ext}"
        shutil.copy2(input_path, str(safe_path))
        return str(safe_path)


    def extract_cover(self, input_path: str, output_dir: Optional[str] = None) -> str:
        """
        从本地视频文件中提取一张封面图（默认取第一帧）
        :param input_path: 输入视频路径
        :param output_dir: 输出目录，默认和视频同目录
        :return: 提取出的封面图片路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        if output_dir is None:
            output_dir = os.path.dirname(input_path)

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_cover.jpg")

        try:
            command = [
                'ffmpeg',
                '-i', input_path,
                '-ss', '00:00:01',  # 跳到视频第1秒，防止黑屏
                '-vframes', '1',  # 只截取一帧
                '-q:v', '2',  # 输出质量高一点（qscale，2是很高）
                '-y',  # 覆盖
                output_path
            ]
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            if not os.path.exists(output_path):
                raise RuntimeError(f"封面图片生成失败: {output_path}")

            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"提取封面失败: {output_path}") from e

    def convert_to_mp3(self,input_path: str, output_path: str = None) -> str:
        """
        将本地视频文件转为 MP3 音频文件
        :param input_path: 输入文件路径（如 .mp4）
        :param output_path: 输出文件路径（可选，默认同目录同名 .mp3）
        :return: 生成的 mp3 文件路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        if output_path is None:
            base, _ = os.path.splitext(input_path)
            output_path = base + ".mp3"
        try:
        # 调用 ffmpeg 转换
            command = [
                'ffmpeg',
                '-i', input_path,
                '-vn',  # 不要视频流
                '-acodec', 'libmp3lame',  # 使用mp3编码
                '-y',  # 覆盖输出文件
                output_path
            ]

            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            if not os.path.exists(output_path):
                raise RuntimeError(f"mp3 文件生成失败: {output_path}")

            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"mp3 文件生成失败: {output_path}") from e
    def download_video(self, video_url: str, output_dir: str = None) -> str:
        """
        处理本地文件路径，返回视频文件路径
        """
        if video_url.startswith('/uploads'):
            project_root = backend_root()
            video_url = os.path.normpath(str((project_root / video_url.lstrip('/')).resolve()))

        if not os.path.exists(video_url):
            raise FileNotFoundError()
        return video_url
    def download(
            self,
            video_url: str,
            output_dir: str = None,
            quality: DownloadQuality = "fast",
            need_video: Optional[bool] = False
    ) -> AudioDownloadResult:
        """
        处理本地文件路径，返回音频元信息
        """
        if video_url.startswith('/uploads'):
            project_root = backend_root()
            video_url = os.path.normpath(str((project_root / video_url.lstrip('/')).resolve()))

        if not os.path.exists(video_url):
            raise FileNotFoundError(f"本地文件不存在: {video_url}")

        file_name = os.path.basename(video_url)
        title, _ = os.path.splitext(file_name)
        print(title, file_name,video_url)

        working_path = video_url
        try:
            file_path = self.convert_to_mp3(working_path)
            cover_path = self.extract_cover(working_path)
        except RuntimeError:
            # Some Windows ffmpeg builds may fail to open non-ascii filenames.
            # Fallback: copy to an ascii-only path then retry.
            if not self._needs_safe_path(video_url):
                raise
            working_path = self._copy_to_safe_path(video_url)
            file_path = self.convert_to_mp3(working_path)
            cover_path = self.extract_cover(working_path)
        cover_url = save_cover_to_static(cover_path)

        print('file——path',file_path)
        return AudioDownloadResult(
            file_path=file_path,
            title=title,
            duration=0,  # 可选：后续加上读取时长
            cover_url=cover_url,  # 暂无封面
            platform="local",
            video_id=title,
            raw_info={
                'path':  file_path
            },
            video_path=None
        )
