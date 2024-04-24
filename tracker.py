import cv2
import numpy as np
import torch
from ultralytics import YOLO

from ultralytics.utils.plotting import Annotator, colors


model = YOLO("yolov8n.pt")
names = model.model.names


def track_obj(video_path: str, obj_class: str):
    obj_class_ind = [k for k, v in names.items() if v == obj_class][0]

    if torch.cuda.is_available():
        print("Cuda доступен")
        device = torch.device('cuda')
        model.to(device)
    else:
        print("Cuda не доступен")

    tracked_objects_ids = set()

    v_name = "Tracked_" + video_path.split('\\')[-1][:-4] + ".avi"
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), "Ошибка чтения видео файла"

    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    result = cv2.VideoWriter(v_name,
                             cv2.VideoWriter_fourcc(*'mp4v'),
                             fps,
                             (w, h))

    black_fill = np.ones((h, w, 3), dtype=np.uint8)
    while cap.isOpened():
        success, frame = cap.read()
        if success:
            new_frame = black_fill.copy()
            results = model.track(frame, persist=True, verbose=False, classes=obj_class_ind)
            boxes = results[0].boxes.xyxy.cpu()

            if results[0].boxes.id is not None:
                track_ids = results[0].boxes.id.int().cpu().tolist()

                for box, track_id in zip(boxes, track_ids):
                    tracked_objects_ids.add(track_id)
                    # вставка поля с найденным объектом
                    xmin, ymin, xmax, ymax = map(int, box)
                    new_frame[ymin:ymax, xmin:xmax, 0:3] = frame[ymin:ymax, xmin:xmax, 0:3]

                for box, track_id in zip(boxes, track_ids):
                    # отрисовка метки объекта
                    annotator = Annotator(new_frame, line_width=2)
                    annotator.box_label(box, color=colors(int(obj_class_ind), True), label=f"{obj_class} ID: {track_id}")

            result.write(new_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break

    result.release()
    cap.release()
    cv2.destroyAllWindows()

    return v_name, len(tracked_objects_ids)
