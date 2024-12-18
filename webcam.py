# import cv2
# import torch
# import time
# import function.utils_rotate as utils_rotate
# import function.helper as helper

# # Load models
# yolo_LP_detect = torch.hub.load('yolov5', 'custom', path='model/LP_detector_nano_61.pt', force_reload=True, source='local')
# yolo_license_plate = torch.hub.load('yolov5', 'custom', path='model/LP_ocr_nano_62.pt', force_reload=True, source='local')
# yolo_license_plate.conf = 0.60

# prev_frame_time = 0
# new_frame_time = 0

# # Open video capture
# vid = cv2.VideoCapture(0)  # Use your camera index
# if not vid.isOpened():
#     print("Error: Camera not accessible.")
#     exit()

# while True:
#     ret, frame = vid.read()

#     # Check if frame is read correctly
#     if not ret:
#         print("Failed to grab frame")
#         break

#     # License plate detection
#     plates = yolo_LP_detect(frame, size=640)
#     list_plates = plates.pandas().xyxy[0].values.tolist()
#     list_read_plates = set()

#     for plate in list_plates:
#         flag = 0
#         x = int(plate[0])  # xmin
#         y = int(plate[1])  # ymin
#         w = int(plate[2] - plate[0])  # xmax - xmin
#         h = int(plate[3] - plate[1])  # ymax - ymin

#         # Prevent out-of-bounds cropping
#         x = max(0, x)
#         y = max(0, y)
#         w = min(frame.shape[1] - x, w)
#         h = min(frame.shape[0] - y, h)

#         crop_img = frame[y:y + h, x:x + w]
#         cv2.rectangle(frame, (x, y), (x + w, y + h), color=(0, 0, 225), thickness=2)

#         # Directly use crop_img, no need to save/load as a file
#         lp = ""
#         for cc in range(0, 2):
#             for ct in range(0, 2):
#                 lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
#                 if lp != "unknown":
#                     list_read_plates.add(lp)
#                     cv2.putText(frame, lp, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
#                     flag = 1
#                     break
#             if flag == 1:
#                 break

#     # FPS Calculation
#     new_frame_time = time.time()
#     fps = 1 / (new_frame_time - prev_frame_time)
#     prev_frame_time = new_frame_time
#     fps = int(fps)
#     fps = max(fps, 1)  # Prevent FPS from dropping below 1

#     cv2.putText(frame, f'FPS: {fps}', (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)

#     # Show frame with detected license plates
#     cv2.imshow('frame', frame)

#     # Exit loop on 'q' key press
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release the video capture object and close any OpenCV windows
# vid.release()
# cv2.destroyAllWindows()






import cv2
import torch
import time
import function.utils_rotate as utils_rotate
import function.helper as helper

