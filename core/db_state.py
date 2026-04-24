db_changed = False

def mark_db_changed():
    global db_changed
    db_changed = True

def reset_db_changed():
    global db_changed
    db_changed = False

def has_db_changed():
    return db_changed