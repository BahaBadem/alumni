"""
core/management/commands/seed.py - Veritabanı Tohumlama Yönetim Komutu

Kullanım:
    python manage.py seed
    python manage.py seed --users 20 --announcements 10
    python manage.py seed --fresh --no-input
    python manage.py seed --seed 42
"""

import random
from django.core.management.base import BaseCommand, CommandError
from core.database.seeders.database_seeder import DatabaseSeeder


class Command(BaseCommand):
    help = "Alumni Portal veritabanını kapsamlı ve idempotent test/demo verileriyle tohumlar."

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=10,
            help="Üretilecek dinamik kullanıcı adedi (Varsayılan: 10)",
        )
        parser.add_argument(
            "--announcements",
            type=int,
            default=5,
            help="Üretilecek dinamik duyuru adedi (Varsayılan: 5)",
        )
        parser.add_argument(
            "--jobs",
            type=int,
            default=10,
            help="Üretilecek dinamik iş & staj ilanı adedi (Varsayılan: 10)",
        )
        parser.add_argument(
            "--jobs-only",
            action="store_true",
            help="Sadece iş & staj ilanları (JobPosting) tablosunu tohumlar.",
        )
        parser.add_argument(
            "--fresh",
            action="store_true",
            help="Tohumlamadan önce veritabanındaki mevcut kayıtları sıfırlar.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="--fresh ile aynı: Mevcut verileri sıfırlar ve tohumlar.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Deterministik ve tekrarlanabilir veri üretimi için rastgelelik tohumu (random seed).",
        )
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Kullanıcı onay sorularını sormadan doğrudan icra eder.",
        )

    def handle(self, *args, **options):
        users_count = options["users"]
        announcements_count = options["announcements"]
        jobs_count = options["jobs"]
        jobs_only = options["jobs_only"]
        is_fresh = options["fresh"] or options["clear"]
        random_seed = options["seed"]
        no_input = options["no_input"]

        if random_seed is not None:
            random.seed(random_seed)
            self.stdout.write(self.style.NOTICE(f"🎲 Rastgelelik tohumu ayarlandı: {random_seed}"))

        seeder = DatabaseSeeder()

        if jobs_only:
            self.stdout.write(self.style.HTTP_INFO("🌱 Yalnızca İş & Staj İlanları tohumlanıyor (İdempotent mod)..."))
            report = seeder.seed_jobs_only(count=jobs_count)
            job_info = report["jobs"]
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("✨ İŞ İLANLARI TOHUMLAMA (SEED) BAŞARIYLA TAMAMLANDI!"))
            self.stdout.write("=" * 60)
            self.stdout.write(
                f"💼 İş & Staj İlanları  : +{job_info['created']} yeni eklendi "
                f"({job_info['existing']} zaten vardı) -> Toplam: {job_info['total']}"
            )
            self.stdout.write("=" * 60 + "\n")
            return

        if is_fresh:
            if not no_input:
                confirm = input("⚠️  DİKKAT: Veritabanındaki kayıtlar temizlenecek! Devam edilsin mi? (e/h): ")
                if confirm.lower() not in ("e", "evet", "y", "yes"):
                    self.stdout.write(self.style.WARNING("İşlem kullanıcı tarafından iptal edildi."))
                    return

            self.stdout.write(self.style.WARNING("🧹 Mevcut veritabanı kayıtları temizleniyor..."))
            report = seeder.seed_fresh(
                users_count=users_count,
                announcements_count=announcements_count,
                jobs_count=jobs_count,
            )
            self.stdout.write(self.style.SUCCESS(f"  └─ {report.get('deleted_before_seed', 0)} kayıt silindi."))
        else:
            self.stdout.write(self.style.HTTP_INFO("🌱 Veritabanı tohumlama işlemi başlatılıyor (İdempotent mod)..."))
            report = seeder.seed(
                users_count=users_count,
                announcements_count=announcements_count,
                jobs_count=jobs_count,
            )

        users_info = report["users"]
        ann_info = report["announcements"]
        job_info = report.get("jobs", {"created": 0, "existing": 0, "total": 0})

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✨ VERİTABANI TOHUMLAMA (SEED) BAŞARIYLA TAMAMLANDI!"))
        self.stdout.write("=" * 60)
        self.stdout.write(
            f"👤 Kullanıcı Profilleri : +{users_info['created']} yeni eklendi "
            f"({users_info['existing']} zaten vardı) -> Toplam: {users_info['total']}"
        )
        self.stdout.write(
            f"📢 Duyurular           : +{ann_info['created']} yeni eklendi "
            f"({ann_info['existing']} zaten vardı) -> Toplam: {ann_info['total']}"
        )
        self.stdout.write(
            f"💼 İş & Staj İlanları  : +{job_info['created']} yeni eklendi "
            f"({job_info['existing']} zaten vardı) -> Toplam: {job_info['total']}"
        )
        self.stdout.write("=" * 60 + "\n")
