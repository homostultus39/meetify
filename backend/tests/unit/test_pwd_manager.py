from api.auth.management.pwd_manager import PWDManager

class TestPWDManager:
    def test_hash_password_returns_different_hashes(self):
        password = "secres"
        hash1 = PWDManager.hash_password(password)
        hash2 = PWDManager.hash_password(password)
        assert hash1 != hash2

    def test_check_password_correct(self):
        password = "correct123"
        hashed = PWDManager.hash_password(password)
        assert PWDManager.check_password(password, hashed) is True

    def test_check_password_incorrect(self):
        password = "correct123"
        hashed = PWDManager.hash_password(password)
        assert PWDManager.check_password("wrong", hashed) is False

    def test_hash_password_unicode(self):
        password = "кириллица"
        hashed = PWDManager.hash_password(password)
        assert PWDManager.check_password(password, hashed) is True