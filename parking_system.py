import cv2
import torch
import function.helper as helper
import database  # Import module database
from datetime import datetime  # Import datetime for capturing the current date and time

# Hàm mở camera và hiển thị hình ảnh
def open_camera():
    vid = cv2.VideoCapture(0)
    if not vid.isOpened():
        print("Camera không khả dụng.")
        return None

    return vid

def detect_license_plate_from_image(img):
    if img is None:
        return "unknown"

    # Sử dụng mô hình YOLO để nhận diện biển số
    yolo_license_plate = torch.hub.load('yolov5', 'custom', path='model/LP_ocr.pt', force_reload=True, source='local')
    yolo_license_plate.conf = 0.60

    # Nhận diện biển số
    lp = helper.read_plate(yolo_license_plate, img)
    return lp

def capture_and_save(vid):
    ret, img = vid.read()
    if not ret:
        print("Không thể chụp ảnh.")
        return

    plate = detect_license_plate_from_image(img)
    if plate != "unknown":
        # Capture the current time when the vehicle is sent
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save the license plate to the database
        database.save_license_plate(plate, current_time)
        
        # Print a message with the license plate and time
        print(f"Xe đã được gửi với biển số: {plate} vào lúc {current_time}")
    else:
        print("Không nhận diện được biển số.")

def capture_and_retrieve(vid):
    ret, img = vid.read()
    if not ret:
        print("Không thể chụp ảnh.")
        return

    plate = detect_license_plate_from_image(img)
    if plate != "unknown":
        if database.check_license_plate(plate):
            database.remove_license_plate(plate)
            print(f"Lấy xe thành công với biển số: {plate}")
        else:
            print("Không tìm thấy biển số trong database.")
    else:
        print("Không nhận diện được biển số.")


