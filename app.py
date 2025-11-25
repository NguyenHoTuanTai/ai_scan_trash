import streamlit as st
import cv2
import numpy as np
import random
import pandas as pd
from ultralytics import YOLO

st.set_page_config(layout="wide")
st.title("Trash Detection")

#Load model
@st.cache_resource
def load_model():
    return YOLO("best.pt")

yolo = load_model()

# Helper functions
def generate_color(cls_number: int):
    random.seed(cls_number)
    return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

def draw_box_on_img(img, xyxy, label, conf, color):
    x1, y1, x2, y2 = map(int, xyxy)
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    cv2.putText(img, f"{label} {conf:.2f}", (x1, max(15, y1-7)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

def process_yolo(img, min_conf):
    results = yolo(img)
    detections = []
    for result in results:
        names = result.names
        for box in result.boxes:
            conf = float(box.conf[0])
            if conf < min_conf:
                continue
            cls = int(box.cls[0])
            class_name = names.get(cls, str(cls))
            xyxy = box.xyxy[0].cpu().numpy() if hasattr(box.xyxy[0], "cpu") else box.xyxy[0]
            xyxy = [float(v) for v in xyxy]
            color = generate_color(cls)
            draw_box_on_img(img, xyxy, class_name, conf, color)
            detections.append({
                "class": class_name, "confidence": conf,
                "x1": int(xyxy[0]), "y1": int(xyxy[1]),
                "x2": int(xyxy[2]), "y2": int(xyxy[3])
            })
    return img, detections


# Sidebar
st.sidebar.header("Cài đặt")
mode = st.sidebar.radio("Chọn chế độ:", ["📷 Webcam", "🖼 Upload ảnh"])
min_conf = st.sidebar.slider("Min confidence", 0.0, 1.0, 0.5, 0.01)

# Webcam mode
if mode == "📷 Webcam":
    st.subheader("Webcam")
    run = st.checkbox("Bật camera")
    frame_window = st.image([])

    cap = None
    prev_time = 0

    if run:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)

        if not cap.isOpened():
            st.error("Không thể mở webcam")

        stop_cam = st.button("Stop camera")

        while run:
            if stop_cam:
                break
            ret, frame = cap.read()
            if not ret:
                st.warning("Không lấy được frame")
                break

            frame, detections = process_yolo(frame.copy(), min_conf)

            #Tính FPS
            curr_time = cv2.getTickCount() / cv2.getTickFrequency()
            fps = 1 / (curr_time - prev_time) if prev_time else 0
            prev_time = curr_time
            cv2.putText(frame, f"FPS: {fps:.1f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            frame_window.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if cap:
            cap.release()
#Upload multi-image mode
elif mode == "Upload ảnh":
    st.subheader("Upload nhiều ảnh")
    uploaded_files = st.file_uploader("Chọn ảnh", type=["jpg","jpeg","png"], accept_multiple_files=True)
    all_detections = []

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            st.write(f"**Ảnh:** {uploaded_file.name}")
            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            img_out, detections = process_yolo(img.copy(), min_conf)

            st.subheader("Kết quả detect")
            st.image(cv2.cvtColor(img_out, cv2.COLOR_BGR2RGB))

            if detections:
                df = pd.DataFrame(detections)
                st.dataframe(df)
                #Lưu tất cả detections
                for det in detections:
                    det["image_name"] = uploaded_file.name
                all_detections.extend(detections)
            else:
                st.info("Không có vật nào vượt ngưỡng Min confidence.")

        #tải CSV tất cả detections
        if all_detections:
            df_all = pd.DataFrame(all_detections)
            csv = df_all.to_csv(index=False).encode("utf-8")
            st.download_button("Tải CSV toàn bộ detections", csv, file_name="detections_all.csv", mime="text/csv")
