"""
SmartWallet AI Bot - Charts Generator
=====================================
Matplotlib va Plotly yordamida grafiklar yaratish

Functions:
    - create_pie_chart: Donut chart (kategoriyalar)
    - create_line_chart: Line chart (trend)
    - create_bar_chart: Bar chart (taqqoslash)
    - save_chart_to_file: Faylga saqlash

Author: SmartWallet AI Team
Version: 1.0.0
"""

import io
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal

import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
import seaborn as sns

from config import ReportConfig, Categories, Paths
from utils.colors import get_category_color, hex_to_rgb

# Logger
logger = logging.getLogger(__name__)

# Seaborn style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = ReportConfig.CHART_DPI


# =====================================================
# PIE CHART (DONUT)
# =====================================================
def create_pie_chart(
    data: List[Dict[str, Any]],
    title: str = "Xarajatlar taqsimoti",
    language: str = 'uz',
    save_path: Optional[Path] = None
) -> io.BytesIO:
    """
    Donut chart yaratish (kategoriyalar bo'yicha)
    
    Args:
        data: [{'category': Category, 'total': Decimal, 'count': int}, ...]
        title: Grafik sarlavhasi
        language: Til kodi
        save_path: Saqlash yo'li (optional)
        
    Returns:
        io.BytesIO: PNG buffer
    """
    try:
        # Ma'lumotlarni tayyorlash
        labels = []
        sizes = []
        colors = []
        
        for item in data:
            category = item['category']
            total = float(item['total'])
            
            # Kategoriya nomi (emoji bilan)
            name = category.get_name(language)
            label = f"{category.icon} {name}"
            
            labels.append(label)
            sizes.append(total)
            colors.append(category.color)
        
        # Agar ma'lumot bo'sh bo'lsa
        if not sizes:
            logger.warning("Pie chart uchun ma'lumot yo'q")
            return create_empty_chart("Ma'lumot topilmadi")
        
        # Figure yaratish
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Donut chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85,
            textprops={'fontsize': 11, 'weight': 'bold'}
        )
        
        # Donut effekti (markazda oq doira)
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)
        
        # Prosentlarni oq rangda qilish
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
        
        # Sarlavha
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        
        # Equal aspect ratio
        ax.axis('equal')
        
        # Tight layout
        plt.tight_layout()
        
        # Faylga saqlash (agar kerak bo'lsa)
        if save_path:
            plt.savefig(save_path, format='png', dpi=ReportConfig.CHART_DPI, bbox_inches='tight')
            logger.info(f"Pie chart saqlandi: {save_path}")
        
        # BytesIO'ga saqlash
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=ReportConfig.CHART_DPI, bbox_inches='tight')
        buffer.seek(0)
        
        plt.close(fig)
        
        return buffer
        
    except Exception as e:
        logger.error(f"create_pie_chart xatosi: {e}")
        return create_empty_chart("Xatolik yuz berdi")


# =====================================================
# LINE CHART
# =====================================================
def create_line_chart(
    data: List[Dict[str, Any]],
    title: str = "Kunlik xarajatlar trendi",
    xlabel: str = "Sana",
    ylabel: str = "Summa (so'm)",
    save_path: Optional[Path] = None
) -> io.BytesIO:
    """
    Line chart yaratish (trend)
    
    Args:
        data: [{'date': date, 'total': Decimal}, ...]
        title: Grafik sarlavhasi
        xlabel: X o'qi nomi
        ylabel: Y o'qi nomi
        save_path: Saqlash yo'li (optional)
        
    Returns:
        io.BytesIO: PNG buffer
    """
    try:
        # Ma'lumotlarni tayyorlash
        dates = []
        amounts = []
        
        for item in data:
            dates.append(item['date'])
            amounts.append(float(item['total']))
        
        # Agar ma'lumot bo'sh bo'lsa
        if not dates:
            logger.warning("Line chart uchun ma'lumot yo'q")
            return create_empty_chart("Ma'lumot topilmadi")
        
        # Figure yaratish
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Line plot
        ax.plot(
            dates,
            amounts,
            marker='o',
            linewidth=2.5,
            markersize=8,
            color='#ef4444',
            markerfacecolor='#ef4444',
            markeredgecolor='white',
            markeredgewidth=2
        )
        
        # Fill area
        ax.fill_between(dates, amounts, alpha=0.2, color='#ef4444')
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Labels
        ax.set_xlabel(xlabel, fontsize=12, weight='bold')
        ax.set_ylabel(ylabel, fontsize=12, weight='bold')
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        
        # Format Y axis (add thousand separators)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', ' ')))
        
        # Rotate X labels
        plt.xticks(rotation=45, ha='right')
        
        # Tight layout
        plt.tight_layout()
        
        # Faylga saqlash (agar kerak bo'lsa)
        if save_path:
            plt.savefig(save_path, format='png', dpi=ReportConfig.CHART_DPI, bbox_inches='tight')
            logger.info(f"Line chart saqlandi: {save_path}")
        
        # BytesIO'ga saqlash
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=ReportConfig.CHART_DPI, bbox_inches='tight')
        buffer.seek(0)
        
        plt.close(fig)
        
        return buffer
        
    except Exception as e:
        logger.error(f"create_line_chart xatosi: {e}")
        return create_empty_chart("Xatolik yuz berdi")