# Hàm xác định vùng miền dựa trên biển số
def detect_region(plate):
    region_codes = {
        "1": "Lạng Sơn", 
        "2": "Cao Bằng", 
        "3": "Bắc Giang", 
        "4": "Bắc Kạn", 
        "5": "Bắc Ninh", 
        "6": "Bến Tre", 
        "7": "Bình Dương", 
        "8": "Bình Định", 
        "9": "Bình Phước", 
        "10": "Bình Thuận", 
        "11": "Cà Mau", 
        "12": "Cần Thơ", 
        "13": "Đắk Lắk", 
        "14": "Đắk Nông", 
        "15": "Điện Biên", 
        "16": "Đồng Nai", 
        "17": "Đồng Tháp", 
        "18": "Gia Lai", 
        "19": "Hà Giang", 
        "20": "Hà Nam", 
        "21": "Hà Tĩnh", 
        "22": "Hải Dương", 
        "23": "Hải Phòng", 
        "24": "Hậu Giang", 
        "25": "Hòa Bình", 
        "26": "Hồ Chí Minh", 
        "27": "Hưng Yên", 
        "28": "Khánh Hòa", 
        "29": "Hà Nội", 
        "30": "Hà Nội", 
        "31": "Hà Nội", 
        "32": "Hà Nội", 
        "33": "Hà Nội", 
        "34": "Hà Nội", 
        "35": "Hà Nội", 
        "36": "Hà Nội", 
        "37": "Hà Nội", 
        "38": "Hà Nội", 
        "39": "Hà Nội", 
        "40": "Hà Nam", 
        "41": "Hải Dương", 
        "42": "Hải Phòng", 
        "43": "Hưng Yên", 
        "44": "Hòa Bình", 
        "45": "Lai Châu", 
        "46": "Lào Cai", 
        "47": "Lâm Đồng", 
        "48": "Long An", 
        "49": "Nam Định", 
        "50": "Sài Gòn",  # Mã biển số từ 50 đến 59
        "51": "Sài Gòn",
        "52": "Sài Gòn",
        "53": "Sài Gòn",
        "54": "Sài Gòn",
        "55": "Sài Gòn",
        "56": "Sài Gòn",
        "57": "Sài Gòn",
        "58": "Sài Gòn",
        "59": "Sài Gòn",
        "60": "Đà Nẵng",
        "61": "Đắk Lắk",
        "62": "Điện Biên",
        "63": "Gia Lai",
        "64": "Hà Giang",
        "65": "Hậu Giang",
        "66": "Hồ Chí Minh",
        "67": "Hòa Bình",
        "68": "Khánh Hòa",
        "69": "Kiên Giang",
        "70": "Kon Tum",
        "71": "Lạng Sơn",
        "72": "Lào Cai",
        "73": "Lào Cai",
        "74": "Lâm Đồng",
        "75": "Long An",
        "76": "Nam Định",
        "77": "Ninh Bình",
        "78": "Ninh Thuận",
        "79": "Phú Thọ",
        "80": "Phú Yên",
        "81": "Quảng Bình",
        "82": "Quảng Ngãi",
        "83": "Quảng Ninh",
        "84": "Quảng Trị",
        "85": "Sóc Trăng",
        "86": "Sơn La",
        "87": "Tây Ninh",
        "88": "Thái Bình",
        "89": "Thái Nguyên",
        "90": "Thanh Hóa",
        "91": "Thừa Thiên Huế",
        "92": "Tiền Giang",
        "93": "Trà Vinh",
        "94": "Tuyên Quang",
        "95": "Vĩnh Long",
        "96": "Vĩnh Phúc",
        "97": "Yên Bái",
    }

    
    plate_code = plate.split('-')[0]  # Lấy mã vùng từ biển số
    for code, region in region_codes.items():
        if plate_code.startswith(code):
            return region
    return "Không xác định"

# Load models
yolo_LP_detect = torch.hub.load('yolov5', 'custom', path='model/LP_detector_nano_61.pt', force_reload=True, source='local')
yolo_license_plate = torch.hub.load('yolov5', 'custom', path='model/LP_ocr_nano_62.pt', force_reload=True, source='local')
yolo_license_plate.conf = 0.60

prev_frame_time = 0
new_frame_time = 0

# Open video capture
vid = cv2.VideoCapture(0)  # Use your camera index
if not vid.isOpened():
    print("Error: Camera not accessible.")
    exit()

while True:
    ret, frame = vid.read()

    if not ret:
        print("Failed to grab frame")
        break

    # License plate detection
    plates = yolo_LP_detect(frame, size=640)
    list_plates = plates.pandas().xyxy[0].values.tolist()
    list_read_plates = set()

    for plate in list_plates:
        flag = 0
        x = int(plate[0])  # xmin
        y = int(plate[1])  # ymin
        w = int(plate[2] - plate[0])  # xmax - xmin
        h = int(plate[3] - plate[1])  # ymax - ymin

        # Prevent out-of-bounds cropping
        x = max(0, x)
        y = max(0, y)
        w = min(frame.shape[1] - x, w)
        h = min(frame.shape[0] - y, h)

        crop_img = frame[y:y + h, x:x + w]
        cv2.rectangle(frame, (x, y), (x + w, y + h), color=(0, 0, 225), thickness=2)

        # Directly use crop_img, no need to save/load as a file
        lp = ""
        for cc in range(0, 2):
            for ct in range(0, 2):
                lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                if lp != "unknown":
                    list_read_plates.add(lp)
                    region = detect_region(lp)  # Xác định vùng miền
                    cv2.putText(frame, f'{lp} - {region}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                    flag = 1
                    break
            if flag == 1:
                break

    # FPS Calculation
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    fps = int(fps)
    fps = max(fps, 1)  # Prevent FPS from dropping below 1

    cv2.putText(frame, f'FPS: {fps}', (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)

    # Show frame with detected license plates
    cv2.imshow('frame', frame)

    # Exit loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close any OpenCV windows
vid.release()
cv2.destroyAllWindows()
