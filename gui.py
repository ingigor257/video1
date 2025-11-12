# Instagram Video Uploader GUI - Full Version with Uniquifier Integration
import sys
import os
import json
import threading
import time
import subprocess
import random
import math
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QSlider, QComboBox,
    QCheckBox, QFileDialog, QMessageBox, QScrollArea, QFrame,
    QStackedWidget, QSpinBox, QDoubleSpinBox, QProgressBar, QTableWidget,
    QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect, QDialog,
    QListWidget, QListWidgetItem, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QVariantAnimation, QEasingCurve, QEvent
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QPixmap
from PyQt6.QtCore import QPoint

# Import our modules
from config import (
    logger, load_config, save_config, load_descriptions,
    get_proxy_status, toggle_proxy, update_proxy_settings, PROXY_HOST, PROXY_PORT,
    PROXY_USER, PROXY_PASS, PROXY_CHANGE_IP_URL
)
from core import (
    load_accounts, add_account, delete_account,
    sequential_upload_to_all_accounts, clear_all_sessions,
    change_avatars_for_accounts, get_avatar_files, edit_biographies_for_accounts,
    parse_accounts_from_file, import_accounts_from_file, validate_account_cookies,
    get_account_status, set_account_status
)

# === CSS STYLES ===
MAIN_STYLESHEET = """
QMainWindow {
    background-color: #0a0e1a;
}

QWidget {
    background-color: #0a0e1a;
    color: #e8eaf0;
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
}

/* Base Button Style */
QPushButton {
    background-color: #252b3d;
    color: #e8eaf0;
    border: 2px solid #2a3142;
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
    min-height: 40px;
    outline: none;
}

QPushButton:hover {
    background-color: #2d3548;
    border-color: #353c52;
}

QPushButton:pressed {
    background-color: #1e2433;
}

QPushButton:disabled {
    background-color: #1e2433;
    color: #5a6275;
    border-color: #2a3142;
}

QPushButton:focus {
    outline: none;
    border: 2px solid #2a3142;
}

/* Primary Action Buttons */
.btn-primary {
    background-color: #00994d;
    border: 2px solid #007a3d;
}

.btn-primary:hover {
    background-color: #00b35c;
    border: 2px solid #00994d;
}

/* Danger Buttons */
.btn-danger {
    background-color: #cc0033;
    border: 2px solid #990026;
}

.btn-danger:hover {
    background-color: #e6003d;
    border: 2px solid #cc0033;
}

/* Glass Card Style */
.glass-card {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1e2433, stop:1 #1a1f2e);
    border: 1px solid #2a3142;
    border-radius: 16px;
    padding: 20px;
}

/* Settings Input Frame */
.settings-input-frame {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #252b3d, stop:1 #1e2433);
    border: none;
    border-radius: 10px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.settings-input-frame:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2d3548, stop:1 #252b3d);
}

/* Sidebar */
.sidebar {
    background-color: #151a27;
    border-right: 1px solid #2a3142;
}

/* Text Inputs */
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
    background-color: #1a1f2e;
    color: #e8eaf0;
    border: 2px solid #2a3142;
    border-radius: 10px;
    padding: 10px 15px;
    font-size: 13px;
    selection-background-color: #00ccff;
}

QLineEdit:hover, QTextEdit:hover {
    border-color: #353c52;
    background-color: #1e2433;
}

QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #00ccff;
    background-color: #252b3d;
}

/* ComboBox */
QComboBox {
    background-color: #1a1f2e;
    color: #e8eaf0;
    border: 2px solid #2a3142;
    border-radius: 10px;
    padding: 10px 15px;
    font-size: 13px;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #353c52;
    background-color: #1e2433;
}

QComboBox:focus {
    border: 2px solid #00ccff;
    background-color: #252b3d;
}

QComboBox::drop-down {
    border: none;
    width: 35px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #e8eaf0;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #1e2433;
    color: #e8eaf0;
    selection-background-color: #00ccff;
    border: 2px solid #2a3142;
    border-radius: 10px;
    outline: none;
}

/* Sliders */
QSlider {
    background: transparent;
}

QSlider::groove:horizontal {
    height: 10px;
    background: #1a1f2e;
    border: none;
    border-radius: 5px;
}

QSlider::handle:horizontal {
    width: 20px;
    height: 20px;
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                                fx:0.5, fy:0.5,
                                stop:0 #00ffff, stop:1 #00ccff);
    border: none;
    border-radius: 10px;
    margin: -5px 0;
}

QSlider::handle:horizontal:hover {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                                fx:0.5, fy:0.5,
                                stop:0 #33ffff, stop:1 #00ddff);
    width: 20px;
    height: 20px;
    border-radius: 10px;
    margin: -5px 0;
}

QSlider::add-page:horizontal {
    background: #1a1f2e;
    border: none;
    border-radius: 5px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #00ccff, stop:0.5 #00ffcc, stop:1 #b026ff);
    border: none;
    border-radius: 5px;
}

/* CheckBox */
QCheckBox {
    spacing: 10px;
    color: #e8eaf0;
    font-size: 13px;
    background: transparent;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #2a3142;
    border-radius: 4px;
    background-color: #1a1f2e;
}

QCheckBox::indicator:hover {
    background-color: #252b3d;
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #00ffff, stop:1 #00ccff);
    border: 2px solid #00ccff;
}

QCheckBox::indicator:checked:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #33ffff, stop:1 #00ddff);
}

/* ScrollBar */
QScrollBar:vertical {
    background: transparent;
    width: 12px;
    border: none;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #2a3142;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #00ccff;
}

QScrollBar::add-line:vertical {
    height: 0px;
}

QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

/* Labels */
QLabel {
    color: #e8eaf0;
    background: transparent;
}

.label-title {
    font-size: 32px;
    font-weight: bold;
    color: #00ffff;
}

.label-section {
    font-size: 18px;
    font-weight: bold;
    color: #e8eaf0;
}

.label-secondary {
    color: #8b92a8;
    font-size: 13px;
}

.label-muted {
    color: #5a6275;
    font-size: 11px;
}

/* Status Indicators */
.status-ready {
    color: #00ccff;
}

.status-working {
    color: #ffaa00;
}

.status-success {
    color: #00cc66;
}

/* Progress Bar */
QProgressBar {
    background-color: #252b3d;
    border: 1px solid #2a3142;
    border-radius: 8px;
    text-align: center;
    color: #e8eaf0;
    height: 25px;
}

QProgressBar::chunk {
    background-color: #00ffff;
    border-radius: 7px;
}

/* Tables */
QTableWidget {
    background-color: #1a1f2e;
    border: 2px solid #2a3142;
    border-radius: 10px;
    gridline-color: #2a3142;
    selection-background-color: #00ccff;
    selection-color: #ffffff;
    outline: none;
}

QTableWidget::item {
    padding: 12px 15px;
    color: #e8eaf0;
    border: none;
    background-color: transparent;
}

QTableWidget::item:hover {
    background-color: #252b3d;
}

QTableWidget::item:selected {
    background-color: #00ccff;
    color: #ffffff;
}

QTableWidget::item:selected:hover {
    background-color: #33ffff;
}

QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2d3548, stop:1 #252b3d);
    color: #00ffff;
    padding: 12px 15px;
    border: none;
    border-bottom: 2px solid #00ccff;
    font-weight: bold;
    font-size: 13px;
    text-transform: uppercase;
}

QHeaderView::section:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #353c52, stop:1 #2d3548);
}
"""


class GlowButton(QPushButton):
    """Кнопка с анимированным свечением"""
    def __init__(self, text, parent=None, glow=True):
        super().__init__(text, parent)
        self.glow_enabled = glow

        self.gradient_colors = [
            QColor('#ff0000'), QColor('#ff7300'), QColor('#fffb00'),
            QColor('#48ff00'), QColor('#00ffd5'), QColor('#002bff'),
            QColor('#7a00ff'), QColor('#ff00c8'), QColor('#ff0000'),
        ]

        self.gradient_position = 0.0
        self.glow_opacity = 0.0

        if self.glow_enabled:
            self.shadow_effect = QGraphicsDropShadowEffect(self)
            self.shadow_effect.setBlurRadius(30)
            self.shadow_effect.setOffset(0, 0)
            self.shadow_effect.setColor(QColor(255, 0, 0, 0))
            self.setGraphicsEffect(self.shadow_effect)

            self.gradient_timer = QTimer(self)
            self.gradient_timer.timeout.connect(self._animate_gradient)
            self.gradient_timer.setInterval(50)

            self.fade_animation = QVariantAnimation(self)
            self.fade_animation.setDuration(300)
            self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.fade_animation.valueChanged.connect(self._update_glow_opacity)

    def enterEvent(self, event):
        if self.glow_enabled and self.isEnabled():
            self.fade_animation.setStartValue(0.0)
            self.fade_animation.setEndValue(1.0)
            self.fade_animation.start()
            self.gradient_timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.glow_enabled:
            self.fade_animation.setStartValue(self.glow_opacity)
            self.fade_animation.setEndValue(0.0)
            self.fade_animation.start()
            self.gradient_timer.stop()
        super().leaveEvent(event)

    def _update_glow_opacity(self, value):
        self.glow_opacity = value
        self._update_gradient_color()

    def _get_gradient_color_at_position(self, position):
        num_colors = len(self.gradient_colors) - 1
        color_position = (position * num_colors / 4.0) % num_colors
        color_index = int(color_position)
        next_index = (color_index + 1) % len(self.gradient_colors)
        t = color_position - color_index
        color1 = self.gradient_colors[color_index]
        color2 = self.gradient_colors[next_index]
        r = int(color1.red() + (color2.red() - color1.red()) * t)
        g = int(color1.green() + (color2.green() - color1.green()) * t)
        b = int(color1.blue() + (color2.blue() - color1.blue()) * t)
        return QColor(r, g, b)

    def _update_gradient_color(self):
        if self.glow_enabled:
            color = self._get_gradient_color_at_position(self.gradient_position)
            alpha = int(255 * self.glow_opacity)
            glow_color = QColor(color.red(), color.green(), color.blue(), alpha)
            self.shadow_effect.setColor(glow_color)

    def _animate_gradient(self):
        speed = 0.01
        self.gradient_position += speed
        if self.gradient_position >= 4.0:
            self.gradient_position = 0.0
        self._update_gradient_color()


class ProcessThread(QThread):
    """Thread для обработки видео уникализатором"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, config, selected_videos=None):
        super().__init__()
        self.config = config
        self.selected_videos = selected_videos  # Список выбранных видео (только имена файлов)
        self.stop_requested = False

    def run(self):
        try:
            self.log_signal.emit("🎬 Запуск уникализатора видео...")
            self.log_signal.emit(f"📂 Входная папка: {self.config.get('input_folder', 'unik/input')}")
            self.log_signal.emit(f"📂 Выходная папка: {self.config.get('output_folder', 'video1')}")
            self.log_signal.emit(f"🎵 Добавлять музыку: {'Да' if self.config.get('add_music', True) else 'Нет'}")
            self.log_signal.emit(f"📊 Копий на видео: {self.config.get('copies_per_video', 5)}")

            input_folder = self.config.get('input_folder', 'unik/input')
            output_folder = self.config.get('output_folder', 'video1')
            music_folder = self.config.get('music_folder', 'unik/music')

            # Clean output folder
            if os.path.exists(output_folder):
                import shutil
                shutil.rmtree(output_folder)
            os.makedirs(output_folder, exist_ok=True)
            self.log_signal.emit("🧹 Папка output очищена")

            # Get video and music files
            all_input_videos = self.get_video_files(input_folder)

            # Фильтруем видео если указаны selected_videos
            if self.selected_videos:
                input_videos = [v for v in all_input_videos if os.path.basename(v) in self.selected_videos]
                self.log_signal.emit(f"📝 Обработка выбранных видео: {len(input_videos)} из {len(all_input_videos)}")
            else:
                input_videos = all_input_videos

            music_videos = self.get_audio_files(music_folder) if self.config.get('add_music', True) else []

            if not input_videos:
                self.log_signal.emit(f"❌ Нет видео в папке: {input_folder}")
                return

            if self.config.get('add_music', True) and not music_videos:
                self.log_signal.emit(f"❌ Нет музыки в папке: {music_folder}")
                return

            self.log_signal.emit(f"\nИсходных видео: {len(input_videos)}")
            if self.config.get('add_music', True):
                self.log_signal.emit(f"Музыкальных треков: {len(music_videos)}")
            else:
                self.log_signal.emit("Музыка: ВЫКЛЮЧЕНО (оригинальный звук сохраняется)")
            self.log_signal.emit(f"Будет создано: {len(input_videos) * self.config.get('copies_per_video', 5)} видео ({self.config.get('copies_per_video', 5)} копий на видео)\n")

            # Show angle-zoom mapping
            self.log_signal.emit("Angle-to-Zoom Mapping:")
            for angle, zoom in sorted(self.config.get('angle_zoom_map', {}).items(), key=lambda x: int(x[0])):
                angle_int = int(angle)
                zoom_float = float(zoom)
                self.log_signal.emit(f"  {angle_int:+3d}° → {zoom_float:.4f}x zoom ({(zoom_float-1)*100:.1f}% crop)")
            self.log_signal.emit("")

            processed_count = 0
            failed_count = 0

            # Process each video
            for i, input_video in enumerate(input_videos, 1):
                if self.stop_requested:
                    self.log_signal.emit("\n⏹ ОСТАНОВЛЕНО")
                    break

                for j in range(1, self.config.get('copies_per_video', 5) + 1):
                    if self.stop_requested:
                        break

                    music_video = random.choice(music_videos) if self.config.get('add_music', True) and music_videos else None

                    output_filename = f"{i}.{j}.mp4"
                    output_path = os.path.join(output_folder, output_filename)

                    if self.uniquify_video(input_video, music_video, output_path):
                        processed_count += 1
                    else:
                        failed_count += 1

            if not self.stop_requested:
                self.log_signal.emit("\n" + "="*85)
                self.log_signal.emit(f"◈ ОБРАБОТКА ЗАВЕРШЕНА")
                self.log_signal.emit("="*85)
                self.log_signal.emit(f"✦ Успешно: {processed_count}")
                self.log_signal.emit(f"✧ Ошибок: {failed_count}")
                self.log_signal.emit(f"◈ Всего: {processed_count + failed_count}")
                self.log_signal.emit("="*85)

            self.log_signal.emit("✅ Уникализация завершена!")
        except Exception as e:
            self.log_signal.emit(f"❌ Ошибка уникализации: {e}")
            import traceback
            self.log_signal.emit(f"Подробности: {traceback.format_exc()}")
        finally:
            self.finished_signal.emit()

    def get_video_files(self, folder):
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
        files = {}
        try:
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in video_extensions:
                        key = filepath.lower()
                        files[key] = filepath
        except:
            pass
        return sorted(files.values())

    def get_audio_files(self, folder):
        audio_extensions = ['.mp3', '.wav', '.aac', '.m4a', '.ogg', '.flac', '.mp4', '.mov', '.avi', '.mkv']
        files = {}
        try:
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in audio_extensions:
                        key = filepath.lower()
                        files[key] = filepath
        except:
            pass
        return sorted(files.values())

    def get_video_resolution(self, video_path):
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "json",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            width = data['streams'][0]['width']
            height = data['streams'][0]['height']
            return width, height
        except:
            return 1920, 1080

    def get_random_filters(self):
        filters = []
        effects = self.config.get('effects_settings', {})

        if random.random() < effects.get('color_balance_probability', 0.7):
            range_val = effects.get('color_balance_range', 0.05)
            rs = random.uniform(-range_val, range_val)
            gs = random.uniform(-range_val, range_val)
            bs = random.uniform(-range_val, range_val)
            rm = random.uniform(-range_val, range_val)
            gm = random.uniform(-range_val, range_val)
            bm = random.uniform(-range_val, range_val)
            filters.append(f"colorbalance=rs={rs:.3f}:gs={gs:.3f}:bs={bs:.3f}:rm={rm:.3f}:gm={gm:.3f}:bm={bm:.3f}")

        if random.random() < effects.get('brightness_contrast_probability', 0.5):
            brightness = random.uniform(-effects.get('brightness_range', 0.02), effects.get('brightness_range', 0.02))
            contrast = random.uniform(effects.get('contrast_min', 0.98), effects.get('contrast_max', 1.02))
            filters.append(f"eq=brightness={brightness:.3f}:contrast={contrast:.3f}")

        if random.random() < effects.get('saturation_probability', 0.5):
            saturation = random.uniform(effects.get('saturation_min', 0.95), effects.get('saturation_max', 1.05))
            filters.append(f"eq=saturation={saturation:.3f}")

        return filters

    def uniquify_video(self, input_video, music_video, output_video):
        try:
            orig_w, orig_h = self.get_video_resolution(input_video)

            angle_zoom_map = {int(k): v for k, v in self.config.get('angle_zoom_map', {}).items()}
            angle_degrees = random.choice(list(angle_zoom_map.keys()))
            zoom_factor = angle_zoom_map[angle_degrees]
            angle_radians = angle_degrees * math.pi / 180

            mirror_prob = self.config.get('effects_settings', {}).get('mirror_probability', 0.5)
            mirror = random.random() < mirror_prob

            video_settings = self.config.get('video_settings', {})
            resolution = video_settings.get('output_resolution', '1080x1920').split('x')
            output_width = int(resolution[0])
            output_height = int(resolution[1])

            filter_parts = []
            filter_parts.append(f"rotate={angle_radians:.6f}:fillcolor=black")

            zoom_w = int(orig_w / zoom_factor)
            zoom_h = int(orig_h / zoom_factor)
            zoom_w = zoom_w if zoom_w % 2 == 0 else zoom_w - 1
            zoom_h = zoom_h if zoom_h % 2 == 0 else zoom_h - 1
            filter_parts.append(f"crop={zoom_w}:{zoom_h}:(iw-{zoom_w})/2:(ih-{zoom_h})/2")

            filter_parts.append(f"scale={output_width}:{output_height}:force_original_aspect_ratio=decrease")
            filter_parts.append(f"pad={output_width}:{output_height}:(ow-iw)/2:(oh-ih)/2:color=black")

            if mirror:
                filter_parts.append("hflip")

            random_filters = self.get_random_filters()
            filter_parts.extend(random_filters)

            video_filter = ",".join(filter_parts)

            add_music = self.config.get('add_music', True)

            temp_video = output_video if not add_music else output_video.replace('.mp4', '_temp.mp4')

            cmd1 = [
                "ffmpeg",
                "-hide_banner", "-loglevel", "error",
                "-i", input_video,
                "-filter:v", video_filter,
                "-c:v", video_settings.get('video_codec', 'libx264'),
                "-preset", video_settings.get('video_preset', 'veryfast'),
                "-crf", str(video_settings.get('video_crf', 23)),
                "-pix_fmt", video_settings.get('pixel_format', 'yuv420p'),
            ]

            if add_music:
                cmd1.append("-an")
            else:
                cmd1.extend(["-c:a", video_settings.get('audio_codec', 'aac'), "-b:a", video_settings.get('audio_bitrate', '128k')])

            cmd1.extend(["-y", temp_video])

            subprocess.run(cmd1, check=True)

            if add_music and music_video:
                cmd2 = [
                    "ffmpeg",
                    "-hide_banner", "-loglevel", "error",
                    "-i", temp_video,
                    "-i", music_video,
                    "-c:v", "copy",
                    "-c:a", video_settings.get('audio_codec', 'aac'),
                    "-b:a", video_settings.get('audio_bitrate', '128k'),
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-shortest",
                    "-map_metadata", "-1",
                    "-movflags", "+faststart",
                    "-y",
                    output_video
                ]

                subprocess.run(cmd2, check=True)
                if os.path.exists(temp_video):
                    os.remove(temp_video)

            mirror_str = "🔀" if mirror else "  "
            music_str = "🎵" if add_music else "🔇"
            self.log_signal.emit(f"✓ {os.path.basename(output_video)} | Angle: {angle_degrees:+3d}° | Zoom: {zoom_factor:.4f}x | Mirror: {mirror_str} | Music: {music_str}")
            return True
        except Exception as e:
            self.log_signal.emit(f"✗ {os.path.basename(output_video)} | Error: {str(e)}")
            if 'temp_video' in locals() and os.path.exists(temp_video):
                os.remove(temp_video)
            return False


class UploadThread(QThread):
    """Thread для загрузки видео на Instagram"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    refresh_table_signal = pyqtSignal()  # Новый сигнал для обновления таблицы

    def __init__(self, accounts, descriptions, config):
        super().__init__()
        self.accounts = accounts
        self.descriptions = descriptions
        self.config = config

    def run(self):
        try:
            self.log_signal.emit("📤 Начинаем загрузку на Instagram...")

            def callback(msg):
                self.log_signal.emit(msg)
                # Обновляем таблицу при каждом сообщении (будет обновляться при изменении статуса)
                self.refresh_table_signal.emit()

            sequential_upload_to_all_accounts(
                self.accounts,
                self.descriptions,
                self.config,
                callback=callback
            )
            self.log_signal.emit("✅ Загрузка завершена!")
        except Exception as e:
            self.log_signal.emit(f"❌ Ошибка загрузки: {e}")
        finally:
            self.finished_signal.emit()

