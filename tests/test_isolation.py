import database


def test_tests_do_not_use_the_working_directory_database():
    assert database.DB_PATH != "metrics.db"
