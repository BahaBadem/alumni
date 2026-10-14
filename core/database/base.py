"""
core/database/base.py - Base Factory ve Base Seeder Soyut Sınıfları

Bu modül, Alumni Portal projesindeki tüm Factory ve Seeder sınıfları için
ortak arayüzleri, abstract metotları ve batch operasyonlarını tanımlar.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Dict, Any, Optional
from django.db import models, transaction

T = TypeVar('T', bound=models.Model)


class BaseFactory(Generic[T], ABC):
    """
    Model nesneleri üretmek için temel Factory soyut sınıfı.

    Türeyecek sınıflar `model_class` ve `definition()` metodunu sağlamalıdır.
    """
    model_class: type[T]

    @abstractmethod
    def definition(self) -> Dict[str, Any]:
        """
        Model için varsayılan alan değerlerini sözlük olarak döner.
        """
        raise NotImplementedError("Factory alt sınıfları definition() metodunu uygulamalıdır.")

    def build(self, **overrides) -> T:
        """
        Model nesnesini bellekte oluşturur fakat veritabanına kaydetmez.
        """
        attributes = self.definition()
        attributes.update(overrides)
        return self.model_class(**attributes)

    def create(self, **overrides) -> T:
        """
        Model nesnesini oluşturur ve veritabanına kaydeder.
        """
        instance = self.build(**overrides)
        instance.save()
        return instance

    def build_batch(self, count: int, **overrides) -> List[T]:
        """
        Belirtilen adette model nesnesini bellekte oluşturur.
        """
        return [self.build(**overrides) for _ in range(count)]

    def create_batch(self, count: int, **overrides) -> List[T]:
        """
        Belirtilen adette model nesnesini oluşturur ve toplu/tekil olarak veritabanına kaydeder.
        """
        instances = []
        with transaction.atomic():
            for _ in range(count):
                instances.append(self.create(**overrides))
        return instances


class BaseSeeder(ABC):
    """
    Veritabanına başlangıç ve demo verilerini yükleyen Seeder soyut sınıfı.

    Tüm seeder'lar idempotent (tekrar çalıştırılabilir) olmalı,
    mükerrer kayıt oluşturmamalı ve gerektiğinde temizleme yapabilmelidir.
    """
    name: str = "BaseSeeder"

    @abstractmethod
    def seed(self, count: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Veritabanını tohumlar (seed eder).

        Returns:
            Dict[str, Any]: İşlem özeti (örn: {'created': 10, 'skipped': 2})
        """
        raise NotImplementedError("Seeder alt sınıfları seed() metodunu uygulamalıdır.")

    @abstractmethod
    def clear(self) -> int:
        """
        Bu seeder tarafından yönetilen/oluşturulan kayıtları temizler.

        Returns:
            int: Silinen kayıt sayısı
        """
        raise NotImplementedError("Seeder alt sınıfları clear() metodunu uygulamalıdır.")