class StatisticsThread(QThread):
    """Thread для получения статистики рилсов"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    stats_signal = pyqtSignal(dict)

    def __init__(self, accounts, selected_username, num_clips):
        super().__init__()
        self.accounts = accounts
        self.selected_username = selected_username
        self.num_clips = num_clips

    def run(self):
        try:
            from core import get_clips_statistics

            self.log_signal.emit(f"📊 Получение статистики...")
            if self.selected_username:
                self.log_signal.emit(f"📊 Аккаунт: @{self.selected_username}")
            else:
                self.log_signal.emit(f"📊 Получение для всех {len(self.accounts)} аккаунтов...")

            self.log_signal.emit(f"📊 Количество рилсов: {self.num_clips}")

            statistics = get_clips_statistics(
                self.accounts,
                selected_username=self.selected_username,
                num_clips=self.num_clips
            )

            self.stats_signal.emit(statistics)
            self.log_signal.emit("✅ Статистика получена!")
        except Exception as e:
            self.log_signal.emit(f"❌ Ошибка получения статистики: {e}")
            import traceback
            self.log_signal.emit(f"Traceback: {traceback.format_exc()}")
        finally:
            self.finished_signal.emit()


class ImportAccountsDialog(QDialog):
    """Диалог для импорта аккаунтов из файла"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parsed_accounts = []
        self.selected_indices = []
        self.file_path = None
        self.setWindowTitle("Импорт аккаунтов из файла")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("📥 Импорт аккаунтов из файла")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ffff; margin-bottom: 10px;")
        layout.addWidget(title)

        # Выбор файла
        file_card = QFrame()
        file_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e2433, stop:1 #1a1f2e);
                border: 1px solid #2a3142;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        file_layout = QVBoxLayout(file_card)

        file_label = QLabel("Выберите файл с аккаунтами:")
        file_label.setStyleSheet("font-size: 14px; color: #e8eaf0; font-weight: bold;")
        file_layout.addWidget(file_label)

        file_select_layout = QHBoxLayout()
        self.file_path_label = QLabel("Файл не выбран")
        self.file_path_label.setStyleSheet("color: #8b92a8; font-size: 12px;")
        file_select_layout.addWidget(self.file_path_label)

        select_file_btn = QPushButton("📁 Выбрать файл")
        select_file_btn.setStyleSheet("background-color: #00994d; color: white; padding: 8px 15px; border-radius: 6px; font-weight: bold;")
        select_file_btn.clicked.connect(self.select_file)
        file_select_layout.addWidget(select_file_btn)

        file_layout.addLayout(file_select_layout)
        layout.addWidget(file_card)

        # Список аккаунтов
        accounts_label = QLabel("Аккаунты в файле:")
        accounts_label.setStyleSheet("font-size: 14px; color: #e8eaf0; font-weight: bold; margin-top: 10px;")
        layout.addWidget(accounts_label)

        self.account_list = QListWidget()
        self.account_list.setStyleSheet("""
            QListWidget {
                background-color: #141824;
                border: 2px solid #2a3142;
                border-radius: 8px;
                padding: 10px;
                color: #e8eaf0;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 4px;
                border: 1px solid transparent;
            }
            QListWidget::item:hover {
                background-color: #1a1f2e;
                border: 1px solid #353c52;
            }
            QListWidget::item:selected {
                background-color: #2a3142;
                border: 1px solid #00ccff;
            }
        """)
        layout.addWidget(self.account_list)

        # Кнопки выбора
        select_buttons = QHBoxLayout()

        select_all_btn = QPushButton("✓ Выбрать все")
        select_all_btn.setStyleSheet("background-color: #007a3d; color: white; padding: 8px 15px; border-radius: 6px; font-weight: bold;")
        select_all_btn.clicked.connect(self.select_all)
        select_buttons.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("✗ Снять все")
        deselect_all_btn.setStyleSheet("background-color: #cc0033; color: white; padding: 8px 15px; border-radius: 6px; font-weight: bold;")
        deselect_all_btn.clicked.connect(self.deselect_all)
        select_buttons.addWidget(deselect_all_btn)

        layout.addLayout(select_buttons)

        # Опции импорта
        options_card = QFrame()
        options_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e2433, stop:1 #1a1f2e);
                border: 1px solid #2a3142;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        options_layout = QVBoxLayout(options_card)

        # Выбор режима импорта
        mode_label = QLabel("📋 Режим импорта:")
        mode_label.setStyleSheet("color: #00ffff; font-size: 14px; font-weight: bold; margin-bottom: 5px;")
        options_layout.addWidget(mode_label)

        from PyQt6.QtWidgets import QRadioButton, QButtonGroup
        self.import_mode_group = QButtonGroup()

        self.mode_login_password = QRadioButton("🔑 Логин:Пароль (авторизация через Instagram)")
        self.mode_login_password.setStyleSheet("color: #e8eaf0; font-size: 13px; font-weight: bold;")
        self.import_mode_group.addButton(self.mode_login_password, 1)
        options_layout.addWidget(self.mode_login_password)

        mode_login_hint = QLabel("Скрипт будет использовать только логин и пароль, игнорируя cookies. Потребуется авторизация в Instagram.")
        mode_login_hint.setStyleSheet("color: #8b92a8; font-size: 11px; margin-left: 25px;")
        mode_login_hint.setWordWrap(True)
        options_layout.addWidget(mode_login_hint)

        self.mode_cookies = QRadioButton("🍪 Cookies (быстрый вход с готовой сессией)")
        self.mode_cookies.setStyleSheet("color: #e8eaf0; font-size: 13px; font-weight: bold; margin-top: 10px;")
        self.mode_cookies.setChecked(True)  # По умолчанию
        self.import_mode_group.addButton(self.mode_cookies, 2)
        options_layout.addWidget(self.mode_cookies)

        mode_cookies_hint = QLabel("Скрипт будет использовать сохранённые cookies для быстрого входа без повторной авторизации.")
        mode_cookies_hint.setStyleSheet("color: #8b92a8; font-size: 11px; margin-left: 25px; margin-bottom: 15px;")
        mode_cookies_hint.setWordWrap(True)
        options_layout.addWidget(mode_cookies_hint)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #2a3142; max-height: 1px;")
        options_layout.addWidget(separator)

        self.validate_checkbox = QCheckBox("✓ Проверять валидность аккаунтов при импорте")
        self.validate_checkbox.setChecked(True)
        self.validate_checkbox.setStyleSheet("color: #e8eaf0; font-size: 13px; font-weight: bold; margin-top: 10px;")
        options_layout.addWidget(self.validate_checkbox)

        validate_hint = QLabel("Проверка валидности может занять некоторое время, но гарантирует, что будут добавлены только рабочие аккаунты")
        validate_hint.setStyleSheet("color: #8b92a8; font-size: 11px; margin-left: 25px;")
        validate_hint.setWordWrap(True)
        options_layout.addWidget(validate_hint)

        layout.addWidget(options_card)

        # Кнопки действий
        buttons = QHBoxLayout()

        import_btn = QPushButton("📥 Импортировать выбранные")
        import_btn.setStyleSheet("background-color: #00cc66; color: white; padding: 12px 30px; border-radius: 6px; font-weight: bold; font-size: 14px;")
        import_btn.clicked.connect(self.import_accounts)
        buttons.addWidget(import_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("background-color: #6b7280; color: white; padding: 12px 30px; border-radius: 6px; font-weight: bold; font-size: 14px;")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)

    def select_file(self):
        """Выбор файла с аккаунтами"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл с аккаунтами",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )

        if file_path:
            self.file_path = file_path
            self.file_path_label.setText(file_path)
            self.file_path_label.setStyleSheet("color: #00cc66; font-size: 12px; font-weight: bold;")
            self.load_accounts_from_file()

    def load_accounts_from_file(self):
        """Загрузка и парсинг аккаунтов из файла"""
        if not self.file_path:
            return

        try:
            self.parsed_accounts = parse_accounts_from_file(self.file_path)
            self.account_list.clear()

            if not self.parsed_accounts:
                QMessageBox.warning(self, "Ошибка", "Не найдено аккаунтов в файле или неверный формат")
                return

            for i, acc in enumerate(self.parsed_accounts):
                username = acc['username']
                phone = acc.get('phone', 'N/A')
                cookies_count = len(acc.get('cookies', {}))

                # Добавляем номер аккаунта
                item_text = f"#{i + 1} | 👤 {username}"

                # Показываем тип аккаунта
                if cookies_count > 0:
                    item_text += f" | 🍪 {cookies_count} cookies"
                else:
                    item_text += " | 🔑 login:password"

                if phone and phone != 'N/A':
                    item_text += f" | 📱 {phone}"

                item = QListWidgetItem(item_text)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked)  # По умолчанию все выбраны
                self.account_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке файла: {str(e)}")

    def select_all(self):
        """Выбрать все аккаунты"""
        for i in range(self.account_list.count()):
            self.account_list.item(i).setCheckState(Qt.CheckState.Checked)

    def deselect_all(self):
        """Снять выбор со всех аккаунтов"""
        for i in range(self.account_list.count()):
            self.account_list.item(i).setCheckState(Qt.CheckState.Unchecked)

    def import_accounts(self):
        """Импорт выбранных аккаунтов"""
        if not self.file_path:
            QMessageBox.warning(self, "Ошибка", "Выберите файл с аккаунтами")
            return

        # Получаем индексы выбранных аккаунтов
        self.selected_indices = []
        for i in range(self.account_list.count()):
            item = self.account_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                self.selected_indices.append(i)

        if not self.selected_indices:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один аккаунт для импорта")
            return

        self.accept()

    def get_import_data(self):
        """Получить данные для импорта"""
        # Определяем режим импорта
        use_cookies = self.mode_cookies.isChecked()

        return {
            'file_path': self.file_path,
            'selected_indices': self.selected_indices,
            'validate': self.validate_checkbox.isChecked(),
            'use_cookies': use_cookies  # True = cookies, False = login:password
        }


class AccountSelectionDialog(QDialog):
    """Диалог для выбора аккаунтов"""
    def __init__(self, accounts, parent=None):
        super().__init__(parent)
        self.accounts = accounts
        self.selected_accounts = []
        self.setWindowTitle("Выбор аккаунтов")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel("Выберите аккаунты для загрузки:")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ffff; margin-bottom: 10px;")
        layout.addWidget(title)

        # Список аккаунтов с чекбоксами
        self.account_list = QListWidget()
        self.account_list.setStyleSheet("""
            QListWidget {
                background-color: #141824;
                border: 1px solid #2a3142;
                border-radius: 8px;
                padding: 10px;
                color: #e8eaf0;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #1a1f2e;
            }
            QListWidget::item:selected {
                background-color: #2a3142;
            }
        """)

        for account in self.accounts:
            item = QListWidgetItem(f"👤 {account['username']}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.account_list.addItem(item)

        layout.addWidget(self.account_list)

        # Кнопки выбора
        select_buttons = QHBoxLayout()

        select_all_btn = QPushButton("✓ Выбрать все")
        select_all_btn.setStyleSheet("background-color: #007a3d; color: white; padding: 8px; border-radius: 4px;")
        select_all_btn.clicked.connect(self.select_all)
        select_buttons.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("✗ Снять все")
        deselect_all_btn.setStyleSheet("background-color: #8b0000; color: white; padding: 8px; border-radius: 4px;")
        deselect_all_btn.clicked.connect(self.deselect_all)
        select_buttons.addWidget(deselect_all_btn)

        layout.addLayout(select_buttons)

        # Кнопки действий
        buttons = QHBoxLayout()

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("background-color: #00cc66; color: white; padding: 10px 30px; border-radius: 4px; font-weight: bold;")
        ok_btn.clicked.connect(self.accept_selection)
        buttons.addWidget(ok_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("background-color: #6b7280; color: white; padding: 10px 30px; border-radius: 4px;")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)

    def select_all(self):
        for i in range(self.account_list.count()):
            self.account_list.item(i).setCheckState(Qt.CheckState.Checked)

    def deselect_all(self):
        for i in range(self.account_list.count()):
            self.account_list.item(i).setCheckState(Qt.CheckState.Unchecked)

    def accept_selection(self):
        self.selected_accounts = []
        for i in range(self.account_list.count()):
            item = self.account_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                self.selected_accounts.append(self.accounts[i])
        self.accept()

    def get_selected_accounts(self):
        return self.selected_accounts


class VideoSelectionDialog(QDialog):
    """Диалог для выбора видео с предпросмотром обложек"""
    def __init__(self, video_folder, video_files, parent=None):
        super().__init__(parent)
        self.video_folder = video_folder
        self.video_files = video_files
        self.selected_videos = []
        self.setWindowTitle("Выбор видео для уникализации")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel("Выберите видео для уникализации:")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ffff; margin-bottom: 10px;")
        layout.addWidget(title)

        # Скролл область для видео
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #0d1117;
                border: 1px solid #2a3142;
                border-radius: 8px;
            }
        """)

        # Контейнер для сетки видео
        video_container = QWidget()
        self.video_grid = QGridLayout(video_container)
        self.video_grid.setSpacing(15)

        # Создаем карточки для каждого видео
        self.video_checkboxes = []
        row, col = 0, 0
        max_cols = 3

        for video_file in self.video_files:
            video_card = self.create_video_card(video_file)
            self.video_grid.addWidget(video_card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        scroll.setWidget(video_container)
        layout.addWidget(scroll)

        # Кнопки выбора
        select_buttons = QHBoxLayout()

        select_all_btn = QPushButton("✓ Выбрать все")
        select_all_btn.setStyleSheet("background-color: #007a3d; color: white; padding: 8px; border-radius: 4px;")
        select_all_btn.clicked.connect(self.select_all)
        select_buttons.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("✗ Снять все")
        deselect_all_btn.setStyleSheet("background-color: #8b0000; color: white; padding: 8px; border-radius: 4px;")
        deselect_all_btn.clicked.connect(self.deselect_all)
        select_buttons.addWidget(deselect_all_btn)

        layout.addLayout(select_buttons)

        # Кнопки действий
        buttons = QHBoxLayout()

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("background-color: #00cc66; color: white; padding: 10px 30px; border-radius: 4px; font-weight: bold;")
        ok_btn.clicked.connect(self.accept_selection)
        buttons.addWidget(ok_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("background-color: #6b7280; color: white; padding: 10px 30px; border-radius: 4px;")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)

    def create_video_card(self, video_file):
        """Создать карточку видео с обложкой"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #141824;
                border: 2px solid #2a3142;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #00ffff;
            }
        """)
        card.setMinimumWidth(220)
        card.setMaximumWidth(250)

        card_layout = QVBoxLayout(card)

        # Чекбокс
        checkbox = QCheckBox(video_file)
        checkbox.setStyleSheet("""
            QCheckBox {
                color: #e8eaf0;
                font-size: 12px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #2a3142;
                border-radius: 4px;
                background-color: #0d1117;
            }
            QCheckBox::indicator:checked {
                background-color: #00cc66;
                border-color: #00cc66;
            }
        """)
        self.video_checkboxes.append((checkbox, video_file))
        card_layout.addWidget(checkbox)

        # Превью обложки
        thumbnail_label = QLabel()
        thumbnail_label.setMinimumHeight(150)
        thumbnail_label.setMaximumHeight(180)
        thumbnail_label.setStyleSheet("""
            QLabel {
                background-color: #0d1117;
                border: 1px solid #2a3142;
                border-radius: 4px;
                color: #6b7280;
                text-align: center;
            }
        """)
        thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Генерируем превью
        video_path = os.path.join(self.video_folder, video_file)
        thumbnail = self.generate_thumbnail(video_path)

        if thumbnail:
            thumbnail_label.setPixmap(thumbnail)
            thumbnail_label.setScaledContents(True)
        else:
            thumbnail_label.setText("🎬\nВидео")

        card_layout.addWidget(thumbnail_label)

        # Информация о файле
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        info_label = QLabel(f"📊 {file_size:.1f} MB")
        info_label.setStyleSheet("color: #6b7280; font-size: 11px; margin-top: 5px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(info_label)

        return card

    def generate_thumbnail(self, video_path):
        """Генерация превью видео"""
        try:
            from PyQt6.QtGui import QPixmap, QImage
            import subprocess
            import tempfile

            # Создаем временный файл для скриншота
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp_path = tmp.name

            # Используем ffmpeg для извлечения кадра
            cmd = [
                'ffmpeg', '-i', video_path,
                '-ss', '00:00:01',  # 1 секунда от начала
                '-vframes', '1',
                '-vf', 'scale=220:-1',
                '-y', tmp_path
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=5)

            if result.returncode == 0 and os.path.exists(tmp_path):
                pixmap = QPixmap(tmp_path)
                os.remove(tmp_path)
                return pixmap

            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return None

        except Exception as e:
            return None

    def select_all(self):
        for checkbox, _ in self.video_checkboxes:
            checkbox.setChecked(True)

    def deselect_all(self):
        for checkbox, _ in self.video_checkboxes:
            checkbox.setChecked(False)

    def accept_selection(self):
        self.selected_videos = []
        for checkbox, video_file in self.video_checkboxes:
            if checkbox.isChecked():
                self.selected_videos.append(video_file)
        self.accept()

    def get_selected_videos(self):
        return self.selected_videos


class InstagramUploaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("◈ INSTAGRAM UPLOADER PRO ◈")
        self.setGeometry(100, 100, 1700, 950)

        # Change working directory to script location
        script_dir = Path(__file__).parent.absolute()
        os.chdir(script_dir)
        logger.info(f"Рабочая директория установлена: {script_dir}")

        # Load configuration
        self.config_file = Path("instagram_config.json")
        self.config = self.load_config()

        # Create required folders
        self.create_required_folders()

        # Processing state
        self.is_running = False
        self.stop_requested = False
        self.accounts = load_accounts()
        self.descriptions = load_descriptions()

        # Threads
        self.process_thread = None
        self.upload_thread = None
        self.statistics_thread = None

        # Sliders list
        self.sliders = []

        # Apply stylesheet
        self.setStyleSheet(MAIN_STYLESHEET)

        # Setup UI
        self.setup_ui()

        # Install event filter on sliders
        for slider in self.sliders:
            slider.installEventFilter(self)

        # Log working directory and file counts
        self.log(f"📂 Рабочая директория: {script_dir}")
        self.log(f"📊 Найдено аккаунтов: {len(self.accounts)}")

        # Count files
        input_videos = len([f for f in os.listdir("unik/input") if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]) if os.path.exists("unik/input") else 0
        music_files = len([f for f in os.listdir("unik/music") if f.endswith(('.mp3', '.wav', '.m4a'))]) if os.path.exists("unik/music") else 0

        self.log(f"🎬 Входных видео: {input_videos}")
        self.log(f"🎵 Музыкальных треков: {music_files}")

        # Update thumbnail count
        self.update_thumbnail_count()

        self.log("✅ Приложение готово к работе!")

    def create_required_folders(self):
        """Create required folders if they don't exist"""
        required_folders = [
            self.config.get('input_folder', 'unik/input'),
            self.config.get('output_folder', 'video1'),
            self.config.get('music_folder', 'unik/music'),
            'ava',  # Папка для аватарок
            'oblo'  # Папка для обложек видео
        ]
        for folder in required_folders:
            os.makedirs(folder, exist_ok=True)
            logger.info(f"Проверена/создана папка: {folder}")

    def open_folder_safe(self, folder_path):
        """Safely open folder in file explorer"""
        try:
            # Ensure folder exists
            os.makedirs(folder_path, exist_ok=True)
            # Open folder
            os.startfile(folder_path)
        except Exception as e:
            self.log(f"❌ Ошибка открытия папки {folder_path}: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть папку:\n{folder_path}\n\nОшибка: {e}")

    def open_file_safe(self, file_path):
        """Safely open file"""
        try:
            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                self.log(f"⚠️ Файл не найден: {file_path}")
                QMessageBox.warning(self, "Файл не найден", f"Файл не существует:\n{file_path}\n\nПожалуйста, создайте его сначала.")
        except Exception as e:
            self.log(f"❌ Ошибка открытия файла {file_path}: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл:\n{file_path}\n\nОшибка: {e}")

    def add_checkmark_to_checkbox(self, checkbox):
        """Добавить визуальную галочку к чекбоксу"""
        original_paint = checkbox.paintEvent

        def paint_with_checkmark(event):
            original_paint(event)
            if checkbox.isChecked():
                painter = QPainter(checkbox)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                pen = QPen(QColor(255, 255, 255), 2.2)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)

                # Draw checkmark (centered in the box)
                # Short line (left part of checkmark)
                painter.drawLine(QPoint(5, 10), QPoint(8, 13))
                # Long line (right part of checkmark)
                painter.drawLine(QPoint(8, 13), QPoint(15, 6))
                painter.end()

        checkbox.paintEvent = paint_with_checkmark

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel and isinstance(obj, QSlider):
            return True
        return super().eventFilter(obj, event)

    def load_config(self):
        """Load configuration from file"""
        default_config = {
            'input_folder': 'unik/input',
            'output_folder': 'video1',
            'music_folder': 'unik/music',
            'add_music': True,
            'copies_per_video': 5,
            'add_hashtags': False,
            'angle_zoom_map': {
                '-3': 1.085, '-2': 1.05, '-1': 1.025,
                '1': 1.025, '2': 1.05, '3': 1.085
            },
            'video_settings': {
                'output_resolution': '1080x1920',
                'video_codec': 'libx264',
                'video_preset': 'veryfast',
                'video_crf': 23,
                'audio_codec': 'aac',
                'audio_bitrate': '128k',
                'pixel_format': 'yuv420p'
            },
            'effects_settings': {
                'mirror_probability': 0.5,
                'color_balance_probability': 0.7,
                'brightness_contrast_probability': 0.5,
                'saturation_probability': 0.5,
                'color_balance_range': 0.05,
                'brightness_range': 0.02,
                'contrast_min': 0.98,
                'contrast_max': 1.02,
                'saturation_min': 0.95,
                'saturation_max': 1.05
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    config = default_config.copy()
                    config.update(loaded)
                    return config
            except:
                pass
        return default_config

    def save_config_to_file(self):
        """Save configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Sidebar
        self.create_sidebar(main_layout)

        # Content stack
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)

        # Create sections
        self.create_dashboard_section()
        self.create_accounts_section()
        self.create_proxy_section()
        self.create_uniquifier_settings_section()
        self.create_reels_downloader_section()
        self.create_input_video_manager_section()
        self.create_instagram_settings_section()
        self.create_statistics_section()
        self.create_console_section()

        # Show dashboard
        self.show_section(0)

    def create_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setProperty("class", "sidebar")
        sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 20)
        sidebar_layout.setSpacing(20)

        # Title
        title_frame = QFrame()
        title_frame.setProperty("class", "glass-card")
        title_layout = QVBoxLayout(title_frame)

        title = QLabel("◈ INSTAGRAM\nUPLOADER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #00ffff;")
        title_layout.addWidget(title)
        sidebar_layout.addWidget(title_frame)

        # Status
        status_frame = QFrame()
        status_frame.setProperty("class", "glass-card")
        status_layout = QHBoxLayout(status_frame)
        self.status_label = QLabel("● ГОТОВА")
        self.status_label.setProperty("class", "status-ready")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        status_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(status_frame)

        sidebar_layout.addSpacing(20)

        # Navigation
        nav_items = [
            ("📊 Dashboard", 0),
            ("👥 Аккаунты", 1),
            ("🌐 Прокси", 2),
            ("🎬 Уникализатор", 3),
            ("⬇️ Загрузка рилсов", 4),
            ("📂 Менеджер видео", 5),
            ("⚙️ Instagram", 6),
            ("📈 Статистика", 7),
            ("📝 Консоль", 8),
        ]

        self.nav_buttons = []
        for text, index in nav_items:
            btn = GlowButton(text, glow=True)
            btn.setMinimumHeight(50)
            btn.clicked.connect(lambda checked, idx=index: self.show_section(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addSpacing(20)

        # Statistics
        stats_frame = QFrame()
        stats_frame.setProperty("class", "glass-card")
        stats_layout = QVBoxLayout(stats_frame)

        stats_title = QLabel("◈ СТАТИСТИКА")
        stats_title.setProperty("class", "label-secondary")
        stats_layout.addWidget(stats_title)

        self.stat_labels = {}
        stats_data = [
            ("Аккаунтов", "accounts", "#00cc66"),
            ("Видео", "videos", "#00ccff"),
            ("Прокси", "proxy", "#b026ff"),
        ]

        for label_text, key, color in stats_data:
            stat_row = QHBoxLayout()
            label = QLabel(label_text)
            label.setProperty("class", "label-muted")
            value = QLabel("0")
            value.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
            stat_row.addWidget(label)
            stat_row.addStretch()
            stat_row.addWidget(value)
            stats_layout.addLayout(stat_row)
            self.stat_labels[key] = value

        sidebar_layout.addWidget(stats_frame)
        sidebar_layout.addStretch()

        parent_layout.addWidget(sidebar)

        # Update stats
        self.update_stats()

    def create_dashboard_section(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        layout.setSpacing(20)

        # Header
        header = QLabel("◈ ПАНЕЛЬ УПРАВЛЕНИЯ")
        header.setProperty("class", "label-title")
        layout.addWidget(header)

        # Statistics cards
        stats_row = QHBoxLayout()
        self.dashboard_stats = {}

        stat_cards = [
            ("Аккаунтов", "accounts_dash", "#00ffff"),
            ("Входных видео", "input_videos", "#b026ff"),
            ("Музыкальных треков", "music_tracks", "#00cc66"),
            ("Будет создано", "output_videos", "#ffaa00"),
        ]

        for label_text, key, color in stat_cards:
            card = self.create_stat_card(label_text, "0", color)
            stats_row.addWidget(card)
            self.dashboard_stats[key] = card.findChild(QLabel, "value")

        layout.addLayout(stats_row)

        # Main controls card
        control_card = QFrame()
        control_card.setProperty("class", "glass-card")
        control_layout = QVBoxLayout(control_card)

        control_title = QLabel("◈ БЫСТРЫЙ ЗАПУСК")
        control_title.setProperty("class", "label-section")
        control_layout.addWidget(control_title)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.process_btn = QPushButton("🎬 УНИКАЛИЗИРОВАТЬ")
        self.process_btn.setProperty("class", "btn-primary")
        self.process_btn.setMinimumHeight(60)
        self.process_btn.clicked.connect(self.start_uniquifier)
        buttons_layout.addWidget(self.process_btn)

        self.upload_btn = QPushButton("📤 ЗАГРУЗИТЬ НА INSTAGRAM")
        self.upload_btn.setProperty("class", "btn-primary")
        self.upload_btn.setMinimumHeight(60)
        self.upload_btn.clicked.connect(self.start_upload)
        buttons_layout.addWidget(self.upload_btn)

        control_layout.addLayout(buttons_layout)

        self.all_in_one_btn = QPushButton("⚡ ВСЁ СРАЗУ (Уникализация + Загрузка)")
        self.all_in_one_btn.setProperty("class", "btn-primary")
        self.all_in_one_btn.setStyleSheet("background-color: #007a3d; font-size: 16px;")
        self.all_in_one_btn.setMinimumHeight(60)
        self.all_in_one_btn.clicked.connect(self.start_all_in_one)
        control_layout.addWidget(self.all_in_one_btn)

        # Дополнительные кнопки выбора
        additional_buttons_layout = QHBoxLayout()

        self.selective_unique_btn = QPushButton("🎞️ УНИКАЛИЗИРОВАТЬ ВЫБРАННЫЕ")
        self.selective_unique_btn.setProperty("class", "btn-primary")
        self.selective_unique_btn.setStyleSheet("background-color: #9d4edd; font-size: 14px;")
        self.selective_unique_btn.setMinimumHeight(50)
        self.selective_unique_btn.clicked.connect(self.start_selective_uniquify)
        additional_buttons_layout.addWidget(self.selective_unique_btn)

        self.selective_upload_btn = QPushButton("📮 ЗАГРУЗИТЬ НА ВЫБРАННЫЕ")
        self.selective_upload_btn.setProperty("class", "btn-primary")
        self.selective_upload_btn.setStyleSheet("background-color: #f72585; font-size: 14px;")
        self.selective_upload_btn.setMinimumHeight(50)
        self.selective_upload_btn.clicked.connect(self.start_selective_upload)
        additional_buttons_layout.addWidget(self.selective_upload_btn)

        control_layout.addLayout(additional_buttons_layout)

        self.stop_btn = QPushButton("⏹ ОСТАНОВИТЬ")
        self.stop_btn.setProperty("class", "btn-danger")
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_processing)
        control_layout.addWidget(self.stop_btn)

        layout.addWidget(control_card)

        # Progress card
        progress_card = QFrame()
        progress_card.setProperty("class", "glass-card")
        progress_layout = QVBoxLayout(progress_card)

        progress_title = QLabel("◈ ПРОГРЕСС")
        progress_title.setProperty("class", "label-section")
        progress_layout.addWidget(progress_title)

        self.current_video_label = QLabel("Ожидание...")
        self.current_video_label.setProperty("class", "label-secondary")
        self.current_video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.current_video_label)

        layout.addWidget(progress_card)

        layout.addStretch()

        scroll.setWidget(dashboard)
        self.content_stack.addWidget(scroll)

    def create_stat_card(self, title, value, color):
        """Create statistics card for dashboard"""
        card = QFrame()
        card.setProperty("class", "glass-card")
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel(title)
        title_label.setProperty("class", "label-secondary")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet(f"color: {color}; font-size: 40px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(value_label)

        return card

    def create_accounts_section(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        accounts = QWidget()
        layout = QVBoxLayout(accounts)
        layout.setSpacing(20)

        # Header
        header = QLabel("◈ УПРАВЛЕНИЕ АККАУНТАМИ")
        header.setProperty("class", "label-title")
        layout.addWidget(header)

        # Add account card
        add_card = QFrame()
        add_card.setProperty("class", "glass-card")
        add_layout = QVBoxLayout(add_card)

        add_title = QLabel("◈ Добавить аккаунт")
        add_title.setProperty("class", "label-section")
        add_layout.addWidget(add_title)

        self.acc_username_input = QLineEdit()
        self.acc_username_input.setPlaceholderText("Instagram Username")
        add_layout.addWidget(self.acc_username_input)

        self.acc_password_input = QLineEdit()
        self.acc_password_input.setPlaceholderText("Instagram Password")
        self.acc_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        add_layout.addWidget(self.acc_password_input)

        add_btn = QPushButton("➕ Добавить аккаунт")
        add_btn.setProperty("class", "btn-primary")
        add_btn.clicked.connect(self.add_account_clicked)
        add_layout.addWidget(add_btn)

        # Quick add button for format: username:password||cookies|||phone
        quick_add_btn = QPushButton("⚡ Быстрое добавление (логин:пароль||cookies|||телефон)")
        quick_add_btn.setProperty("class", "btn-primary")
        quick_add_btn.setStyleSheet("background-color: #9900cc; border: 2px solid #7700a3;")
        quick_add_btn.clicked.connect(self.quick_add_account_clicked)
        add_layout.addWidget(quick_add_btn)

        # Import accounts button
        import_btn = QPushButton("📥 Импортировать из файла")
        import_btn.setProperty("class", "btn-primary")
        import_btn.setStyleSheet("background-color: #0066cc; border: 2px solid #0052a3;")
        import_btn.clicked.connect(self.import_accounts_clicked)
        add_layout.addWidget(import_btn)

        layout.addWidget(add_card)

        # Accounts list card
        list_card = QFrame()
        list_card.setProperty("class", "glass-card")
        list_layout = QVBoxLayout(list_card)

        list_title = QLabel(f"◈ Список аккаунтов ({len(self.accounts)})")
        list_title.setProperty("class", "label-section")
        list_layout.addWidget(list_title)

        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(4)
        self.accounts_table.setHorizontalHeaderLabels(["#", "USERNAME", "СТАТУС", "ОШИБКА"])

        # Улучшенные настройки таблицы
        self.accounts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.accounts_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.accounts_table.setShowGrid(False)
        self.accounts_table.setAlternatingRowColors(False)
        self.accounts_table.verticalHeader().setVisible(False)
        self.accounts_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Настройка заголовков
        header = self.accounts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # #
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # USERNAME
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # СТАТУС
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # ОШИБКА
        self.accounts_table.setColumnWidth(1, 200)
        header.setMinimumHeight(45)

        # Настройка высоты строк
        self.accounts_table.verticalHeader().setDefaultSectionSize(50)

        self.refresh_accounts_table()
        list_layout.addWidget(self.accounts_table)

        # Buttons row 1
        buttons_layout1 = QHBoxLayout()

        delete_btn = QPushButton("🗑️ Удалить выбранный")
        delete_btn.setProperty("class", "btn-danger")
        delete_btn.clicked.connect(self.delete_selected_account)
        buttons_layout1.addWidget(delete_btn)

        clear_sessions_btn = QPushButton("🧹 Очистить все сессии")
        clear_sessions_btn.setProperty("class", "btn-danger")
        clear_sessions_btn.clicked.connect(self.clear_all_sessions_clicked)
        buttons_layout1.addWidget(clear_sessions_btn)

        list_layout.addLayout(buttons_layout1)

        # Buttons row 2
        buttons_layout2 = QHBoxLayout()

        validate_btn = QPushButton("✓ Проверить валидность")
        validate_btn.setStyleSheet("background-color: #ff9900; border: 2px solid #cc7700; color: white; padding: 10px; border-radius: 10px; font-weight: bold;")
        validate_btn.clicked.connect(self.validate_accounts_clicked)
        buttons_layout2.addWidget(validate_btn)

        list_layout.addLayout(buttons_layout2)

        layout.addWidget(list_card)
        layout.addStretch()

        scroll.setWidget(accounts)
        self.content_stack.addWidget(scroll)

    def create_proxy_section(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        proxy_widget = QWidget()
        layout = QVBoxLayout(proxy_widget)
        layout.setSpacing(20)

        # Header
        header = QLabel("◈ НАСТРОЙКИ ПРОКСИ")
        header.setProperty("class", "label-title")
        layout.addWidget(header)

        # Proxy toggle card
        toggle_card = QFrame()
        toggle_card.setProperty("class", "glass-card")
        toggle_layout = QVBoxLayout(toggle_card)

        toggle_title = QLabel("◈ Статус прокси")
        toggle_title.setProperty("class", "label-section")
        toggle_layout.addWidget(toggle_title)

        proxy_status_layout = QHBoxLayout()
        self.proxy_status_label = QLabel("Прокси ВКЛЮЧЕН" if get_proxy_status() else "Прокси ВЫКЛЮЧЕН")
        self.proxy_status_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {'#00cc66' if get_proxy_status() else '#ff0055'};")
        proxy_status_layout.addWidget(self.proxy_status_label)
        proxy_status_layout.addStretch()

        self.proxy_toggle_btn = QPushButton("🔄 Переключить")
        self.proxy_toggle_btn.setProperty("class", "btn-primary")
        self.proxy_toggle_btn.clicked.connect(self.toggle_proxy_clicked)
        proxy_status_layout.addWidget(self.proxy_toggle_btn)

        toggle_layout.addLayout(proxy_status_layout)
        layout.addWidget(toggle_card)

        # Proxy settings card
        settings_card = QFrame()
        settings_card.setProperty("class", "glass-card")
        settings_layout = QVBoxLayout(settings_card)

        settings_title = QLabel("◈ Настройки прокси")
        settings_title.setProperty("class", "label-section")
        settings_layout.addWidget(settings_title)

        # Host
        host_layout = QHBoxLayout()
        host_label = QLabel("Host:")
        host_label.setMinimumWidth(130)
        host_layout.addWidget(host_label)
        self.proxy_host_input = QLineEdit(PROXY_HOST)
        self.proxy_host_input.setPlaceholderText("Введите IP или домен")
        host_layout.addWidget(self.proxy_host_input)
        settings_layout.addLayout(host_layout)

        # Port
        port_layout = QHBoxLayout()
        port_label = QLabel("Port:")
        port_label.setMinimumWidth(130)
        port_layout.addWidget(port_label)
        self.proxy_port_input = QLineEdit(PROXY_PORT)
        self.proxy_port_input.setPlaceholderText("Введите порт")
        port_layout.addWidget(self.proxy_port_input)
        settings_layout.addLayout(port_layout)

        # User
        user_layout = QHBoxLayout()
        user_label = QLabel("User:")
        user_label.setMinimumWidth(130)
        user_layout.addWidget(user_label)
        self.proxy_user_input = QLineEdit(PROXY_USER)
        self.proxy_user_input.setPlaceholderText("Введите логин")
        user_layout.addWidget(self.proxy_user_input)
        settings_layout.addLayout(user_layout)

        # Password
        pass_layout = QHBoxLayout()
        pass_label = QLabel("Password:")
        pass_label.setMinimumWidth(130)
        pass_layout.addWidget(pass_label)
        self.proxy_pass_input = QLineEdit(PROXY_PASS)
        self.proxy_pass_input.setPlaceholderText("Введите пароль")
        self.proxy_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(self.proxy_pass_input)
        settings_layout.addLayout(pass_layout)

        # Change IP URL
        url_layout = QHBoxLayout()
        url_label = QLabel("Change IP URL:")
        url_label.setMinimumWidth(130)
        url_layout.addWidget(url_label)
        self.proxy_url_input = QLineEdit(PROXY_CHANGE_IP_URL)
        self.proxy_url_input.setPlaceholderText("Введите URL для смены IP")
        url_layout.addWidget(self.proxy_url_input)
        settings_layout.addLayout(url_layout)

        # Save button
        save_proxy_btn = QPushButton("💾 Сохранить настройки")
        save_proxy_btn.setProperty("class", "btn-primary")
        save_proxy_btn.setMinimumHeight(40)
        save_proxy_btn.clicked.connect(self.save_proxy_settings)
        settings_layout.addWidget(save_proxy_btn)

        layout.addWidget(settings_card)

        # IP change card
        ip_card = QFrame()
        ip_card.setProperty("class", "glass-card")
        ip_layout = QVBoxLayout(ip_card)

        ip_title = QLabel("◈ Смена IP")
        ip_title.setProperty("class", "label-section")
        ip_layout.addWidget(ip_title)

        change_ip_btn = QPushButton("🔄 Сменить IP сейчас")
        change_ip_btn.setProperty("class", "btn-primary")
        change_ip_btn.setMinimumHeight(50)
        change_ip_btn.clicked.connect(self.change_ip_now)
        ip_layout.addWidget(change_ip_btn)

        layout.addWidget(ip_card)
        layout.addStretch()

        scroll.setWidget(proxy_widget)
        self.content_stack.addWidget(scroll)

    def create_uniquifier_settings_section(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        layout.setSpacing(20)

        # Header
        header = QLabel("◈ НАСТРОЙКИ УНИКАЛИЗАТОРА")
        header.setProperty("class", "label-title")
        layout.addWidget(header)

        # Folders card
        folders_card = QFrame()
        folders_card.setProperty("class", "glass-card")
        folders_layout = QVBoxLayout(folders_card)

        folders_title = QLabel("◈ Папки")
        folders_title.setProperty("class", "label-section")
        folders_layout.addWidget(folders_title)

        # Input folder
        input_layout = QHBoxLayout()
        input_label = QLabel("Входные видео:")
        input_layout.addWidget(input_label)
        input_btn = QPushButton("📁 unik/input")
        input_btn.clicked.connect(lambda: self.open_folder_safe("unik/input"))
        input_layout.addWidget(input_btn)
        folders_layout.addLayout(input_layout)

        # Music folder
        music_layout_row = QHBoxLayout()
        music_label = QLabel("Музыка:")
        music_layout_row.addWidget(music_label)
        music_btn = QPushButton("🎵 unik/music")
        music_btn.clicked.connect(lambda: self.open_folder_safe("unik/music"))
        music_layout_row.addWidget(music_btn)
        folders_layout.addLayout(music_layout_row)

        # Output folder
        output_layout = QHBoxLayout()
        output_label = QLabel("Выходные видео:")
        output_layout.addWidget(output_label)
        output_btn = QPushButton("📂 video1")
        output_btn.clicked.connect(lambda: self.open_folder_safe("video1"))
        output_layout.addWidget(output_btn)
        folders_layout.addLayout(output_layout)

        layout.addWidget(folders_card)

        # Copies card
        copies_card = QFrame()
        copies_card.setProperty("class", "glass-card")
        copies_layout = QVBoxLayout(copies_card)

        copies_title = QLabel("◈ Количество копий на видео")
        copies_title.setProperty("class", "label-section")
        copies_layout.addWidget(copies_title)

        self.create_slider_input(copies_layout, "Копий на видео", "copies_per_video", 1, 20)

        layout.addWidget(copies_card)

        # Add music switch
        music_card = QFrame()
        music_card.setProperty("class", "glass-card")
        music_layout = QVBoxLayout(music_card)

        self.add_music_checkbox = QCheckBox("Добавлять музыку к видео")
        self.add_music_checkbox.setChecked(self.config.get("add_music", True))
        self.add_music_checkbox.setStyleSheet("font-size: 14px;")
        self.add_music_checkbox.stateChanged.connect(self.auto_save_uniquifier_settings)
        self.add_checkmark_to_checkbox(self.add_music_checkbox)
        music_layout.addWidget(self.add_music_checkbox)

        layout.addWidget(music_card)

        # Angle-zoom mapping card
        angles_card = QFrame()
        angles_card.setProperty("class", "glass-card")
        angles_layout = QVBoxLayout(angles_card)

        angles_title = QLabel("◈ Углы и зумы (Angle-to-Zoom Mapping)")
        angles_title.setProperty("class", "label-section")
        angles_layout.addWidget(angles_title)

        angles_info = QLabel("Каждому углу соответствует свой зум, чтобы скрыть углы после поворота")
        angles_info.setProperty("class", "label-muted")
        angles_info.setWordWrap(True)
        angles_layout.addWidget(angles_info)

        # Get default angle_zoom_map
        default_angle_zoom = {
            '-3': 1.085, '-2': 1.05, '-1': 1.025,
            '1': 1.025, '2': 1.05, '3': 1.085
        }
        angle_zoom_map = self.config.get('angle_zoom_map', default_angle_zoom)

        self.angle_entries = {}
        for angle_str in ['-3', '-2', '-1', '1', '2', '3']:
            angle_int = int(angle_str)
            angle_row = QFrame()
            angle_row.setProperty("class", "settings-input-frame")
            angle_row_layout = QHBoxLayout(angle_row)
            angle_row_layout.setContentsMargins(15, 12, 15, 12)

            label = QLabel(f"Угол {angle_int:+d}° Zoom:")
            label.setMinimumWidth(150)
            angle_row_layout.addWidget(label)

            entry = QLineEdit()
            entry.setText(str(angle_zoom_map.get(angle_str, 1.0)))
            entry.setMaximumWidth(100)
            entry.setPlaceholderText("1.0")
            angle_row_layout.addWidget(entry)
            angle_row_layout.addStretch()

            angles_layout.addWidget(angle_row)
            self.angle_entries[angle_str] = entry

        layout.addWidget(angles_card)

        # Video settings card
        video_card = QFrame()
        video_card.setProperty("class", "glass-card")
        video_layout = QVBoxLayout(video_card)

        video_title = QLabel("◈ Настройки видео")
        video_title.setProperty("class", "label-section")
        video_layout.addWidget(video_title)

        # Get default video settings
        default_video_settings = {
            'output_resolution': '1080x1920',
            'video_codec': 'libx264',
            'video_preset': 'veryfast',
            'video_crf': 23,
            'audio_codec': 'aac',
            'audio_bitrate': '128k',
            'pixel_format': 'yuv420p'
        }
        video_settings = self.config.get('video_settings', default_video_settings)

        self.create_dropdown_input(video_layout, "Разрешение выхода", "output_resolution",
                                   ["1920x1080", "1280x720", "720x1280", "1080x1920"],
                                   video_settings.get('output_resolution', '1080x1920'))
        self.create_dropdown_input(video_layout, "Видеокодек", "video_codec",
                                   ["libx264", "libx265", "libvpx-vp9"],
                                   video_settings.get('video_codec', 'libx264'))
        self.create_dropdown_input(video_layout, "Preset", "video_preset",
                                   ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
                                   video_settings.get('video_preset', 'veryfast'))
        self.create_slider_input(video_layout, "CRF (качество)", "video_crf", 0, 51, step=1, in_effects=False)
        self.create_dropdown_input(video_layout, "Аудиокодек", "audio_codec",
                                   ["aac", "libmp3lame", "libopus"],
                                   video_settings.get('audio_codec', 'aac'))
        self.create_dropdown_input(video_layout, "Битрейт аудио", "audio_bitrate",
                                   ["128k", "192k", "256k", "320k"],
                                   video_settings.get('audio_bitrate', '128k'))
        self.create_dropdown_input(video_layout, "Pixel Format", "pixel_format",
                                   ["yuv420p", "yuv444p", "rgb24"],
                                   video_settings.get('pixel_format', 'yuv420p'))

        layout.addWidget(video_card)

        # Effects settings card
        effects_card = QFrame()
        effects_card.setProperty("class", "glass-card")
        effects_layout = QVBoxLayout(effects_card)

        effects_title = QLabel("◈ Настройки эффектов")
        effects_title.setProperty("class", "label-section")
        effects_layout.addWidget(effects_title)

        self.create_slider_input(effects_layout, "Вероятность зеркала", "mirror_probability", 0, 1, step=0.1, in_effects=True)
        self.create_slider_input(effects_layout, "Вероятность цветокоррекции", "color_balance_probability", 0, 1, step=0.1, in_effects=True)
        self.create_slider_input(effects_layout, "Вероятность яркость/контраст", "brightness_contrast_probability", 0, 1, step=0.1, in_effects=True)
        self.create_slider_input(effects_layout, "Вероятность насыщенности", "saturation_probability", 0, 1, step=0.1, in_effects=True)

        layout.addWidget(effects_card)

        # Advanced effects card
        advanced_effects_card = QFrame()
        advanced_effects_card.setProperty("class", "glass-card")
        advanced_effects_layout = QVBoxLayout(advanced_effects_card)

        advanced_title = QLabel("◈ Расширенные настройки эффектов")
        advanced_title.setProperty("class", "label-section")
        advanced_effects_layout.addWidget(advanced_title)

        self.create_slider_input(advanced_effects_layout, "Диапазон цветокоррекции", "color_balance_range", 0, 0.1, step=0.01, in_effects=True)
        self.create_slider_input(advanced_effects_layout, "Диапазон яркости", "brightness_range", 0, 0.1, step=0.01, in_effects=True)

        # Range inputs for contrast and saturation
        default_effects = {
            'contrast_min': 0.98,
            'contrast_max': 1.02,
            'saturation_min': 0.95,
            'saturation_max': 1.05
        }
        effects_settings = self.config.get('effects_settings', default_effects)

        self.create_range_input(advanced_effects_layout, "Диапазон контраста", "contrast_min", "contrast_max",
                               effects_settings.get('contrast_min', 0.98),
                               effects_settings.get('contrast_max', 1.02))
        self.create_range_input(advanced_effects_layout, "Диапазон насыщенности", "saturation_min", "saturation_max",
                               effects_settings.get('saturation_min', 0.95),
                               effects_settings.get('saturation_max', 1.05))

        layout.addWidget(advanced_effects_card)
        layout.addStretch()

        scroll.setWidget(settings_widget)
        self.content_stack.addWidget(scroll)

    def create_reels_downloader_section(self):
        """Create section for downloading Instagram reels"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        downloader_widget = QWidget()
        layout = QVBoxLayout(downloader_widget)
        layout.setSpacing(20)

        # Header
        header = QLabel("◈ ЗАГРУЗКА INSTAGRAM REELS")
        header.setProperty("class", "label-title")
        layout.addWidget(header)

        # Info card
        info_card = QFrame()
        info_card.setProperty("class", "glass-card")
        info_layout = QVBoxLayout(info_card)

        info_text = QLabel(
            "Вставьте ссылки на Instagram рилсы или username с @\n"
            "Примеры:\n"
            "• https://www.instagram.com/reel/ABC123/\n"
            "• @username (загрузит все видео аккаунта)"
        )
        info_text.setProperty("class", "label-muted")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        layout.addWidget(info_card)

        # Input card
        input_card = QFrame()
        input_card.setProperty("class", "glass-card")
        input_layout = QVBoxLayout(input_card)

        input_title = QLabel("◈ URLs для загрузки")
        input_title.setProperty("class", "label-section")
        input_layout.addWidget(input_title)

        from PyQt6.QtWidgets import QTextEdit
        self.reels_input = QTextEdit()
        self.reels_input.setPlaceholderText("Вставьте ссылки (по одной на строку)")
        self.reels_input.setMinimumHeight(200)
        self.reels_input.setStyleSheet("""
            QTextEdit {
                background-color: #1a1f2e;
                border: 1px solid #2a3142;
                border-radius: 8px;
                padding: 10px;
                color: #e8eaf0;
                font-family: 'Consolas', monospace;
                font-size: 13px;
            }
        """)
        input_layout.addWidget(self.reels_input)

        layout.addWidget(input_card)

        # Instagram credentials card
        creds_card = QFrame()
        creds_card.setProperty("class", "glass-card")
        creds_layout = QVBoxLayout(creds_card)

        creds_title = QLabel("◈ Instagram Credentials (опционально)")
        creds_title.setProperty("class", "label-section")
        creds_layout.addWidget(creds_title)

        creds_info = QLabel("Для загрузки приватных аккаунтов")
        creds_info.setProperty("class", "label-muted")
        creds_layout.addWidget(creds_info)

        # Username
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        username_label.setMinimumWidth(100)
        self.insta_username_input = QLineEdit()
        self.insta_username_input.setPlaceholderText("instagram_username")
        self.insta_username_input.setText(self.config.get('instagram_username', ''))
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.insta_username_input)
        creds_layout.addLayout(username_layout)

        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_label.setMinimumWidth(100)
        self.insta_password_input = QLineEdit()
        self.insta_password_input.setPlaceholderText("password")
        self.insta_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.insta_password_input.setText(self.config.get('instagram_password', ''))
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.insta_password_input)
        creds_layout.addLayout(password_layout)

        # Save credentials button
        save_creds_btn = QPushButton("💾 Сохранить credentials")
        save_creds_btn.clicked.connect(self.save_insta_credentials)
        creds_layout.addWidget(save_creds_btn)

        layout.addWidget(creds_card)

        # Download button
        download_btn = QPushButton("⬇️ НАЧАТЬ ЗАГРУЗКУ")
        download_btn.setProperty("class", "btn-primary")
        download_btn.setMinimumHeight(60)
        download_btn.clicked.connect(self.start_reels_download)
        layout.addWidget(download_btn)

        layout.addStretch()

        scroll.setWidget(downloader_widget)
        self.content_stack.addWidget(scroll)

    def create_input_video_manager_section(self):
        """Create section for managing videos in input folder"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        manager_widget = QWidget()
        layout = QVBoxLayout(manager_widget)
        layout.setSpacing(20)

        # Header
        header = QLabel("◈ МЕНЕДЖЕР ВХОДНЫХ ВИДЕО")
        header.setProperty("class", "label-title")
        layout.addWidget(header)

        # Info card
        info_card = QFrame()
        info_card.setProperty("class", "glass-card")
        info_layout = QVBoxLayout(info_card)

        folder_layout = QHBoxLayout()
        folder_label = QLabel("Папка: unik/input")
        folder_label.setStyleSheet("font-size: 14px; color: #a0a8b8;")
        folder_layout.addWidget(folder_label)
        folder_layout.addStretch()

        # Video count label
        self.input_video_count_label = QLabel("Видео: 0")
        self.input_video_count_label.setStyleSheet("font-size: 14px; color: #00ffff; font-weight: bold;")
        folder_layout.addWidget(self.input_video_count_label)

        open_folder_btn = QPushButton("📁 Открыть папку")
        open_folder_btn.clicked.connect(lambda: self.open_folder_safe("unik/input"))
        folder_layout.addWidget(open_folder_btn)

        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.refresh_input_video_list)
        folder_layout.addWidget(refresh_btn)

        info_layout.addLayout(folder_layout)
        layout.addWidget(info_card)

        # Video grid card
        grid_card = QFrame()
        grid_card.setProperty("class", "glass-card")
        grid_layout = QVBoxLayout(grid_card)

        grid_title = QLabel("◈ Список видео")
        grid_title.setProperty("class", "label-section")
        grid_layout.addWidget(grid_title)

        # Create scroll area for video grid
        videos_scroll = QScrollArea()
        videos_scroll.setWidgetResizable(True)
        videos_scroll.setFrameShape(QFrame.Shape.NoFrame)
        videos_scroll.setMinimumHeight(500)

        # Container for video cards
        self.videos_container = QWidget()
        from PyQt6.QtWidgets import QGridLayout
        from PyQt6.QtCore import Qt
        self.videos_grid_layout = QGridLayout(self.videos_container)
        self.videos_grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.videos_grid_layout.setSpacing(15)
        self.videos_grid_layout.setContentsMargins(10, 10, 10, 10)

        videos_scroll.setWidget(self.videos_container)
        grid_layout.addWidget(videos_scroll)

        # Bulk actions
        actions_layout = QHBoxLayout()
        delete_all_btn = QPushButton("🗑️ Удалить все")
        delete_all_btn.clicked.connect(self.delete_all_input_videos)
        actions_layout.addWidget(delete_all_btn)
        actions_layout.addStretch()
        grid_layout.addLayout(actions_layout)

        layout.addWidget(grid_card)
        layout.addStretch()

        scroll.setWidget(manager_widget)
        self.content_stack.addWidget(scroll)

        # Initial load
        self.refresh_input_video_list()

    def create_instagram_settings_section(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        layout.setSpacing(20)

        # Header
        header = QLabel("◈ НАСТРОЙКИ INSTAGRAM")
        header.setProperty("class", "label-title")
        layout.addWidget(header)

        # Upload settings card
        upload_card = QFrame()
        upload_card.setProperty("class", "glass-card")
        upload_layout = QVBoxLayout(upload_card)

        upload_title = QLabel("◈ Параметры загрузки")
        upload_title.setProperty("class", "label-section")
        upload_layout.addWidget(upload_title)

        # Hashtags toggle
        self.hashtags_checkbox = QCheckBox("Добавлять хэштеги автоматически")
        self.hashtags_checkbox.setChecked(load_config().get("add_hashtags", False))
        self.hashtags_checkbox.setStyleSheet("font-size: 14px;")
        self.hashtags_checkbox.stateChanged.connect(self.save_instagram_settings)
        self.add_checkmark_to_checkbox(self.hashtags_checkbox)
        upload_layout.addWidget(self.hashtags_checkbox)

        # Use descriptions toggle
        self.use_descriptions_checkbox = QCheckBox("Использовать описания из text.xlsx")
        self.use_descriptions_checkbox.setChecked(load_config().get("use_descriptions", True))
        self.use_descriptions_checkbox.setStyleSheet("font-size: 14px;")
        self.use_descriptions_checkbox.stateChanged.connect(self.save_instagram_settings)
        self.add_checkmark_to_checkbox(self.use_descriptions_checkbox)
        upload_layout.addWidget(self.use_descriptions_checkbox)

        # Upload threads slider
        upload_layout.addSpacing(15)
        threads_label = QLabel("Количество потоков загрузки:")
        threads_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        upload_layout.addWidget(threads_label)

        threads_layout = QHBoxLayout()
        self.upload_threads_slider = QSlider(Qt.Orientation.Horizontal)
        self.upload_threads_slider.setMinimum(1)
        self.upload_threads_slider.setMaximum(10)
        self.upload_threads_slider.setValue(load_config().get("upload_threads", 1))
        self.upload_threads_slider.valueChanged.connect(self.save_instagram_settings)
        self.sliders.append(self.upload_threads_slider)
        threads_layout.addWidget(self.upload_threads_slider)

        self.upload_threads_value = QLabel(str(self.upload_threads_slider.value()))
        self.upload_threads_value.setMinimumWidth(30)
        self.upload_threads_value.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ffff;")
        threads_layout.addWidget(self.upload_threads_value)

        self.upload_threads_slider.valueChanged.connect(
            lambda v: self.upload_threads_value.setText(str(v))
        )
        upload_layout.addLayout(threads_layout)

        threads_info = QLabel("Рекомендуется: 1-3 потока. Больше потоков = выше риск блокировки.")
        threads_info.setProperty("class", "label-muted")
        threads_info.setWordWrap(True)
        upload_layout.addWidget(threads_info)

        layout.addWidget(upload_card)

        # Description card
        desc_card = QFrame()
        desc_card.setProperty("class", "glass-card")
        desc_layout = QVBoxLayout(desc_card)

        desc_title = QLabel("◈ Описания")
        desc_title.setProperty("class", "label-section")
        desc_layout.addWidget(desc_title)

        self.desc_count_label = QLabel(f"Загружено описаний: {len(self.descriptions)}")
        desc_layout.addWidget(self.desc_count_label)

        reload_desc_btn = QPushButton("🔄 Перезагрузить описания из text.xlsx")
        reload_desc_btn.setProperty("class", "btn-primary")
        reload_desc_btn.clicked.connect(self.reload_descriptions)
        desc_layout.addWidget(reload_desc_btn)

        open_excel_btn = QPushButton("📋 Открыть text.xlsx")
        open_excel_btn.clicked.connect(lambda: self.open_file_safe("text.xlsx"))
        desc_layout.addWidget(open_excel_btn)

        # Add/Delete descriptions buttons
        desc_buttons_row = QHBoxLayout()

        add_desc_btn = QPushButton("➕ Добавить описание")
        add_desc_btn.setProperty("class", "btn-primary")
        add_desc_btn.clicked.connect(self.add_description)
        desc_buttons_row.addWidget(add_desc_btn)

        delete_desc_btn = QPushButton("🗑️ Удалить описание")
        delete_desc_btn.setProperty("class", "btn-danger")
        delete_desc_btn.clicked.connect(self.delete_description)
        desc_buttons_row.addWidget(delete_desc_btn)

        desc_layout.addLayout(desc_buttons_row)

        layout.addWidget(desc_card)

        # Thumbnails (Обложки) card
        thumb_card = QFrame()
        thumb_card.setProperty("class", "glass-card")
        thumb_layout = QVBoxLayout(thumb_card)

        thumb_title = QLabel("◈ Обложки видео")
        thumb_title.setProperty("class", "label-section")
        thumb_layout.addWidget(thumb_title)

        self.use_thumbnails_checkbox = QCheckBox("Использовать обложки из папки oblo")
        self.use_thumbnails_checkbox.setChecked(self.config.get("use_thumbnails", False))
        self.use_thumbnails_checkbox.stateChanged.connect(self.toggle_thumbnails)
        thumb_layout.addWidget(self.use_thumbnails_checkbox)

        self.thumb_count_label = QLabel("Обложек в папке oblo: 0")
        thumb_layout.addWidget(self.thumb_count_label)

        thumb_buttons_row = QHBoxLayout()

        open_thumb_folder_btn = QPushButton("📁 Открыть папку oblo")
        open_thumb_folder_btn.clicked.connect(lambda: self.open_folder_safe("oblo"))
        thumb_buttons_row.addWidget(open_thumb_folder_btn)

        refresh_thumb_btn = QPushButton("🔄 Обновить")
        refresh_thumb_btn.clicked.connect(self.update_thumbnail_count)
        thumb_buttons_row.addWidget(refresh_thumb_btn)

        thumb_layout.addLayout(thumb_buttons_row)

        thumb_info = QLabel("💡 Обложки должны быть в формате .jpg или .png")
        thumb_info.setStyleSheet("color: #a0a8b8; font-size: 11px; margin-top: 5px;")
        thumb_layout.addWidget(thumb_info)

        layout.addWidget(thumb_card)

        # Profile Management card
        profile_card = QFrame()
        profile_card.setProperty("class", "glass-card")
        profile_layout = QVBoxLayout(profile_card)

        profile_title = QLabel("◈ Управление профилями")
        profile_title.setProperty("class", "label-section")
        profile_layout.addWidget(profile_title)

        # Avatar management buttons
        avatar_all_btn = QPushButton("🖼️ Сменить аватарки для всех аккаунтов")
        avatar_all_btn.setProperty("class", "btn-primary")
        avatar_all_btn.clicked.connect(self.change_avatars_all)
        profile_layout.addWidget(avatar_all_btn)

        avatar_selected_btn = QPushButton("🖼️ Сменить аватарки для выбранных")
        avatar_selected_btn.clicked.connect(self.change_avatars_selected)
        profile_layout.addWidget(avatar_selected_btn)

        # Biography editing button
        bio_btn = QPushButton("✏️ Редактировать биографию")
        bio_btn.clicked.connect(self.edit_biography)
        profile_layout.addWidget(bio_btn)

        # Avatar count info
        avatars_count = len(get_avatar_files())
        avatar_info_label = QLabel(f"Аватарок в папке ava: {avatars_count}")
        avatar_info_label.setStyleSheet("color: #a0a8b8; font-size: 12px; margin-top: 10px;")
        profile_layout.addWidget(avatar_info_label)

        layout.addWidget(profile_card)

        layout.addStretch()

        scroll.setWidget(settings_widget)
        self.content_stack.addWidget(scroll)

    def create_statistics_section(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)
        layout.setSpacing(20)

        # Header
        header = QLabel("◈ СТАТИСТИКА РИЛСОВ")
        header.setProperty("class", "label-title")
        layout.addWidget(header)

        # Account selection card
        selection_card = QFrame()
        selection_card.setProperty("class", "glass-card")
        selection_layout = QVBoxLayout(selection_card)

        selection_title = QLabel("◈ ВЫБОР АККАУНТА")
        selection_title.setProperty("class", "label-section")
        selection_layout.addWidget(selection_title)

        # Account selector
        account_row = QHBoxLayout()
        account_label = QLabel("Аккаунт:")
        account_label.setProperty("class", "label-muted")
        account_row.addWidget(account_label)

        self.stats_account_combo = QComboBox()
        self.stats_account_combo.setMinimumHeight(40)
        self.stats_account_combo.addItem("Все аккаунты", None)
        for acc in self.accounts:
            self.stats_account_combo.addItem(acc['username'], acc['username'])
        account_row.addWidget(self.stats_account_combo, 1)
        selection_layout.addLayout(account_row)

        # Number of clips
        clips_row = QHBoxLayout()
        clips_label = QLabel("Количество рилсов:")
        clips_label.setProperty("class", "label-muted")
        clips_row.addWidget(clips_label)

        self.stats_clips_spin = QSpinBox()
        self.stats_clips_spin.setMinimumHeight(40)
        self.stats_clips_spin.setMinimum(1)
        self.stats_clips_spin.setMaximum(50)
        self.stats_clips_spin.setValue(3)
        clips_row.addWidget(self.stats_clips_spin, 1)
        selection_layout.addLayout(clips_row)

        # Get stats button
        get_stats_btn = QPushButton("📊 Получить статистику")
        get_stats_btn.setProperty("class", "btn-primary")
        get_stats_btn.setMinimumHeight(50)
        get_stats_btn.clicked.connect(self.get_reels_statistics)
        selection_layout.addWidget(get_stats_btn)

        layout.addWidget(selection_card)

        # Statistics display card
        display_card = QFrame()
        display_card.setProperty("class", "glass-card")
        display_layout = QVBoxLayout(display_card)

        display_title = QLabel("◈ РЕЗУЛЬТАТЫ")
        display_title.setProperty("class", "label-section")
        display_layout.addWidget(display_title)

        # Table for statistics
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(6)
        self.stats_table.setHorizontalHeaderLabels([
            "Аккаунт", "Описание", "Дата", "Лайки", "Комментарии", "Просмотры"
        ])

        # Configure column widths
        self.stats_table.setColumnWidth(0, 180)  # Аккаунт - увеличена ширина
        self.stats_table.setColumnWidth(1, 300)  # Описание
        self.stats_table.setColumnWidth(2, 150)  # Дата
        self.stats_table.setColumnWidth(3, 100)  # Лайки
        self.stats_table.setColumnWidth(4, 120)  # Комментарии
        self.stats_table.setColumnWidth(5, 120)  # Просмотры

        # Make last column stretch
        self.stats_table.horizontalHeader().setStretchLastSection(False)
        self.stats_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Описание растягивается

        self.stats_table.setMinimumHeight(400)
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setStyleSheet("""
            QTableWidget {
                background-color: #141824;
                border: 1px solid #2a3142;
                border-radius: 8px;
                gridline-color: #2a3142;
            }
            QTableWidget::item {
                padding: 10px;
                color: #e8eaf0;
            }
            QTableWidget::item:alternate {
                background-color: #1a1f2e;
            }
            QTableWidget::item:selected {
                background-color: #2a3142;
            }
            QHeaderView::section {
                background-color: #1e2433;
                color: #00ffff;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        display_layout.addWidget(self.stats_table)

        layout.addWidget(display_card)
        layout.addStretch()

        scroll.setWidget(stats_widget)
        self.content_stack.addWidget(scroll)

    def create_console_section(self):
        console_widget = QWidget()
        layout = QVBoxLayout(console_widget)

        # Header
        header = QLabel("◈ КОНСОЛЬ")
        header.setProperty("class", "label-title")
        layout.addWidget(header)

        # Console
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setStyleSheet("font-family: 'Consolas', monospace; font-size: 12px;")
        layout.addWidget(self.console_text)

        # Clear button
        clear_btn = QPushButton("🧹 Очистить консоль")
        clear_btn.setMaximumWidth(200)
        clear_btn.clicked.connect(self.console_text.clear)
        layout.addWidget(clear_btn)

        self.content_stack.addWidget(console_widget)

    def create_slider_input(self, parent, label, config_key, min_val, max_val, step=1, in_effects=False):
        """Create slider input"""
        frame = QFrame()
        frame.setProperty("class", "settings-input-frame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()
        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-size: 14px; font-weight: bold; color: #a0a8b8;")
        header_layout.addWidget(label_widget)

        # Get value
        if in_effects:
            value = self.config.get('effects_settings', {}).get(config_key, (min_val + max_val) / 2)
        else:
            value = self.config.get(config_key, (min_val + max_val) / 2)

        value_label = QLabel(f"{value:.2f}" if step < 1 else f"{int(value)}")
        value_label.setMinimumWidth(60)
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        value_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #00ffff;
            background-color: #1a1f2e;
            border: 1px solid #2a3142;
            border-radius: 6px;
            padding: 4px 10px;
        """)
        header_layout.addWidget(value_label)
        layout.addLayout(header_layout)

        # Slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(int(min_val / step))
        slider.setMaximum(int(max_val / step))
        slider.setValue(int(value / step))
        slider.valueChanged.connect(lambda: self.auto_save_uniquifier_settings())
        layout.addWidget(slider)

        # Min/Max labels
        minmax_layout = QHBoxLayout()
        min_label = QLabel(str(min_val))
        min_label.setStyleSheet("font-size: 11px; color: #6b7280;")
        minmax_layout.addWidget(min_label)
        minmax_layout.addStretch()
        max_label = QLabel(str(max_val))
        max_label.setStyleSheet("font-size: 11px; color: #6b7280;")
        minmax_layout.addWidget(max_label)
        layout.addLayout(minmax_layout)

        def update_label(val):
            if step < 1:
                value_label.setText(f"{val * step:.2f}")
            else:
                value_label.setText(f"{int(val * step)}")

            # Обновляем дашборд при изменении копий
            if config_key == "copies_per_video":
                # Обновляем значение в конфиге
                self.config['copies_per_video'] = int(val * step)
                # Обновляем дашборд
                self.update_stats()

        slider.valueChanged.connect(update_label)

        parent.addWidget(frame)
        setattr(self, f"{config_key}_slider", slider)
        setattr(self, f"{config_key}_slider_step", step)
        setattr(self, f"{config_key}_slider_in_effects", in_effects)
        self.sliders.append(slider)

    def create_dropdown_input(self, parent, label, config_key, options, default_value):
        """Create dropdown input"""
        frame = QFrame()
        frame.setProperty("class", "settings-input-frame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 12, 15, 12)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-size: 13px; font-weight: bold; color: #a0a8b8;")
        layout.addWidget(label_widget)

        dropdown = QComboBox()
        dropdown.addItems(options)

        # Set current value
        index = options.index(default_value) if default_value in options else 0
        dropdown.setCurrentIndex(index)

        dropdown.currentIndexChanged.connect(lambda: self.auto_save_uniquifier_settings())
        layout.addWidget(dropdown)

        parent.addWidget(frame)
        setattr(self, f"{config_key}_dropdown", dropdown)

    def create_range_input(self, parent, label, min_key, max_key, min_value, max_value):
        """Create min/max range input"""
        frame = QFrame()
        frame.setProperty("class", "settings-input-frame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 12, 15, 12)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-size: 13px; font-weight: bold; color: #a0a8b8;")
        layout.addWidget(label_widget)

        # Min input
        min_layout = QHBoxLayout()
        min_label = QLabel("Min:")
        min_label.setMinimumWidth(50)
        min_layout.addWidget(min_label)

        min_entry = QLineEdit()
        min_entry.setText(str(min_value))
        min_entry.setMaximumWidth(100)
        min_entry.setPlaceholderText("0.0")
        min_entry.textChanged.connect(lambda: self.auto_save_uniquifier_settings())
        min_layout.addWidget(min_entry)
        min_layout.addStretch()
        layout.addLayout(min_layout)

        # Max input
        max_layout = QHBoxLayout()
        max_label = QLabel("Max:")
        max_label.setMinimumWidth(50)
        max_layout.addWidget(max_label)

        max_entry = QLineEdit()
        max_entry.setText(str(max_value))
        max_entry.setMaximumWidth(100)
        max_entry.setPlaceholderText("1.0")
        max_entry.textChanged.connect(lambda: self.auto_save_uniquifier_settings())
        max_layout.addWidget(max_entry)
        max_layout.addStretch()
        layout.addLayout(max_layout)

        parent.addWidget(frame)
        setattr(self, f"{min_key}_entry", min_entry)
        setattr(self, f"{max_key}_entry", max_entry)

    def show_section(self, index):
        self.content_stack.setCurrentIndex(index)

    def log(self, message):
        """Add message to console"""
        self.console_text.append(f"[{time.strftime('%H:%M:%S')}] {message}")
        self.console_text.verticalScrollBar().setValue(
            self.console_text.verticalScrollBar().maximum()
        )

    def update_stats(self):
        """Update statistics in sidebar and dashboard"""
        # Update sidebar stats
        if hasattr(self, 'stat_labels'):
            self.stat_labels['accounts'].setText(str(len(self.accounts)))

            # Get video count from current folder
            video_count = 0
            try:
                current_folder = load_config().get('current_folder', 'video1')
                if os.path.exists(current_folder):
                    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
                    video_count = len([f for f in os.listdir(current_folder)
                                      if any(f.lower().endswith(ext) for ext in video_extensions)])
            except:
                pass
            self.stat_labels['videos'].setText(str(video_count))

            proxy_status = "ON" if get_proxy_status() else "OFF"
            self.stat_labels['proxy'].setText(proxy_status)

        # Update dashboard stats
        if hasattr(self, 'dashboard_stats'):
            # Accounts count
            accounts_count = len(self.accounts)
            self.dashboard_stats['accounts_dash'].setText(str(accounts_count))

            # Input videos count
            input_count = 0
            if os.path.exists("unik/input"):
                input_count = len([f for f in os.listdir("unik/input")
                                  if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))])
            self.dashboard_stats['input_videos'].setText(str(input_count))

            # Music tracks count
            music_count = 0
            if os.path.exists("unik/music"):
                music_count = len([f for f in os.listdir("unik/music")
                                  if f.endswith(('.mp3', '.wav', '.m4a'))])
            self.dashboard_stats['music_tracks'].setText(str(music_count))

            # Output videos count (will be created)
            copies_per_video = self.config.get('copies_per_video', 5)
            output_count = input_count * copies_per_video
            self.dashboard_stats['output_videos'].setText(str(output_count))

    def refresh_accounts_table(self):
        """Refresh accounts table"""
        self.accounts = load_accounts()
        self.accounts_table.setRowCount(len(self.accounts))

        for i, acc in enumerate(self.accounts):
            # Number column
            number_item = QTableWidgetItem(f"  {i + 1}")
            number_item.setFlags(number_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            number_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            number_item.setForeground(QColor("#00ccff"))
            self.accounts_table.setItem(i, 0, number_item)

            # Username column
            username_item = QTableWidgetItem(f"  @{acc['username']}")
            username_item.setFlags(username_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            username_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.accounts_table.setItem(i, 1, username_item)

            # Get account status
            account_status = get_account_status(acc['username'])
            status = account_status.get('status', 'active')
            error_msg = account_status.get('error', '')

            # Status column
            if status == 'active':
                status_text = "✓ Активен"
                status_color = QColor("#00cc66")
            elif status == 'paused':
                status_text = "⏸ На паузе"
                status_color = QColor("#ff9900")
            else:  # error
                status_text = "❌ Ошибка"
                status_color = QColor("#cc0033")

            status_item = QTableWidgetItem(status_text)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            status_item.setFont(QFont("Segoe UI", 10))
            status_item.setForeground(status_color)
            self.accounts_table.setItem(i, 2, status_item)

            # Error column
            error_item = QTableWidgetItem(error_msg if error_msg else "")
            error_item.setFlags(error_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            error_item.setFont(QFont("Segoe UI", 9))
            error_item.setForeground(QColor("#ff6666"))
            self.accounts_table.setItem(i, 3, error_item)

        self.update_stats()

    def add_account_clicked(self):
        """Add new account"""
        username = self.acc_username_input.text().strip()
        password = self.acc_password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите username и password")
            return

        self.log(f"➕ Добавление аккаунта {username}...")
        self.accounts, success = add_account(self.accounts, username, password)
        self.refresh_accounts_table()
        self.acc_username_input.clear()
        self.acc_password_input.clear()
        if success:
            self.log(f"✅ Аккаунт {username} добавлен")
        else:
            self.log(f"⚠️ Аккаунт {username} не добавлен (ошибка авторизации)")

    def quick_add_account_clicked(self):
        """Quick add account using format: username:password||cookies|||phone"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QCheckBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Быстрое добавление аккаунта")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(400)

        layout = QVBoxLayout(dialog)

        # Инструкция
        instruction_label = QLabel(
            "Поддерживаются два формата:\n\n"
            "1. Простой: логин:пароль\n"
            "   Пример: username:mypassword123\n\n"
            "2. С куками: логин:пароль||cookies|||телефон\n"
            "   Пример: username:password||mid=value;sessionid=value|||380123456789\n\n"
            "Куки в формате: name1=value1;name2=value2;...\n"
            "Телефон после ||| опционально"
        )
        instruction_label.setStyleSheet("color: #00ccff; font-size: 12px; padding: 10px; background-color: #1a1f2e; border-radius: 8px;")
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)

        # Текстовое поле для ввода
        account_input = QTextEdit()
        account_input.setPlaceholderText("Вставьте данные аккаунта (поддерживается: логин:пароль или логин:пароль||cookies|||телефон)")
        account_input.setStyleSheet("font-size: 11px; font-family: 'Consolas', 'Courier New', monospace;")
        layout.addWidget(account_input)

        # Выбор режима
        from PyQt6.QtWidgets import QRadioButton, QButtonGroup

        mode_label = QLabel("📋 Режим добавления:")
        mode_label.setStyleSheet("color: #00ffff; font-size: 13px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(mode_label)

        mode_group = QButtonGroup()

        mode_login = QRadioButton("🔑 Логин:Пароль (игнорировать cookies)")
        mode_login.setStyleSheet("color: #e8eaf0; font-size: 12px;")
        mode_group.addButton(mode_login, 1)
        layout.addWidget(mode_login)

        mode_cookies = QRadioButton("🍪 Cookies (использовать готовую сессию)")
        mode_cookies.setStyleSheet("color: #e8eaf0; font-size: 12px;")
        mode_cookies.setChecked(True)
        mode_group.addButton(mode_cookies, 2)
        layout.addWidget(mode_cookies)

        # Чекбокс для валидации
        validate_checkbox = QCheckBox("✓ Проверить валидность после добавления")
        validate_checkbox.setChecked(True)
        validate_checkbox.setStyleSheet("margin-top: 10px;")
        layout.addWidget(validate_checkbox)

        # Кнопки
        buttons_layout = QHBoxLayout()

        add_button = QPushButton("✅ Добавить аккаунт")
        add_button.setProperty("class", "btn-primary")
        add_button.setStyleSheet("background-color: #00994d; border: 2px solid #007a3d; padding: 10px; font-weight: bold;")

        cancel_button = QPushButton("❌ Отмена")
        cancel_button.setProperty("class", "btn-danger")

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        def add_account_from_input():
            account_data_str = account_input.toPlainText().strip()

            if not account_data_str:
                QMessageBox.warning(dialog, "Ошибка", "Введите данные аккаунта")
                return

            # Определяем выбранный режим
            use_cookies = mode_cookies.isChecked()

            try:
                # Парсим данные (поддерживаем оба формата)
                if '||' in account_data_str:
                    parts = account_data_str.split('||', 1)

                    # Парсим username:password
                    username_password = parts[0].split(':', 1)
                    if len(username_password) != 2:
                        QMessageBox.warning(dialog, "Ошибка", "Неверный формат логин:пароль")
                        return

                    username = username_password[0].strip()
                    password = username_password[1].strip()

                    # Парсим вторую часть (cookies|||phone)
                    second_part = parts[1] if len(parts) > 1 else ""

                    phone = None
                    cookies_str = second_part

                    if '|||' in second_part:
                        cookies_and_phone = second_part.split('|||', 1)
                        cookies_str = cookies_and_phone[0].strip()
                        phone = cookies_and_phone[1].strip() if len(cookies_and_phone) > 1 and cookies_and_phone[1].strip() else None

                    # Парсим куки в словарь
                    cookies = {}
                    if cookies_str:
                        cookie_pairs = cookies_str.split(';')
                        for pair in cookie_pairs:
                            pair = pair.strip()
                            if '=' in pair:
                                key, value = pair.split('=', 1)
                                cookies[key.strip()] = value.strip()

                    dialog.accept()

                    # Выбираем режим добавления
                    if use_cookies and cookies:
                        # Режим с cookies
                        self.log(f"⚡ Быстрое добавление аккаунта {username} (режим: 🍪 Cookies)")
                        if phone:
                            self.log(f"Телефон: {phone}")
                        self.log(f"Найдено {len(cookies)} куки")

                        from core import add_account_with_cookies, validate_account_cookies

                        def add_worker():
                            try:
                                accounts = load_accounts()
                                updated_accounts = add_account_with_cookies(
                                    accounts, username, password, cookies, phone, callback=self.log
                                )

                                # Валидация если включена
                                if validate_checkbox.isChecked():
                                    self.log(f"🔍 Проверка валидности {username}...")
                                    is_valid = validate_account_cookies(username, cookies, callback=self.log)

                                    if is_valid:
                                        self.log(f"✅ Аккаунт {username} валиден")
                                    else:
                                        self.log(f"⚠️ Аккаунт {username} может быть невалидным")

                                QTimer.singleShot(0, self.refresh_accounts_table)
                                self.log(f"✅ Аккаунт {username} успешно добавлен")

                            except Exception as e:
                                self.log(f"❌ Ошибка при добавлении {username}: {str(e)}")
                                QTimer.singleShot(0, self.refresh_accounts_table)

                        import_thread = threading.Thread(target=add_worker, daemon=True)
                        import_thread.start()

                    else:
                        # Режим логин:пароль (игнорируем cookies)
                        self.log(f"⚡ Быстрое добавление аккаунта {username} (режим: 🔑 Логин:Пароль)")

                        def add_worker_login():
                            try:
                                accounts = load_accounts()
                                updated_accounts, success = add_account(accounts, username, password)

                                QTimer.singleShot(0, self.refresh_accounts_table)
                                if success:
                                    self.log(f"✅ Аккаунт {username} успешно добавлен")
                                else:
                                    self.log(f"⚠️ Аккаунт {username} не добавлен (ошибка авторизации)")

                            except Exception as e:
                                self.log(f"❌ Ошибка при добавлении {username}: {str(e)}")
                                QTimer.singleShot(0, self.refresh_accounts_table)

                        import_thread = threading.Thread(target=add_worker_login, daemon=True)
                        import_thread.start()

                # Простой формат username:password
                elif ':' in account_data_str:
                    username_password = account_data_str.split(':', 1)
                    if len(username_password) != 2:
                        QMessageBox.warning(dialog, "Ошибка", "Неверный формат логин:пароль")
                        return

                    username = username_password[0].strip()
                    password = username_password[1].strip()

                    dialog.accept()

                    # Логируем добавление
                    self.log(f"⚡ Быстрое добавление аккаунта {username} (логин:пароль)...")

                    def add_worker_simple():
                        try:
                            # Добавляем аккаунт простым способом
                            accounts = load_accounts()
                            updated_accounts, success = add_account(accounts, username, password)

                            # Обновляем таблицу
                            QTimer.singleShot(0, self.refresh_accounts_table)
                            if success:
                                self.log(f"✅ Аккаунт {username} успешно добавлен")
                            else:
                                self.log(f"⚠️ Аккаунт {username} не добавлен (ошибка авторизации)")

                        except Exception as e:
                            self.log(f"❌ Ошибка при добавлении {username}: {str(e)}")
                            QTimer.singleShot(0, self.refresh_accounts_table)

                    # Запускаем в отдельном потоке
                    import_thread = threading.Thread(target=add_worker_simple, daemon=True)
                    import_thread.start()

                else:
                    QMessageBox.warning(dialog, "Ошибка", "Неверный формат. Используйте:\n1. логин:пароль\n2. логин:пароль||cookies|||телефон")
                    return

            except Exception as e:
                QMessageBox.critical(dialog, "Ошибка", f"Ошибка при парсинге данных: {str(e)}")

        add_button.clicked.connect(add_account_from_input)
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec()

    def delete_selected_account(self):
        """Delete selected account"""
        current_row = self.accounts_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите аккаунт для удаления")
            return

        username = self.accounts[current_row]['username']
        reply = QMessageBox.question(
            self, 'Подтверждение',
            f"Удалить аккаунт {username}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.log(f"🗑️ Удаление аккаунта {username}...")
            self.accounts = delete_account(self.accounts, username)
            self.refresh_accounts_table()
            self.log(f"✅ Аккаунт {username} удален")

    def clear_all_sessions_clicked(self):
        """Clear all sessions"""
        reply = QMessageBox.question(
            self, 'Подтверждение',
            "Очистить все сессии? Потребуется повторная авторизация.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.log("🧹 Очистка всех сессий...")
            if clear_all_sessions():
                self.log("✅ Все сессии очищены")
                self.refresh_accounts_table()
            else:
                self.log("❌ Ошибка при очистке сессий")

    def import_accounts_clicked(self):
        """Import accounts from file"""
        dialog = ImportAccountsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            import_data = dialog.get_import_data()

            self.log("📥 Начало импорта аккаунтов...")
            self.log(f"Файл: {import_data['file_path']}")
            self.log(f"Выбрано аккаунтов: {len(import_data['selected_indices'])}")
            self.log(f"Режим: {'🍪 Cookies' if import_data['use_cookies'] else '🔑 Логин:Пароль'}")
            self.log(f"Валидация: {'Да' if import_data['validate'] else 'Нет'}")

            # Запускаем импорт в отдельном потоке
            def import_worker():
                try:
                    added_count = import_accounts_from_file(
                        import_data['file_path'],
                        import_data['selected_indices'],
                        import_data['validate'],
                        import_data['use_cookies'],
                        callback=self.log
                    )

                    if added_count > 0:
                        # Обновляем таблицу в главном потоке
                        QTimer.singleShot(0, self.refresh_accounts_table)
                        self.log(f"✅ Импорт завершен успешно! Добавлено: {added_count}")
                    else:
                        self.log("⚠️ Не удалось добавить ни одного аккаунта")

                except Exception as e:
                    self.log(f"❌ Ошибка при импорте: {str(e)}")

            # Запускаем в отдельном потоке, чтобы не блокировать UI
            import_thread = threading.Thread(target=import_worker, daemon=True)
            import_thread.start()

    def validate_accounts_clicked(self):
        """Validate all accounts"""
        if not self.accounts:
            QMessageBox.information(self, "Информация", "Нет аккаунтов для проверки")
            return

        reply = QMessageBox.question(
            self, 'Подтверждение',
            f"Проверить валидность всех {len(self.accounts)} аккаунтов?\nЭто может занять некоторое время.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.log(f"🔍 Начало проверки валидности {len(self.accounts)} аккаунтов...")

        def validate_worker():
            try:
                valid_count = 0
                invalid_count = 0

                for i, account in enumerate(self.accounts, 1):
                    username = account['username']
                    self.log(f"[{i}/{len(self.accounts)}] Проверка {username}...")

                    # Для проверки валидности нам нужны куки из сессии
                    # Попробуем загрузить сессию и проверить её
                    from config import SESSION_FILE
                    import json
                    import os

                    session_file = SESSION_FILE.format(username)

                    if not os.path.exists(session_file):
                        self.log(f"⚠️ {username}: нет файла сессии")
                        invalid_count += 1
                        continue

                    try:
                        with open(session_file, 'r') as f:
                            session_data = json.load(f)

                        cookies = session_data.get('cookies', {})

                        if not cookies:
                            self.log(f"⚠️ {username}: нет куки в сессии")
                            invalid_count += 1
                            continue

                        # Проверяем валидность
                        is_valid = validate_account_cookies(username, cookies, callback=self.log)

                        if is_valid:
                            valid_count += 1
                        else:
                            invalid_count += 1

                        # Небольшая задержка между проверками
                        time.sleep(2)

                    except Exception as e:
                        self.log(f"❌ {username}: ошибка проверки - {str(e)}")
                        invalid_count += 1

                self.log(f"\n{'='*60}")
                self.log(f"✅ Проверка завершена!")
                self.log(f"Валидных аккаунтов: {valid_count}")
                self.log(f"Невалидных аккаунтов: {invalid_count}")
                self.log(f"{'='*60}\n")

            except Exception as e:
                self.log(f"❌ Критическая ошибка при проверке: {str(e)}")

        # Запускаем в отдельном потоке
        validate_thread = threading.Thread(target=validate_worker, daemon=True)
        validate_thread.start()

    def toggle_proxy_clicked(self):
        """Toggle proxy on/off"""
        enabled = toggle_proxy()
        status = "ВКЛЮЧЕН" if enabled else "ВЫКЛЮЧЕН"
        color = "#00cc66" if enabled else "#ff0055"

        self.proxy_status_label.setText(f"Прокси {status}")
        self.proxy_status_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        self.log(f"🌐 Прокси: {status}")
        self.update_stats()

    def change_ip_now(self):
        """Change IP immediately"""
        from insta_client import InstagramClient
        client = InstagramClient()
        self.log("🔄 Смена IP...")
        if client.change_ip():
            self.log("✅ IP успешно изменён")
        else:
            self.log("❌ Ошибка при смене IP")

    def save_proxy_settings(self):
        """Save proxy settings"""
        host = self.proxy_host_input.text().strip()
        port = self.proxy_port_input.text().strip()
        user = self.proxy_user_input.text().strip()
        password = self.proxy_pass_input.text().strip()
        change_ip_url = self.proxy_url_input.text().strip()

        # Validate input
        if not host or not port:
            QMessageBox.warning(self, "Ошибка", "Host и Port обязательны для заполнения!")
            return

        # Update settings
        if update_proxy_settings(host, port, user, password, change_ip_url):
            self.log("✅ Настройки прокси сохранены")
            QMessageBox.information(self, "Готово", "Настройки прокси успешно сохранены!")
        else:
            self.log("❌ Ошибка сохранения настроек прокси")
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить настройки прокси")

    def reload_descriptions(self):
        """Reload descriptions from Excel"""
        self.descriptions = load_descriptions()
        self.desc_count_label.setText(f"Загружено описаний: {len(self.descriptions)}")
        self.log(f"✅ Перезагружено описаний: {len(self.descriptions)}")
        QMessageBox.information(self, "Готово", f"Загружено {len(self.descriptions)} описаний")

    def add_description(self):
        """Add new description"""
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getMultiLineText(
            self,
            "Добавить описание",
            "Введите новое описание:",
            ""
        )
        if ok and text.strip():
            # Add to descriptions list
            self.descriptions.append(text.strip())

            # Save to Excel file
            try:
                import openpyxl
                from pathlib import Path

                excel_path = Path("text.xlsx")
                if excel_path.exists():
                    wb = openpyxl.load_workbook(excel_path)
                    ws = wb.active
                else:
                    wb = openpyxl.Workbook()
                    ws = wb.active
                    ws['A1'] = 'Описания'

                # Find next empty row
                row = ws.max_row + 1
                ws[f'A{row}'] = text.strip()
                wb.save(excel_path)

                self.desc_count_label.setText(f"Загружено описаний: {len(self.descriptions)}")
                self.log(f"✅ Добавлено новое описание")
                QMessageBox.information(self, "Готово", "Описание успешно добавлено")
            except Exception as e:
                self.log(f"❌ Ошибка при сохранении описания: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить описание: {e}")

    def delete_description(self):
        """Delete description"""
        if not self.descriptions:
            QMessageBox.warning(self, "Ошибка", "Нет описаний для удаления")
            return

        from PyQt6.QtWidgets import QInputDialog

        # Show list of descriptions
        items = [f"{i+1}. {desc[:50]}..." if len(desc) > 50 else f"{i+1}. {desc}"
                 for i, desc in enumerate(self.descriptions)]

        item, ok = QInputDialog.getItem(
            self,
            "Удалить описание",
            "Выберите описание для удаления:",
            items,
            0,
            False
        )

        if ok and item:
            # Get index
            index = int(item.split('.')[0]) - 1

            # Remove from list
            self.descriptions.pop(index)

            # Save to Excel
            try:
                import openpyxl
                from pathlib import Path

                excel_path = Path("text.xlsx")
                wb = openpyxl.Workbook()
                ws = wb.active
                ws['A1'] = 'Описания'

                for i, desc in enumerate(self.descriptions, start=2):
                    ws[f'A{i}'] = desc

                wb.save(excel_path)

                self.desc_count_label.setText(f"Загружено описаний: {len(self.descriptions)}")
                self.log(f"✅ Описание удалено")
                QMessageBox.information(self, "Готово", "Описание успешно удалено")
            except Exception as e:
                self.log(f"❌ Ошибка при сохранении: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения: {e}")

    def toggle_thumbnails(self, state):
        """Toggle thumbnail usage"""
        use_thumbnails = bool(state)
        self.config["use_thumbnails"] = use_thumbnails
        save_config(self.config)
        status = "ВКЛЮЧЕНЫ" if use_thumbnails else "ВЫКЛЮЧЕНЫ"
        self.log(f"🖼️ Обложки: {status}")

    def update_thumbnail_count(self):
        """Update thumbnail count"""
        try:
            import os
            oblo_path = "oblo"
            if not os.path.exists(oblo_path):
                os.makedirs(oblo_path)
                self.log(f"📁 Создана папка {oblo_path}")

            thumbnails = [f for f in os.listdir(oblo_path)
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            count = len(thumbnails)
            self.thumb_count_label.setText(f"Обложек в папке oblo: {count}")
            self.log(f"🖼️ Найдено обложек: {count}")
        except Exception as e:
            self.log(f"❌ Ошибка при подсчете обложек: {e}")

    def change_avatars_all(self):
        """Change avatars for all accounts"""
        if not self.accounts:
            QMessageBox.warning(self, "Ошибка", "Нет доступных аккаунтов")
            return

        avatars = get_avatar_files()
        if not avatars:
            QMessageBox.warning(self, "Ошибка", "Нет аватарок в папке ava. Поместите изображения (.jpg, .png) в папку ava")
            return

        reply = QMessageBox.question(
            self, 'Подтверждение',
            f"Найдено аватарок: {len(avatars)}\nБудет обновлено аккаунтов: {len(self.accounts)}\n\nНачать смену аватарок для всех аккаунтов?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.log("🖼️ Начинаем смену аватарок для всех аккаунтов...")
            change_avatars_for_accounts(self.accounts, selected_usernames=None)
            self.log("✅ Смена аватарок завершена")

    def change_avatars_selected(self):
        """Change avatars for selected accounts"""
        if not self.accounts:
            QMessageBox.warning(self, "Ошибка", "Нет доступных аккаунтов")
            return

        avatars = get_avatar_files()
        if not avatars:
            QMessageBox.warning(self, "Ошибка", "Нет аватарок в папке ava. Поместите изображения (.jpg, .png) в папку ava")
            return

        # Create dialog for selecting accounts
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QPushButton, QScrollArea

        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор аккаунтов")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)

        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        checkboxes = []
        for acc in self.accounts:
            cb = QCheckBox(acc['username'])
            checkboxes.append(cb)
            scroll_layout.addWidget(cb)

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # OK button
        ok_btn = QPushButton("✅ Подтвердить")
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_usernames = [cb.text() for cb in checkboxes if cb.isChecked()]

            if not selected_usernames:
                QMessageBox.warning(self, "Ошибка", "Не выбраны аккаунты")
                return

            reply = QMessageBox.question(
                self, 'Подтверждение',
                f"Найдено аватарок: {len(avatars)}\nБудет обновлено аккаунтов: {len(selected_usernames)}\n\nАккаунты: {', '.join(selected_usernames)}\n\nНачать смену аватарок?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.log(f"🖼️ Начинаем смену аватарок для {len(selected_usernames)} аккаунтов...")
                change_avatars_for_accounts(self.accounts, selected_usernames=selected_usernames)
                self.log("✅ Смена аватарок завершена")

    def edit_biography(self):
        """Edit biography for accounts"""
        if not self.accounts:
            QMessageBox.warning(self, "Ошибка", "Нет доступных аккаунтов")
            return

        # Create dialog
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QRadioButton, QCheckBox, QPushButton, QScrollArea, QButtonGroup

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование биографии")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        layout = QVBoxLayout(dialog)

        # Biography input
        bio_label = QLabel("Введите новую биографию:")
        layout.addWidget(bio_label)

        bio_input = QTextEdit()
        bio_input.setMaximumHeight(100)
        layout.addWidget(bio_input)

        # Account selection
        selection_label = QLabel("Выбор аккаунтов:")
        layout.addWidget(selection_label)

        radio_group = QButtonGroup(dialog)
        all_radio = QRadioButton("Все аккаунты")
        all_radio.setChecked(True)
        radio_group.addButton(all_radio)
        layout.addWidget(all_radio)

        selected_radio = QRadioButton("Выбранные аккаунты")
        radio_group.addButton(selected_radio)
        layout.addWidget(selected_radio)

        # Checkboxes for accounts
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        checkboxes = []
        for acc in self.accounts:
            cb = QCheckBox(acc['username'])
            cb.setEnabled(False)
            checkboxes.append(cb)
            scroll_layout.addWidget(cb)

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        layout.addWidget(scroll)

        # Enable checkboxes when "Selected" is chosen
        def on_radio_changed():
            enabled = selected_radio.isChecked()
            for cb in checkboxes:
                cb.setEnabled(enabled)

        all_radio.toggled.connect(on_radio_changed)

        # OK button
        ok_btn = QPushButton("✅ Обновить биографию")
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            biography = bio_input.toPlainText().strip()

            if not biography:
                QMessageBox.warning(self, "Ошибка", "Биография не может быть пустой")
                return

            selected_usernames = None
            if selected_radio.isChecked():
                selected_usernames = [cb.text() for cb in checkboxes if cb.isChecked()]
                if not selected_usernames:
                    QMessageBox.warning(self, "Ошибка", "Не выбраны аккаунты")
                    return

            accounts_count = len(selected_usernames) if selected_usernames else len(self.accounts)

            reply = QMessageBox.question(
                self, 'Подтверждение',
                f"Будет обновлено аккаунтов: {accounts_count}\nБиография: {biography}\n\nНачать обновление биографии?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.log(f"✏️ Начинаем редактирование биографии для {accounts_count} аккаунтов...")
                edit_biographies_for_accounts(self.accounts, selected_usernames, biography)
                self.log("✅ Редактирование биографии завершено")

    def save_insta_credentials(self):
        """Save Instagram credentials to config"""
        self.config['instagram_username'] = self.insta_username_input.text()
        self.config['instagram_password'] = self.insta_password_input.text()
        self.save_config_to_file()
        self.log("✅ Instagram credentials сохранены")
        QMessageBox.information(self, "Сохранено", "Instagram credentials успешно сохранены")

    def start_reels_download(self):
        """Start downloading Instagram reels"""
        urls = self.reels_input.toPlainText().strip()
        if not urls:
            QMessageBox.warning(self, "Ошибка", "Введите хотя бы одну ссылку")
            return

        # Save credentials if changed
        self.config['instagram_username'] = self.insta_username_input.text()
        self.config['instagram_password'] = self.insta_password_input.text()
        self.save_config_to_file()

        self.log("⬇️ Начинаю загрузку рилсов...")
        self.status_label.setText("● ЗАГРУЗКА")
        self.status_label.setProperty("class", "status-working")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffaa00;")

        # Create download thread
        from PyQt6.QtCore import QThread, pyqtSignal

        class DownloadThread(QThread):
            finished = pyqtSignal(int, str)
            log_signal = pyqtSignal(str)

            def __init__(self, urls, config):
                super().__init__()
                self.urls = urls
                self.config = config

            def run(self):
                import instaloader
                import re
                import subprocess

                inputs = self.urls.splitlines()
                input_folder = self.config.get('input_folder', 'unik/input')
                os.makedirs(input_folder, exist_ok=True)

                downloaded_count = 0
                loader = instaloader.Instaloader()
                loader.dirname_pattern = input_folder
                loader.filename_pattern = '{shortcode}'
                loader.download_pictures = False
                loader.download_geotags = False
                loader.download_comments = False
                loader.download_video_thumbnails = False
                loader.save_metadata = False
                loader.post_metadata_txt_pattern = ''

                username = self.config.get('instagram_username', '')
                password = self.config.get('instagram_password', '')

                if username and password:
                    try:
                        loader.login(username, password)
                        self.log_signal.emit("✓ Успешный вход в Instagram")
                    except Exception as e:
                        self.log_signal.emit(f"✗ Ошибка входа: {str(e)}")
                        self.finished.emit(0, f"Ошибка входа: {str(e)}")
                        return

                for line in inputs:
                    if not line.strip():
                        continue

                    try:
                        if line.startswith('@'):
                            username = line[1:].strip()
                            self.log_signal.emit(f"⬇️ Загрузка видео из аккаунта: {username}")
                            profile = instaloader.Profile.from_username(loader.context, username)
                            for post in profile.get_posts():
                                if post.is_video:
                                    loader.download_post(post, target='')
                                    downloaded_count += 1
                                    self.log_signal.emit(f"✓ Загружено видео из {username}")
                        else:
                            url = line.strip()
                            self.log_signal.emit(f"⬇️ Загрузка: {url}")
                            match = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)/', url)
                            if match:
                                shortcode = match.group(1)
                                try:
                                    post = instaloader.Post.from_shortcode(loader.context, shortcode)
                                    if post.is_video:
                                        loader.download_post(post, target='')
                                        downloaded_count += 1
                                        self.log_signal.emit(f"✓ Загружено: {url}")
                                except Exception as instaloader_e:
                                    self.log_signal.emit(f"✗ Ошибка instaloader: {str(instaloader_e)}")
                                    # Fallback to yt-dlp
                                    cleaned_url = f"https://www.instagram.com/reel/{shortcode}/"
                                    try:
                                        cmd = [
                                            "yt-dlp",
                                            "-f", "best[ext=mp4]",
                                            "--no-playlist",
                                            "-o", os.path.join(input_folder, "%(id)s.%(ext)s"),
                                            cleaned_url
                                        ]
                                        subprocess.run(cmd, check=True, capture_output=True)
                                        downloaded_count += 1
                                        self.log_signal.emit(f"✓ Загружено (yt-dlp): {cleaned_url}")
                                    except Exception as ytdlp_e:
                                        self.log_signal.emit(f"✗ Ошибка yt-dlp: {str(ytdlp_e)}")
                            else:
                                self.log_signal.emit(f"✗ Недействительный URL: {url}")
                    except Exception as e:
                        self.log_signal.emit(f"✗ Ошибка загрузки {line}: {str(e)}")

                # Clean up non-video files
                video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
                for filename in os.listdir(input_folder):
                    filepath = os.path.join(input_folder, filename)
                    if os.path.isfile(filepath):
                        _, ext = os.path.splitext(filename)
                        if ext.lower() not in video_extensions:
                            os.remove(filepath)
                            self.log_signal.emit(f"🗑️ Удален ненужный файл: {filename}")

                self.finished.emit(downloaded_count, "success")

        self.download_thread = DownloadThread(urls, self.config)
        self.download_thread.log_signal.connect(self.log)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()

    def on_download_finished(self, count, status):
        """Handle download completion"""
        self.status_label.setText("● ГОТОВА")
        self.status_label.setProperty("class", "status-ready")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00cc66;")

        if status == "success":
            self.log(f"✅ Загрузка завершена! Скачано видео: {count}")
            QMessageBox.information(self, "Готово", f"Загружено {count} видео в папку unik/input")
            self.refresh_input_video_list()
            self.update_stats()
        else:
            self.log(f"❌ Ошибка загрузки: {status}")
            QMessageBox.warning(self, "Ошибка", status)

    def refresh_input_video_list(self):
        """Refresh the grid of videos in input folder with thumbnails"""
        input_folder = self.config.get('input_folder', 'unik/input')
        os.makedirs(input_folder, exist_ok=True)

        video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
        videos = []

        try:
            # Collect video files
            for filename in os.listdir(input_folder):
                filepath = os.path.join(input_folder, filename)
                if os.path.isfile(filepath):
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in video_extensions:
                        size = os.path.getsize(filepath)
                        size_mb = size / (1024 * 1024)
                        videos.append({
                            'name': filename,
                            'path': filepath,
                            'size': size_mb
                        })

            # Sort by name
            videos.sort(key=lambda x: x['name'])

            # Update count label
            if hasattr(self, 'input_video_count_label'):
                self.input_video_count_label.setText(f"Видео: {len(videos)}")

            # Clear existing grid
            while self.videos_grid_layout.count():
                item = self.videos_grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Create video cards in grid (4 columns for larger cards)
            columns = 4
            for i, video in enumerate(videos):
                row = i // columns
                col = i % columns

                # Create video card
                video_card = self.create_video_card(video)
                self.videos_grid_layout.addWidget(video_card, row, col)

        except Exception as e:
            self.log(f"❌ Ошибка обновления списка видео: {e}")

        self.update_stats()

    def create_video_card(self, video):
        """Create an optimized card widget with gray background"""
        card = QFrame()
        card.setFixedSize(220, 220)
        card.setStyleSheet("""
            QFrame {
                background-color: #1e2433;
                border: 1px solid #2a3142;
                border-radius: 10px;
                padding: 0px;
                margin: 0px;
            }
            QFrame:hover {
                border: 2px solid #00ffff;
                background-color: #252b3d;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Thumbnail
        thumbnail_container = QLabel()
        thumbnail_container.setFixedSize(220, 160)
        thumbnail_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Try to generate thumbnail or show video icon
        thumbnail_pixmap = self.get_video_thumbnail(video['path'])
        if thumbnail_pixmap:
            scaled_pixmap = thumbnail_pixmap.scaled(
                220, 160,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            thumbnail_container.setPixmap(scaled_pixmap)
            thumbnail_container.setStyleSheet("""
                QLabel {
                    background-color: #0a0e1a;
                    border: none;
                    border-radius: 10px 10px 0px 0px;
                }
            """)
        else:
            # Show video icon if thumbnail generation failed
            thumbnail_container.setText("🎬")
            thumbnail_container.setStyleSheet("""
                QLabel {
                    background-color: #151a27;
                    border: none;
                    border-radius: 10px 10px 0px 0px;
                    font-size: 48px;
                    color: #00ffff;
                }
            """)

        layout.addWidget(thumbnail_container)

        # Buttons row
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        buttons_layout.setContentsMargins(12, 12, 12, 12)

        # View button
        view_btn = QPushButton("Посмотреть")
        view_btn.setFixedHeight(32)
        view_btn.setToolTip(f"Открыть: {video['name']}")
        view_btn.clicked.connect(lambda: self.open_video_file(video['path']))
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a3142;
                border: 1px solid #00ffff;
                border-radius: 6px;
                color: #00ffff;
                font-size: 11px;
                font-weight: bold;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background-color: #00ffff;
                color: #0a0e1a;
            }
        """)
        buttons_layout.addWidget(view_btn)

        # Delete button
        delete_btn = QPushButton("Удалить")
        delete_btn.setFixedHeight(32)
        delete_btn.setToolTip("Удалить видео")
        delete_btn.clicked.connect(lambda: self.delete_input_video(video['path']))
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a3142;
                border: 1px solid #ff0055;
                border-radius: 6px;
                color: #ff0055;
                font-size: 11px;
                font-weight: bold;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background-color: #ff0055;
                color: #ffffff;
            }
        """)
        buttons_layout.addWidget(delete_btn)

        layout.addLayout(buttons_layout)

        return card

    def get_video_thumbnail(self, video_path):
        """Generate or get thumbnail for video"""
        try:
            from PyQt6.QtGui import QPixmap
            import subprocess

            # Try to extract frame using ffmpeg
            temp_thumb = os.path.join(os.path.dirname(video_path), f".thumb_{os.path.basename(video_path)}.jpg")

            # Extract frame at 1 second preserving aspect ratio
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', '00:00:01',
                '-vframes', '1',
                '-vf', 'scale=220:160:force_original_aspect_ratio=decrease',
                '-y',
                temp_thumb
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=5)

            if result.returncode == 0 and os.path.exists(temp_thumb):
                pixmap = QPixmap(temp_thumb)
                # Clean up temp file
                try:
                    os.remove(temp_thumb)
                except:
                    pass
                return pixmap

        except:
            pass

        return None

    def open_video_file(self, filepath):
        """Open video file with default application"""
        try:
            if os.path.exists(filepath):
                os.startfile(filepath)
            else:
                QMessageBox.warning(self, "Ошибка", "Файл не найден")
        except Exception as e:
            self.log(f"❌ Ошибка открытия файла: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {e}")

    def delete_input_video(self, filepath):
        """Delete a single video from input folder"""
        reply = QMessageBox.question(
            self, 'Подтверждение',
            f"Удалить видео {os.path.basename(filepath)}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(filepath)
                self.log(f"✅ Удалено: {os.path.basename(filepath)}")
                self.refresh_input_video_list()
            except Exception as e:
                self.log(f"❌ Ошибка удаления: {e}")
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить файл: {e}")

    def delete_all_input_videos(self):
        """Delete all videos from input folder"""
        input_folder = self.config.get('input_folder', 'unik/input')

        reply = QMessageBox.question(
            self, 'Подтверждение',
            "Удалить ВСЕ видео из папки unik/input?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
                deleted_count = 0

                for filename in os.listdir(input_folder):
                    filepath = os.path.join(input_folder, filename)
                    if os.path.isfile(filepath):
                        _, ext = os.path.splitext(filename)
                        if ext.lower() in video_extensions:
                            os.remove(filepath)
                            deleted_count += 1

                self.log(f"✅ Удалено видео: {deleted_count}")
                self.refresh_input_video_list()
                QMessageBox.information(self, "Готово", f"Удалено {deleted_count} видео")
            except Exception as e:
                self.log(f"❌ Ошибка удаления: {e}")
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить файлы: {e}")

    def auto_save_uniquifier_settings(self):
        """Auto-save uniquifier settings"""
        try:
            # Add music
            if hasattr(self, 'add_music_checkbox'):
                self.config['add_music'] = self.add_music_checkbox.isChecked()

            # Copies
            if hasattr(self, 'copies_per_video_slider'):
                step = getattr(self, 'copies_per_video_slider_step', 1)
                self.config['copies_per_video'] = int(self.copies_per_video_slider.value() * step)

            # Angle-zoom mapping
            if hasattr(self, 'angle_entries'):
                if 'angle_zoom_map' not in self.config:
                    self.config['angle_zoom_map'] = {}
                for angle, entry in self.angle_entries.items():
                    try:
                        self.config['angle_zoom_map'][angle] = float(entry.text())
                    except:
                        pass

            # Video settings
            if 'video_settings' not in self.config:
                self.config['video_settings'] = {}

            if hasattr(self, 'output_resolution_dropdown'):
                self.config['video_settings']['output_resolution'] = self.output_resolution_dropdown.currentText()
            if hasattr(self, 'video_codec_dropdown'):
                self.config['video_settings']['video_codec'] = self.video_codec_dropdown.currentText()
            if hasattr(self, 'video_preset_dropdown'):
                self.config['video_settings']['video_preset'] = self.video_preset_dropdown.currentText()
            if hasattr(self, 'video_crf_slider'):
                step = getattr(self, 'video_crf_slider_step', 1)
                self.config['video_settings']['video_crf'] = int(self.video_crf_slider.value() * step)
            if hasattr(self, 'audio_codec_dropdown'):
                self.config['video_settings']['audio_codec'] = self.audio_codec_dropdown.currentText()
            if hasattr(self, 'audio_bitrate_dropdown'):
                self.config['video_settings']['audio_bitrate'] = self.audio_bitrate_dropdown.currentText()
            if hasattr(self, 'pixel_format_dropdown'):
                self.config['video_settings']['pixel_format'] = self.pixel_format_dropdown.currentText()

            # Effects probabilities
            if 'effects_settings' not in self.config:
                self.config['effects_settings'] = {}

            for key in ['mirror_probability', 'color_balance_probability',
                       'brightness_contrast_probability', 'saturation_probability',
                       'color_balance_range', 'brightness_range']:
                if hasattr(self, f'{key}_slider'):
                    slider = getattr(self, f'{key}_slider')
                    step = getattr(self, f'{key}_slider_step', 0.1)
                    self.config['effects_settings'][key] = slider.value() * step

            # Range entries for contrast and saturation
            if hasattr(self, 'contrast_min_entry'):
                try:
                    self.config['effects_settings']['contrast_min'] = float(self.contrast_min_entry.text())
                except:
                    pass
            if hasattr(self, 'contrast_max_entry'):
                try:
                    self.config['effects_settings']['contrast_max'] = float(self.contrast_max_entry.text())
                except:
                    pass
            if hasattr(self, 'saturation_min_entry'):
                try:
                    self.config['effects_settings']['saturation_min'] = float(self.saturation_min_entry.text())
                except:
                    pass
            if hasattr(self, 'saturation_max_entry'):
                try:
                    self.config['effects_settings']['saturation_max'] = float(self.saturation_max_entry.text())
                except:
                    pass

            self.save_config_to_file()
        except Exception as e:
            self.log(f"⚠️ Ошибка автосохранения: {e}")

    def save_instagram_settings(self):
        """Save Instagram settings"""
        config = load_config()

        # Save hashtags setting
        if hasattr(self, 'hashtags_checkbox'):
            config['add_hashtags'] = self.hashtags_checkbox.isChecked()

        # Save use descriptions setting
        if hasattr(self, 'use_descriptions_checkbox'):
            config['use_descriptions'] = self.use_descriptions_checkbox.isChecked()

        # Save upload threads setting
        if hasattr(self, 'upload_threads_slider'):
            config['upload_threads'] = self.upload_threads_slider.value()

        save_config(config)
        self.log("✅ Настройки Instagram сохранены")

    def start_uniquifier(self):
        """Start video uniquifier"""
        if self.process_thread and self.process_thread.isRunning():
            self.log("⚠️ Уникализация уже запущена")
            return

        self.log("🎬 Запуск уникализатора...")
        self.status_label.setText("● РАБОТАЕТ")
        self.status_label.setProperty("class", "status-working")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffaa00;")
        self.process_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.process_thread = ProcessThread(self.config)
        self.process_thread.log_signal.connect(self.log)
        self.process_thread.finished_signal.connect(self.uniquifier_finished)
        self.process_thread.start()

    def uniquifier_finished(self):
        """Called when uniquifier finishes"""
        self.status_label.setText("● ГОТОВА")
        self.status_label.setProperty("class", "status-ready")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ccff;")
        self.process_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.update_stats()

    def start_uniquifier_with_selected(self, selected_videos):
        """Запуск уникализатора для выбранных видео"""
        if self.process_thread and self.process_thread.isRunning():
            self.log("⚠️ Уникализация уже запущена")
            return

        self.log(f"🎬 Запуск уникализатора для {len(selected_videos)} выбранных видео...")
        self.status_label.setText("● РАБОТАЕТ")
        self.status_label.setProperty("class", "status-working")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffaa00;")
        self.selective_unique_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # Создаем поток с указанными видео
        self.process_thread = ProcessThread(self.config, selected_videos=selected_videos)
        self.process_thread.log_signal.connect(self.log)
        self.process_thread.finished_signal.connect(self.selective_uniquifier_finished)
        self.process_thread.start()

    def selective_uniquifier_finished(self):
        """Called when selective uniquifier finishes"""
        self.status_label.setText("● ГОТОВА")
        self.status_label.setProperty("class", "status-ready")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ccff;")
        self.selective_unique_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.update_stats()
        self.log("✅ Уникализация выбранных видео завершена")

    def start_upload(self):
        """Start Instagram upload"""
        if self.upload_thread and self.upload_thread.isRunning():
            self.log("⚠️ Загрузка уже запущена")
            return

        if not self.accounts:
            self.log("❌ Нет аккаунтов для загрузки")
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один аккаунт")
            return

        config = load_config()
        upload_threads = config.get("upload_threads", 2)
        use_descriptions = config.get("use_descriptions", True)

        # Используем descriptions только если включена настройка
        descriptions = self.descriptions if use_descriptions else []

        self.log("📤 Запуск загрузки на Instagram...")
        self.log(f"⚙️ Количество потоков: {upload_threads}")
        self.log(f"📝 Использовать описания: {'Да' if use_descriptions else 'Нет'}")
        self.status_label.setText("● РАБОТАЕТ")
        self.status_label.setProperty("class", "status-working")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffaa00;")
        self.upload_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.upload_thread = UploadThread(self.accounts, descriptions, config)
        self.upload_thread.log_signal.connect(self.log)
        self.upload_thread.finished_signal.connect(self.upload_finished)
        self.upload_thread.refresh_table_signal.connect(self.refresh_accounts_table)  # Обновление таблицы в реальном времени
        self.upload_thread.start()

    def upload_finished(self):
        """Called when upload finishes"""
        self.status_label.setText("● ГОТОВА")
        self.status_label.setProperty("class", "status-ready")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ccff;")
        self.upload_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def start_selective_upload(self):
        """Загрузка видео на выбранные аккаунты"""
        if not self.accounts:
            QMessageBox.warning(self, "Ошибка", "Нет доступных аккаунтов")
            return

        # Диалог выбора аккаунтов
        dialog = AccountSelectionDialog(self.accounts, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_accounts = dialog.get_selected_accounts()
            if not selected_accounts:
                QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один аккаунт")
                return

            self.log(f"📮 Выбрано аккаунтов: {len(selected_accounts)}")
            config = load_config()
            use_descriptions = config.get("use_descriptions", True)
            descriptions = self.descriptions if use_descriptions else []

            self.status_label.setText("● РАБОТАЕТ")
            self.status_label.setProperty("class", "status-working")
            self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffaa00;")
            self.selective_upload_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

            self.upload_thread = UploadThread(selected_accounts, descriptions, config)
            self.upload_thread.log_signal.connect(self.log)
            self.upload_thread.finished_signal.connect(lambda: self.selective_upload_finished())
            self.upload_thread.refresh_table_signal.connect(self.refresh_accounts_table)  # Обновление таблицы в реальном времени
            self.upload_thread.start()

    def selective_upload_finished(self):
        """Called when selective upload finishes"""
        self.status_label.setText("● ГОТОВА")
        self.status_label.setProperty("class", "status-ready")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ccff;")
        self.selective_upload_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log("✅ Загрузка на выбранные аккаунты завершена")

    def start_selective_uniquify(self):
        """Уникализация выбранных видео"""
        input_folder = self.config.get('input_folder', 'unik/input')

        if not os.path.exists(input_folder):
            QMessageBox.warning(self, "Ошибка", f"Папка {input_folder} не найдена")
            return

        # Получаем список видео
        video_files = [f for f in os.listdir(input_folder)
                      if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

        if not video_files:
            QMessageBox.warning(self, "Ошибка", f"Нет видео в папке {input_folder}")
            return

        # Диалог выбора видео с предпросмотром
        dialog = VideoSelectionDialog(input_folder, video_files, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_videos = dialog.get_selected_videos()
            if not selected_videos:
                QMessageBox.warning(self, "Ошибка", "Выберите хотя бы одно видео")
                return

            self.log(f"🎞️ Выбрано видео: {len(selected_videos)}")
            self.start_uniquifier_with_selected(selected_videos)

    def start_all_in_one(self):
        """Start uniquifier then upload"""
        if (self.process_thread and self.process_thread.isRunning()) or \
           (self.upload_thread and self.upload_thread.isRunning()):
            self.log("⚠️ Процесс уже запущен")
            return

        if not self.accounts:
            self.log("❌ Нет аккаунтов для загрузки")
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один аккаунт")
            return

        config = load_config()
        upload_threads = config.get("upload_threads", 2)

        self.log("⚡ Запуск полного цикла: Уникализация + Загрузка")
        self.log(f"⚙️ Количество потоков для загрузки: {upload_threads}")
        self.status_label.setText("● РАБОТАЕТ")
        self.status_label.setProperty("class", "status-working")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffaa00;")
        self.all_in_one_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.process_thread = ProcessThread(self.config)
        self.process_thread.log_signal.connect(self.log)
        self.process_thread.finished_signal.connect(self.all_in_one_phase2)
        self.process_thread.start()

    def all_in_one_phase2(self):
        """Phase 2: Start upload after uniquifier"""
        self.log("📤 Переход к загрузке на Instagram...")

        config = load_config()
        self.upload_thread = UploadThread(self.accounts, self.descriptions, config)
        self.upload_thread.log_signal.connect(self.log)
        self.upload_thread.finished_signal.connect(self.all_in_one_finished)
        self.upload_thread.refresh_table_signal.connect(self.refresh_accounts_table)  # Обновление таблицы в реальном времени
        self.upload_thread.start()

    def all_in_one_finished(self):
        """Called when all-in-one finishes"""
        self.status_label.setText("● ГОТОВА")
        self.status_label.setProperty("class", "status-ready")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ccff;")
        self.all_in_one_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log("🎉 Полный цикл завершён!")
        QMessageBox.information(self, "Готово", "Полный цикл успешно завершён!")

    def get_reels_statistics(self):
        """Get reels statistics"""
        if self.statistics_thread and self.statistics_thread.isRunning():
            self.log("⚠️ Получение статистики уже выполняется")
            return

        if not self.accounts:
            self.log("❌ Нет аккаунтов")
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один аккаунт")
            return

        # Get selected account
        selected_username = self.stats_account_combo.currentData()
        num_clips = self.stats_clips_spin.value()

        self.log("📊 Запуск получения статистики...")
        self.status_label.setText("● РАБОТАЕТ")
        self.status_label.setProperty("class", "status-working")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffaa00;")

        self.statistics_thread = StatisticsThread(self.accounts, selected_username, num_clips)
        self.statistics_thread.log_signal.connect(self.log)
        self.statistics_thread.stats_signal.connect(self.display_statistics)
        self.statistics_thread.finished_signal.connect(self.statistics_finished)
        self.statistics_thread.start()

    def display_statistics(self, statistics):
        """Display statistics in table"""
        self.stats_table.setRowCount(0)

        if not statistics:
            self.log("⚠️ Нет данных для отображения")
            return

        row = 0
        for username, data in statistics.items():
            if "error" in data:
                # Add error row
                self.stats_table.insertRow(row)
                self.stats_table.setItem(row, 0, QTableWidgetItem(username))
                error_item = QTableWidgetItem(data["error"])
                error_item.setForeground(QColor("#ff4444"))
                self.stats_table.setItem(row, 1, error_item)
                row += 1
                continue

            clips = data.get("clips", [])
            if not clips:
                # Add no clips row
                self.stats_table.insertRow(row)
                self.stats_table.setItem(row, 0, QTableWidgetItem(username))
                self.stats_table.setItem(row, 1, QTableWidgetItem("Нет рилсов"))
                row += 1
                continue

            for clip in clips:
                self.stats_table.insertRow(row)

                # Account with emoji
                account_item = QTableWidgetItem(f"👤 {username}")
                account_item.setForeground(QColor("#00ffff"))
                self.stats_table.setItem(row, 0, account_item)

                # Caption with emoji
                caption = clip.get('caption', 'Без описания')
                caption_item = QTableWidgetItem(f"📝 {caption}")
                caption_item.setForeground(QColor("#e8eaf0"))
                self.stats_table.setItem(row, 1, caption_item)

                # Date with emoji
                taken_at = clip.get('taken_at', 'N/A')
                date_item = QTableWidgetItem(f"📅 {taken_at}")
                date_item.setForeground(QColor("#a0a8b8"))
                self.stats_table.setItem(row, 2, date_item)

                # Likes with emoji
                likes = str(clip.get('like_count', 0))
                likes_item = QTableWidgetItem(f"❤️ {likes}")
                likes_item.setForeground(QColor("#ff6b9d"))
                self.stats_table.setItem(row, 3, likes_item)

                # Comments with emoji
                comments = str(clip.get('comment_count', 0))
                comments_item = QTableWidgetItem(f"💬 {comments}")
                comments_item.setForeground(QColor("#4dabf7"))
                self.stats_table.setItem(row, 4, comments_item)

                # Views with emoji (prefer play_count over view_count)
                views = clip.get('play_count', clip.get('view_count', 'N/A'))
                views_item = QTableWidgetItem(f"👁️ {views}")
                views_item.setForeground(QColor("#51cf66"))
                self.stats_table.setItem(row, 5, views_item)

                row += 1

        self.log(f"✅ Отображено {row} записей")

    def statistics_finished(self):
        """Called when statistics collection finishes"""
        self.status_label.setText("● ГОТОВА")
        self.status_label.setProperty("class", "status-ready")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ccff;")

    def stop_processing(self):
        """Stop current processing"""
        self.stop_requested = True
        self.log("⏹ Остановка запрошена...")


def main():
    app = QApplication(sys.argv)
    window = InstagramUploaderGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
