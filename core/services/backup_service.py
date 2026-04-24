import shutil
import os
from datetime import datetime
from core.database import get_db_path


def create_backup():
    db_path = get_db_path()

    # 📁 Carpeta backups dentro de /data
    backup_dir = os.path.join(os.path.dirname(db_path), "backups")

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # 🕒 Nombre con fecha
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}.db")

    shutil.copy(db_path, backup_path)

    print(f"✅ Backup creado en: {backup_path}")

    # 🧹 LIMPIAR BACKUPS ANTIGUOS
    clean_old_backups(backup_dir)

    return backup_path


def clean_old_backups(backup_dir, max_backups=20):
    backups = sorted(
        [f for f in os.listdir(backup_dir) if f.startswith("backup_")],
        reverse=True
    )

    # borrar los que sobran
    for old_backup in backups[max_backups:]:
        os.remove(os.path.join(backup_dir, old_backup))

def get_db_file():
    return get_db_path()

