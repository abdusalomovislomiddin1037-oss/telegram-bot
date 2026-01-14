"""
SmartWallet AI Bot - Colors
===========================
Rang palitrasi va ranglar bilan ishlash

Functions:
    - get_category_color: Kategoriya rangini olish
    - get_color_palette: Rang palitrasini olish
    - hex_to_rgb: HEX → RGB konversiya
    - rgb_to_hex: RGB → HEX konversiya

Author: SmartWallet AI Team
Version: 1.0.0
"""

from typing import Tuple, List, Optional
from config import Categories


# =====================================================
# GET CATEGORY COLOR
# =====================================================
def get_category_color(category_key: str) -> str:
    """
    Kategoriya rangini olish
    
    Args:
        category_key: Kategoriya key
        
    Returns:
        str: HEX rang (#RRGGBB)
    """
    return Categories.get_color(category_key)


# =====================================================
# GET COLOR PALETTE
# =====================================================
def get_color_palette() -> List[str]:
    """
    Barcha kategoriya ranglarini olish
    
    Returns:
        List[str]: Ranglar ro'yxati
    """
    return [cat['color'] for cat in Categories.LIST]


# =====================================================
# HEX TO RGB
# =====================================================
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    HEX rangni RGB ga o'girish
    
    Args:
        hex_color: HEX rang (#RRGGBB yoki RRGGBB)
        
    Returns:
        Tuple[int, int, int]: (R, G, B) 0-255
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# =====================================================
# RGB TO HEX
# =====================================================
def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    RGB ni HEX ga o'girish
    
    Args:
        r: Qizil (0-255)
        g: Yashil (0-255)
        b: Ko'k (0-255)
        
    Returns:
        str: HEX rang (#RRGGBB)
    """
    return f'#{r:02x}{g:02x}{b:02x}'


# =====================================================
# LIGHTEN COLOR
# =====================================================
def lighten_color(hex_color: str, factor: float = 0.2) -> str:
    """
    Rangni ochroq qilish
    
    Args:
        hex_color: HEX rang
        factor: Ochroqlik darajasi (0-1)
        
    Returns:
        str: Yangi HEX rang
    """
    r, g, b = hex_to_rgb(hex_color)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return rgb_to_hex(r, g, b)


# =====================================================
# DARKEN COLOR
# =====================================================
def darken_color(hex_color: str, factor: float = 0.2) -> str:
    """
    Rangni quyuroq qilish
    
    Args:
        hex_color: HEX rang
        factor: Quyuroqlik darajasi (0-1)
        
    Returns:
        str: Yangi HEX rang
    """
    r, g, b = hex_to_rgb(hex_color)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return rgb_to_hex(r, g, b)
