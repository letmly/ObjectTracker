import cv2
import numpy as np
from matplotlib import pyplot as plt
from ultralytics import YOLO

from ultralytics.utils.plotting import Annotator, colors
from collections import defaultdict

track_history = defaultdict(lambda: [])
model = YOLO("yolov8n.pt")
names = model.model.names


def track_obj(video_path: str, obj_class: str):
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
            results = model.track(frame, persist=True, verbose=False)
            boxes = results[0].boxes.xyxy.cpu()

            if results[0].boxes.id is not None:
                # Extract prediction results
                clss = results[0].boxes.cls.cpu().tolist()
                track_ids = results[0].boxes.id.int().cpu().tolist()

                for box, cls, track_id in zip(boxes, clss, track_ids):
                    if names[int(cls)] == obj_class:
                        tracked_objects_ids.add(track_id)
                        xmin, ymin, xmax, ymax = map(int, box)
                        new_frame[ymin:ymax, xmin:xmax, 0:3] = frame[ymin:ymax, xmin:xmax, 0:3]

                        # Annotator Init
                        annotator = Annotator(new_frame, line_width=2)
                        annotator.box_label(box, color=colors(int(cls), True),
                                            label=f"{names[int(cls)]} ID: {track_id}")

            result.write(new_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break

    result.release()
    cap.release()
    cv2.destroyAllWindows()

    return v_name, len(tracked_objects_ids)
