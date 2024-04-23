from user_input import get_input_data
from tracker import track_obj


def process():
    video_path, obj_class = get_input_data()

    result = track_obj(video_path, obj_class)

    print(f"Результат обработки:\n{result[0]}\n")
    if not result[1]:
        print(f"Ни один {obj_class} не был найден :(")


if __name__ == "__main__":
    process()

