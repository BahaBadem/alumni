"""
core/user.py - Kök dizindeki user.py modülünün core paketi altındaki eşdeğeri.
"""
from user import (
    create_user,
    add_user,
    get_user,
    get_user_by_id,
    get_all_users,
    filter_users,
    update_user,
    patch_user,
    delete_user,
    delete_all_users,
    count_users,
    clear_storage,
    seed_demo_users,
)

__all__ = [
    "create_user",
    "add_user",
    "get_user",
    "get_user_by_id",
    "get_all_users",
    "filter_users",
    "update_user",
    "patch_user",
    "delete_user",
    "delete_all_users",
    "count_users",
    "clear_storage",
    "seed_demo_users",
]
