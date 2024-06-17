import sqlite3
import json
import yaml
import os
import db
from fetch import CACHE_DB_LOCATION

ADMIN_YAML_LOCATION = "data/admin.yml"
EXPORT_FILE_LOCATION = "data/export.json"

DEFAULT_DATA = {
    'visitor_can_add': False,
    'editor_can_remove': True,
    'default_address': ""
}


def init_yaml():
    # Check if the file exists
    if not os.path.exists(ADMIN_YAML_LOCATION):
        # If the file doesn't exist, create it with default values
        with open(ADMIN_YAML_LOCATION, 'w') as file:
            yaml.safe_dump(DEFAULT_DATA, file)

    with open(ADMIN_YAML_LOCATION, 'r') as file:
        data = yaml.safe_load(file)

    data.setdefault('visitor_can_add', DEFAULT_DATA['visitor_can_add'])
    data.setdefault('editor_can_remove', DEFAULT_DATA['editor_can_remove'])
    data.setdefault('default_address', DEFAULT_DATA['default_address'])

    with open(ADMIN_YAML_LOCATION, 'w') as file:
        yaml.safe_dump(data, file)


def update_yaml(visitor_can_add=None, editor_can_remove=None, default_address=None):
    init_yaml()
    with open(ADMIN_YAML_LOCATION, 'r') as file:
        data = yaml.safe_load(file)

    data['visitor_can_add'] = visitor_can_add if visitor_can_add is not None else data['visitor_can_add']
    data['editor_can_remove'] = editor_can_remove if editor_can_remove is not None else data['editor_can_remove']
    data['default_address'] = default_address if default_address is not None else data['default_address']

    with open(ADMIN_YAML_LOCATION, 'w') as file:
        yaml.safe_dump(data, file)


def get_settings():
    init_yaml()
    with open(ADMIN_YAML_LOCATION, 'r') as file:
        data = yaml.safe_load(file)

    class Yaml_Settings():
        visitor_can_add = data['visitor_can_add']
        editor_can_remove = data['editor_can_remove']
        default_address = data['default_address']
    return Yaml_Settings()


def export_to_json():
    rows = db.read_books()
    rows_json = json.dumps(rows, indent=4)
    with open(EXPORT_FILE_LOCATION, 'w') as file:
        file.writelines(rows_json)
    return EXPORT_FILE_LOCATION


def import_from_json(file_storage):
    file_content = file_storage.read().decode('utf-8')
    data = json.loads(file_content)
    for i in data:
        db.create_book(i[1], i[2], i[3], i[4], i[5], i[6],
                       i[7], i[8], i[9], i[10], i[11])


def clear_cache_db():
    db.delete_db(CACHE_DB_LOCATION)


def delete_main_db():
    db.delete_db()
    db.init_db()



# if __name__ == '__main__':
    # pass
    # update_yaml(visitor_can_add=True, editor_can_remove=True, default_address="Hackmann House")
    # export_to_json()
    # clear_cache()
    # delete_main_db()
    # init_yaml()