# =====================================================
# BAR CHART
# =====================================================
def create_bar_chart(
    data: List[Dict[str, Any]],
    title: str = "Eng ko'p xarajatlar",
    xlabel: str = "Kategoriya",
    ylabel: str = "Summa (so'm)",
    language: str = 'uz',
    horizontal: bool = False,
    save_path: Optional[Path] = None
) -> io.BytesIO:
    """
    Bar chart yaratish
    
    Args:
        data: [{'category': Category, 'total': Decimal}, ...]
        title: Grafik sarlavhasi
        xlabel: X o'qi nomi
        ylabel: Y o'qi nomi
        language: Til kodi
        horizontal: Gorizontal bar chart
        save_path: Saqlash yo'li (optional)
        
    Returns:
        io.BytesIO: PNG buffer
    """
    try:
        # Ma'lumotlarni tayyorlash
        labels = []
        amounts = []
        colors = []
        
        for item in data:
            category = item['category']
            total = float(item['total'])
            
            # Kategoriya nomi
            name = category.get_name(language)
            label = f"{category.icon} {name}"
            
            labels.append(label)
            amounts.append(total)
            colors.append(category.color)
        
        # Agar ma'lumot bo'sh bo'lsa
        if not labels:
            logger.warning("Bar chart uchun ma'lumot yo'q")
            return create_empty_chart("Ma'lumot topilmadi")
        
        # Figure yaratish
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Bar chart
        if horizontal:
            bars = ax.barh(labels, amounts, color=colors, edgecolor='white', linewidth=1.5)
            ax.set_xlabel(ylabel, fontsize=12, weight='bold')
            ax.set_ylabel(xlabel, fontsize=12, weight='bold')
        else:
            bars = ax.bar(labels, amounts, color=colors, edgecolor='white', linewidth=1.5)
            ax.set_xlabel(xlabel, fontsize=12, weight='bold')
            ax.set_ylabel(ylabel, fontsize=12, weight='bold')
            plt.xticks(rotation=45, ha='right')
        
        # Har bir bar ustiga summa yozish
        for i, bar in enumerate(bars):
            if horizontal:
                width = bar.get_width()
                ax.text(
                    width,
                    bar.get_y() + bar.get_height() / 2,
                    f' {int(amounts[i]):,}'.replace(',', ' '),
                    ha='left',
                    va='center',
                    fontsize=10,
                    weight='bold'
                )
            else:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    f'{int(amounts[i]):,}'.replace(',', ' '),
                    ha='center',
                    va='bottom',
                    fontsize=10,
                    weight='bold'
                )
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--', axis='y' if not horizontal else 'x')
        
        # Title
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        
        # Format axis
        if horizontal:
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', ' ')))
        else:
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', ' ')))
        
        # Tight layout
        plt.tight_layout()
        
        # Faylga saqlash (agar kerak bo'lsa)
        if save_path:
            plt.savefig(save_path, format='png', dpi=ReportConfig.CHART_DPI, bbox_inches='tight')
            logger.info(f"Bar chart saqlandi: {save_path}")
        
        # BytesIO'ga saqlash
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=ReportConfig.CHART_DPI, bbox_inches='tight')
        buffer.seek(0)
        
        plt.close(fig)
        
        return buffer
        
    except Exception as e:
        logger.error(f"create_bar_chart xatosi: {e}")
        return create_empty_chart("Xatolik yuz berdi")


