"""
test_in_memory_user.py - In-Memory User Modeli ve CRUD Fonksiyonları Birim Testleri
Harici veritabanı bağlantısı olmaksızın çalışan saf Python testleri.
"""

import unittest
from datetime import date
from model import User, ModelValidationError, UserNotFoundError, parse_date_value
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


class InMemoryUserModelTestCase(unittest.TestCase):
    """model.py içindeki User sınıfının birim testleri."""

    def test_user_initialization_and_to_dict(self):
        user = User(
            id=1,
            name="Ahmet Baha",
            birth_date="2001-04-12",
            city="Ankara",
            school="Hacettepe Üniversitesi"
        )
        self.assertEqual(user.birth_date, date(2001, 4, 12))
        data = user.to_dict()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Ahmet Baha")
        self.assertEqual(data["isim"], "Ahmet Baha")
        self.assertEqual(data["birth_date"], "2001-04-12")
        self.assertEqual(data["dogum_tarihi"], "2001-04-12")
        self.assertEqual(data["city"], "Ankara")
        self.assertEqual(data["school"], "Hacettepe Üniversitesi")

    def test_user_from_dict_english_and_turkish(self):
        # İngilizce anahtarlarla
        u_en = User.from_dict({
            "id": 10,
            "name": "John Doe",
            "birth_date": "1995-05-20",
            "city": "London",
            "school": "Oxford"
        })
        self.assertEqual(u_en.id, 10)
        self.assertEqual(u_en.name, "John Doe")
        self.assertEqual(u_en.city, "London")

        # Türkçe anahtarlarla
        u_tr = User.from_dict({
            "isim": "Ali Veli",
            "dogum_tarihi": "1998-10-15",
            "sehir": "İzmir",
            "okul": "Ege Üniversitesi"
        }, user_id=11)
        self.assertEqual(u_tr.id, 11)
        self.assertEqual(u_tr.name, "Ali Veli")
        self.assertEqual(u_tr.school, "Ege Üniversitesi")

    def test_validation_errors(self):
        # Boş isim
        u_empty_name = User(name="", birth_date=date(2000, 1, 1), city="Ankara", school="ODTÜ")
        with self.assertRaises(ModelValidationError):
            u_empty_name.validate()

        # Eksik doğum tarihi
        u_no_date = User(name="Test", birth_date=None, city="Ankara", school="ODTÜ")
        with self.assertRaises(ModelValidationError):
            u_no_date.validate()

        # Geçersiz tarih formatı
        with self.assertRaises(ModelValidationError):
            parse_date_value("gecersiz-tarih")


class InMemoryUserCrudTestCase(unittest.TestCase):
    """user.py içindeki in-memory CRUD operasyonlarının testleri."""

    def setUp(self):
        clear_storage()

    def tearDown(self):
        clear_storage()

    def test_create_user(self):
        user = create_user(
            name="Zeynep Kaya",
            birth_date="2002-06-14",
            city="Bursa",
            school="Uludağ Üniversitesi"
        )
        self.assertIsNotNone(user.id)
        self.assertEqual(user.name, "Zeynep Kaya")
        self.assertEqual(count_users(), 1)

    def test_create_user_with_turkish_params(self):
        user = create_user(
            name="",
            birth_date="",
            city="",
            school="",
            isim="Mehmet Öz",
            dogum_tarihi="1997-03-22",
            sehir="Antalya",
            okul="Akdeniz Üniversitesi"
        )
        self.assertEqual(user.name, "Mehmet Öz")
        self.assertEqual(user.city, "Antalya")
        self.assertEqual(count_users(), 1)

    def test_get_user_by_id_success_and_not_found(self):
        u = create_user("Test Kullanıcı", "2000-01-01", "İstanbul", "Boğaziçi")
        fetched = get_user_by_id(u.id)
        self.assertEqual(fetched.name, "Test Kullanıcı")

        with self.assertRaises(UserNotFoundError):
            get_user_by_id(99999)

        self.assertIsNone(get_user(99999))

    def test_get_all_users_and_filter(self):
        create_user("Ali Yılmaz", "2001-01-01", "Ankara", "Hacettepe")
        create_user("Ayşe Demir", "2002-02-02", "İstanbul", "İTÜ")
        create_user("Can Yılmaz", "2003-03-03", "Ankara", "ODTÜ")

        self.assertEqual(count_users(), 3)
        all_u = get_all_users()
        self.assertEqual(len(all_u), 3)

        # Filtreleme
        ankara_users = filter_users(city="Ankara")
        self.assertEqual(len(ankara_users), 2)

        yilmaz_users = filter_users(name="Yılmaz")
        self.assertEqual(len(yilmaz_users), 2)

    def test_update_user_put(self):
        u = create_user("Eski İsim", "2000-01-01", "Eski Şehir", "Eski Okul")
        updated = update_user(u.id, "Yeni İsim", "1995-12-12", "Yeni Şehir", "Yeni Okul")

        self.assertEqual(updated.name, "Yeni İsim")
        self.assertEqual(updated.city, "Yeni Şehir")
        self.assertEqual(updated.birth_date, date(1995, 12, 12))

    def test_patch_user_partial(self):
        u = create_user("Sabit İsim", "2000-01-01", "Ankara", "Gazi Üniversitesi")
        patched = patch_user(u.id, city="İzmir")

        self.assertEqual(patched.city, "İzmir")
        self.assertEqual(patched.name, "Sabit İsim")  # Değişmedi
        self.assertEqual(patched.school, "Gazi Üniversitesi")  # Değişmedi

    def test_patch_user_no_fields_error(self):
        u = create_user("Test", "2000-01-01", "Ankara", "Gazi")
        with self.assertRaises(ModelValidationError):
            patch_user(u.id)

    def test_delete_user(self):
        u1 = create_user("User 1", "2000-01-01", "A", "B")
        u2 = create_user("User 2", "2000-01-01", "C", "D")
        self.assertEqual(count_users(), 2)

        deleted = delete_user(u1.id)
        self.assertEqual(deleted.id, u1.id)
        self.assertEqual(count_users(), 1)

        with self.assertRaises(UserNotFoundError):
            delete_user(u1.id)

    def test_delete_all_users(self):
        seed_demo_users()
        self.assertGreater(count_users(), 0)
        deleted_count = delete_all_users()
        self.assertEqual(deleted_count, 3)
        self.assertEqual(count_users(), 0)


if __name__ == "__main__":
    unittest.main()
