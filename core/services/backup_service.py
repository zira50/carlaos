import shutil
from datetime import datetime
from core.database import get_db_path


def create_backup():
    db_path = get_db_path()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.replace("database.db", f"backup_{timestamp}.db")

    shutil.copy(db_path, backup_path)

    return backup_path


def get_db_file():
    return get_db_path()