# =====================================================
# COMBINED CHART (Pie + Bar)
# =====================================================
def create_combined_chart(
    pie_data: List[Dict[str, Any]],
    bar_data: List[Dict[str, Any]],
    title: str = "Xarajatlar tahlili",
    language: str = 'uz',
    save_path: Optional[Path] = None
) -> io.BytesIO:
    """
    Birlashtirilgan grafik (Pie + Bar)
    
    Args:
        pie_data: Pie chart ma'lumotlari
        bar_data: Bar chart ma'lumotlari
        title: Sarlavha
        language: Til kodi
        save_path: Saqlash yo'li
        
    Returns:
        io.BytesIO: PNG buffer
    """
    try:
        # Figure yaratish
        fig = plt.figure(figsize=(16, 8))
        
        # 2 ta subplot
        ax1 = plt.subplot(1, 2, 1)
        ax2 = plt.subplot(1, 2, 2)
        
        # Pie chart (chapda)
        labels = []
        sizes = []
        colors = []
        
        for item in pie_data:
            category = item['category']
            total = float(item['total'])
            name = category.get_name(language)
            label = f"{category.icon} {name}"
            labels.append(label)
            sizes.append(total)
            colors.append(category.color)
        
        if sizes:
            wedges, texts, autotexts = ax1.pie(
                sizes,
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                pctdistance=0.85
            )
            
            # Donut
            centre_circle = plt.Circle((0, 0), 0.70, fc='white')
            ax1.add_artist(centre_circle)
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(10)
            
            ax1.set_title("Taqsimot", fontsize=14, weight='bold')
            ax1.axis('equal')
        
        # Bar chart (o'ngda)
        bar_labels = []
        bar_amounts = []
        bar_colors = []
        
        for item in bar_data:
            category = item['category']
            total = float(item['total'])
            name = category.get_name(language)
            bar_labels.append(f"{category.icon} {name}")
            bar_amounts.append(total)
            bar_colors.append(category.color)
        
        if bar_amounts:
            bars = ax2.barh(bar_labels, bar_amounts, color=bar_colors, edgecolor='white', linewidth=1.5)
            
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax2.text(
                    width,
                    bar.get_y() + bar.get_height() / 2,
                    f' {int(bar_amounts[i]):,}'.replace(',', ' '),
                    ha='left',
                    va='center',
                    fontsize=9,
                    weight='bold'
                )
            
            ax2.set_xlabel("Summa (so'm)", fontsize=12, weight='bold')
            ax2.set_title("Taqqoslash", fontsize=14, weight='bold')
            ax2.grid(True, alpha=0.3, linestyle='--', axis='x')
            ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', ' ')))
        
        # Umumiy sarlavha
        fig.suptitle(title, fontsize=18, weight='bold')
        
        plt.tight_layout()
        
        # Save
        if save_path:
            plt.savefig(save_path, format='png', dpi=ReportConfig.CHART_DPI, bbox_inches='tight')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=ReportConfig.CHART_DPI, bbox_inches='tight')
        buffer.seek(0)
        
        plt.close(fig)
        
        return buffer
        
    except Exception as e:
        logger.error(f"create_combined_chart xatosi: {e}")
        return create_empty_chart("Xatolik yuz berdi")


# =====================================================
# EMPTY CHART (placeholder)
# =====================================================
def create_empty_chart(message: str = "Ma'lumot topilmadi") -> io.BytesIO:
    """
    Bo'sh grafik (placeholder)
    
    Args:
        message: Xabar
        
    Returns:
        io.BytesIO: PNG buffer
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.text(
        0.5, 0.5,
        message,
        ha='center',
        va='center',
        fontsize=18,
        weight='bold',
        color='gray'
    )
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    
    plt.close(fig)
    
    return buffer


# =====================================================
# SAVE CHART TO FILE
# =====================================================
def save_chart_to_file(
    buffer: io.BytesIO,
    filename: str,
    directory: Optional[Path] = None
) -> Path:
    """
    Chart'ni faylga saqlash
    
    Args:
        buffer: BytesIO buffer
        filename: Fayl nomi
        directory: Papka (default: REPORTS_DIR)
        
    Returns:
        Path: Saqlangan fayl yo'li
    """
    try:
        if directory is None:
            directory = Paths.REPORTS_DIR
        
        # Papkani yaratish
        directory.mkdir(parents=True, exist_ok=True)
        
        # Fayl yo'li
        file_path = directory / filename
        
        # Saqlash
        with open(file_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        logger.info(f"Chart saqlandi: {file_path}")
        
        return file_path
        
    except Exception as e:
        logger.error(f"save_chart_to_file xatosi: {e}")
        raise


# =====================================================
# CHART CONFIGURATION
# =====================================================
def set_chart_style(style: str = 'seaborn-v0_8'):
    """
    Grafik stilini o'rnatish
    
    Args:
        style: Stil nomi
    """
    try:
        plt.style.use(style)
        logger.info(f"Chart style o'rnatildi: {style}")
    except Exception as e:
        logger.warning(f"Chart style o'rnatishda xato: {e}")


def get_chart_size(device_type: str = 'computer') -> Tuple[int, int]:
    """
    Gadjet turiga qarab grafik o'lchamini olish
    
    Args:
        device_type: 'phone', 'tablet', 'computer'
        
    Returns:
        Tuple[int, int]: (width, height) in pixels
    """
    sizes = {
        'phone': (800, 600),
        'tablet': (1024, 768),
        'computer': (1200, 800)
    }
    
    return sizes.get(device_type, sizes['computer'])
