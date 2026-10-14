"""
core/database/factories/user_factory.py - UserProfile Model Factory

Bu modül, testler ve seeder operasyonları için gerçekçi UserProfile model
örnekleri üretmek üzere Factory Pattern uygular.
"""

from typing import Dict, Any
from core.models import UserProfile
from core.database.base import BaseFactory
from core.database.data_pools import (
    get_random_name,
    get_random_city,
    get_random_school,
    get_random_birth_date,
)


class UserProfileFactory(BaseFactory[UserProfile]):
    """
    UserProfile ORM modeli için nesne üreteci (Factory).
    
    Kullanım:
        factory = UserProfileFactory()
        user_in_memory = factory.build()
        user_in_db = factory.create(city="İstanbul")
        batch_users = factory.create_batch(10)
    """
    model_class = UserProfile

    def definition(self) -> Dict[str, Any]:
        """Varsayılan gerçekçi alan tanımları."""
        return {
            "name": get_random_name(),
            "birth_date": get_random_birth_date(min_age=22, max_age=48),
            "city": get_random_city(),
            "school": get_random_school(),
        }
