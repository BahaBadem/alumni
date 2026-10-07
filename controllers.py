"""
controllers.py - Kök Dizin Controller Köprüsü (MVC)

Bu modül, core/controllers altındaki UserController ve ApiUserController
sınıflarını kök dizinden doğrudan erişilebilir hale getirir.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.controllers.user_controller import UserController, user_controller_view
from core.controllers.api_user_controller import ApiUserController, api_user_controller_view

__all__ = [
    "UserController",
    "user_controller_view",
    "ApiUserController",
    "api_user_controller_view",
]
