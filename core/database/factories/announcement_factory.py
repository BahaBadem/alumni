"""
core/database/factories/announcement_factory.py - Announcement Model Factory

Bu modül, testler ve seeder operasyonları için gerçekçi Announcement model
örnekleri üretmek üzere Factory Pattern uygular.
"""

import random
from typing import Dict, Any
from core.models import Announcement
from core.database.base import BaseFactory
from core.database.data_pools import (
    SEED_ANNOUNCEMENT_TEMPLATES,
    get_random_announcement_author,
    get_random_announcement_category,
)


class AnnouncementFactory(BaseFactory[Announcement]):
    """
    Announcement ORM modeli için nesne üreteci (Factory).

    Kullanım:
        factory = AnnouncementFactory()
        ann_in_memory = factory.build()
        ann_in_db = factory.create(category="Kariyer")
        batch_anns = factory.create_batch(5)
    """
    model_class = Announcement

    def definition(self) -> Dict[str, Any]:
        """Varsayılan gerçekçi duyuru alan tanımları."""
        template = random.choice(SEED_ANNOUNCEMENT_TEMPLATES)
        
        # Hafif varyasyon katmak için dinamik ekleme yapılabilir
        suffix_years = ["2026", "Güz Dönemi", "Bahar Dönemi", "Online", "Merkez Kampüs"]
        chosen_suffix = random.choice(suffix_years)

        title = f"{template['title']} ({chosen_suffix})"
        
        return {
            "title": title,
            "content": template["content"],
            "author": template.get("author") or get_random_announcement_author(),
            "category": template.get("category") or get_random_announcement_category(),
            "is_active": True,
        }
