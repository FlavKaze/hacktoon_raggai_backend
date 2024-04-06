import lancedb


def _connect_db(uri="raggaidb"):
    db = lancedb.connect(f"database/{uri}")
    return db


def _create_table(table_name, uri, mode="overwrite"):
    db = _connect_db(uri)
    table = db.create_table(table_name, mode=mode)
    return table

def get_table(table_name, uri):
    db = _connect_db(uri)
    try:
        table = db.get_table(table_name)
    except:
        table = _create_table(table_name, uri)
    return table


def insert(table_name, uri, data, mode="append"):
    table = get_table(table_name, uri)
    table.insert(data, mode=mode)
    return


def search(table_name, uri, vector, limit=3):
    table = get_table(table_name, uri)
    result = table.search(vector).limit(limit).to_pandas()
    return result