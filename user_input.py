import os
from tracker import names

def get_input_data():
    v_path, obj_class = None, None
    valid_obj_classes = list(names.values())

    while v_path is None:
        v_path = input("Введите путь к видео файлу:\n")

        if not (os.path.exists(v_path) and os.path.isfile(v_path)):
            v_path = None
            print("Путь к файлу некорректен!\n")

    while obj_class is None:
        obj_class = input("Введите название класса:\n")

        if obj_class not in valid_obj_classes:
            obj_class = None
            print("Этот класс не поддерживается!")

    return v_path, obj_class
