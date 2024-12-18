import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.simpledialog import askstring
import cv2
from PIL import Image, ImageTk
from datetime import datetime
import subprocess
from tkinter import ttk  # Add this import to use ttk
import torch

from function import helper

# Giả sử bạn đã có hàm detect_license_plate_from_image để nhận diện biển số xe
# Ví dụ hàm đơn giản:
def detect_license_plate_from_image(img):
    if img is None:
        return "unknown"

    # Sử dụng mô hình YOLO để nhận diện biển số
    yolo_license_plate = torch.hub.load('yolov5', 'custom', path='model/LP_ocr.pt', force_reload=True, source='local')
    yolo_license_plate.conf = 0.60

    # Nhận diện biển số
    lp = helper.read_plate(yolo_license_plate, img)
    return lp

class CameraApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        # Open the camera
        self.vid = cv2.VideoCapture(0)
        if not self.vid.isOpened():
            messagebox.showerror("Error", "Cannot open the camera.")
            self.window.destroy()  # Close the window if the camera cannot be opened
            return
        
        # Create the main frame
        main_frame = tk.Frame(self.window)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Create the image frame for displaying vehicle images
        self.image_frame = tk.Frame(main_frame)
        self.image_frame.pack(side=tk.RIGHT, padx=10, pady=10)  # Move the image frame to the right

        # Label to display the image
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack()

        # Create the canvas for video display
        self.canvas = tk.Canvas(main_frame, width=800, height=300)
        self.canvas.pack(side=tk.TOP, expand=True, fill=tk.BOTH, anchor="center", pady=5)

        # Button frame for controls
        button_frame = tk.Frame(self.window, bg='#4CAF50')
        button_frame.pack(pady=10)

        # "Send Vehicle" button
        self.send_button = tk.Button(button_frame, text="Send Vehicle", width=20, height=2, command=self.capture_and_send, bg='#ffffff', fg='#4CAF50', font=('Arial', 12, 'bold'))
        self.send_button.pack(side=tk.LEFT, padx=5)

        # "Retrieve Vehicle" button
        self.retrieve_button = tk.Button(button_frame, text="Retrieve Vehicle", width=20, height=2, command=self.capture_and_retrieve, bg='#ffffff', fg='#4CAF50', font=('Arial', 12, 'bold'))
        self.retrieve_button.pack(side=tk.LEFT, padx=5)

        # "Enter Vehicle Info" button
        self.input_info_button = tk.Button(button_frame, text="Enter Vehicle Info", width=20, height=2, command=self.input_vehicle_info, bg='#ffffff', fg='#4CAF50', font=('Arial', 12, 'bold'))
        self.input_info_button.pack(side=tk.LEFT, padx=5)

        # "View Vehicle Data" button
        self.view_data_button = tk.Button(button_frame, text="View Vehicle Data", width=20, height=2, command=self.open_data_view, bg='#ffffff', fg='#4CAF50', font=('Arial', 12, 'bold'))
        self.view_data_button.pack(side=tk.LEFT, padx=5)

        # "View Vehicle Images" button
        self.view_images_button = tk.Button(button_frame, text="View Vehicle Images", width=20, height=2, command=self.view_vehicle_images, bg='#ffffff', fg='#4CAF50', font=('Arial', 12, 'bold'))
        self.view_images_button.pack(side=tk.LEFT, padx=5)

        # Create a button to toggle fullscreen
        self.fullscreen_button = tk.Button(button_frame, text="Toggle Fullscreen", width=20, height=2, command=self.toggle_fullscreen, bg='#ffffff', fg='#4CAF50', font=('Arial', 12, 'bold'))
        self.fullscreen_button.pack(side=tk.LEFT, padx=5)

        # Update the video feed
        self.update()
        self.window.mainloop()



    def toggle_fullscreen(event=None):
        # Toggle fullscreen mode
        is_fullscreen = root.attributes('-fullscreen')
        root.attributes('-fullscreen', not is_fullscreen)

    def end_fullscreen(event=None):
        # Exit fullscreen mode
        root.attributes('-fullscreen', False)

    # root.bind("<Escape>", end_fullscreen)



    def update(self):
        # Đọc một khung hình từ camera
        ret, frame = self.vid.read()
        if ret:
            # Chuyển đổi ảnh từ OpenCV (BGR) sang RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((1600, 400))  # Điều chỉnh kích thước nếu cần
            img_tk = ImageTk.PhotoImage(img)

            # Hiển thị ảnh vào Canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            self.canvas.image = img_tk  # Lưu giữ tham chiếu đến ảnh

        # Tiếp tục cập nhật hình ảnh mỗi 10ms
        self.window.after(10, self.update)

    def set_left_image(self, image_path):
        """Cập nhật ảnh bên trái màn hình với ảnh mới chụp."""
        img = Image.open(image_path)
        img = img.resize((800, 450))  # Điều chỉnh kích thước ảnh nếu cần
        img_tk = ImageTk.PhotoImage(img)
        self.image_label.config(image=img_tk)
        self.image_label.image = img_tk


    def open_data_view(self):
        # Cửa sổ hiển thị dữ liệu xe
        data_window = tk.Toplevel(self.window)
        data_window.title("Xem Dữ Liệu Xe")

        # Tạo Frame để sắp xếp các nút ngang hàng
        button_frame = tk.Frame(data_window, bg='#4CAF50')  # Nền xanh cho frame chứa nút
        button_frame.pack(pady=10)

        # Tạo ô nhập tìm kiếm và nút tìm kiếm
        search_label = tk.Label(data_window, text="Tìm kiếm theo Biển Số Xe hoặc Tên Chủ Xe:")
        search_label.pack(pady=5)
        
        search_entry = tk.Entry(data_window, width=30)
        search_entry.pack(pady=5)

        def search():
            search_term = search_entry.get().strip()
            if search_term:
                self.search_vehicle_in_db(search_term, tree)  # Tìm kiếm trong cơ sở dữ liệu
            else:
                messagebox.showwarning("Lỗi", "Vui lòng nhập biển số xe hoặc tên chủ xe.")

        search_button = tk.Button(button_frame, text="Tìm Kiếm", command=search, bg='#ffffff', fg='#4CAF50', font=('Arial', 12, 'bold'), width=15)
        search_button.pack(side=tk.LEFT, padx=5)

        # Nút Reload để tải lại dữ liệu
        def reload():
            self.display_all_vehicles(tree)  # Tải lại toàn bộ dữ liệu vào bảng Treeview

        reload_button = tk.Button(button_frame, text="Tải Lại Dữ Liệu", command=reload, bg='#ffffff', fg='#4CAF50', font=('Arial', 12, 'bold'), width=15)
        reload_button.pack(side=tk.LEFT, padx=5)

        # Nút Lọc "Gửi Xe"
        def filter_sent():
            self.filter_by_status('sent', tree)

        filter_sent_button = tk.Button(button_frame, text="Lọc Xe Gửi", command=filter_sent, bg='#ffffff', fg='#4CAF50', font=('Arial', 12, 'bold'), width=15)
        filter_sent_button.pack(side=tk.LEFT, padx=5)

        # Nút Lọc "Lấy Xe"
        def filter_retrieved():
            self.filter_by_status('retrieved', tree)

        filter_retrieved_button = tk.Button(button_frame, text="Lọc Xe Lấy", command=filter_retrieved, bg='#ffffff', fg='#4CAF50', font=('Arial', 12, 'bold'), width=15)
        filter_retrieved_button.pack(side=tk.LEFT, padx=5)

        # Tạo Treeview để hiển thị dữ liệu xe
        tree = ttk.Treeview(data_window, columns=("plate", "name", "entry_exit_count", "status"), show="headings")
        tree.pack(padx=10, pady=10)

        # Định nghĩa các cột trong Treeview
        tree.heading("plate", text="Biển Số Xe")
        tree.heading("name", text="Tên Chủ Xe")
        tree.heading("entry_exit_count", text="Số Lần Ra Vào")
        tree.heading("status", text="Trạng Thái")

        # Hiển thị tất cả dữ liệu xe ngay khi cửa sổ được mở
        self.display_all_vehicles(tree)

    def filter_by_status(self, status, tree):
        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()

        # Truy vấn các xe theo trạng thái "Gửi" hoặc "Lấy"
        query = "SELECT plate, name, entry_exit_count, status FROM vehicle_info WHERE status=?"
        cursor.execute(query, (status,))
        vehicles = cursor.fetchall()

        conn.close()

        # Xóa tất cả các dòng cũ trong Treeview
        for item in tree.get_children():
            tree.delete(item)

        # Thêm dữ liệu vào Treeview
        for vehicle in vehicles:
            tree.insert("", tk.END, values=vehicle)
        
    def display_all_vehicles(self, tree):
        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()
        
        # Truy vấn tất cả dữ liệu xe
        cursor.execute("SELECT plate, name, entry_exit_count, status FROM vehicle_info")
        vehicles = cursor.fetchall()
        
        conn.close()
        
        # Xóa tất cả các dòng cũ trong Treeview
        for item in tree.get_children():
            tree.delete(item)

        # Thêm dữ liệu vào Treeview
        for vehicle in vehicles:
            tree.insert("", tk.END, values=vehicle)

    def search_vehicle_in_db(self, search_term, status_filter, tree):
        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()

        # Truy vấn tìm kiếm theo biển số, tên chủ xe, và trạng thái
        query = """
            SELECT plate, name, entry_exit_count, status
            FROM vehicle_info
            WHERE (plate LIKE ? OR name LIKE ?)
        """
        
        if status_filter != 'all':
            query += " AND status = ?"

        cursor.execute(query, ('%' + search_term + '%', '%' + search_term + '%', status_filter if status_filter != 'all' else None))
        results = cursor.fetchall()

        conn.close()

        # Xóa tất cả các dòng cũ trong Treeview
        for item in tree.get_children():
            tree.delete(item)

        # Hiển thị kết quả tìm kiếm
        if results:
            for row in results:
                tree.insert("", tk.END, values=row)
        else:
            messagebox.showinfo("Thông Báo", "Không tìm thấy xe nào.")

    def load_vehicle_data(self, tree):
            # Kết nối cơ sở dữ liệu và lấy dữ liệu
            conn = sqlite3.connect('parking_system.db')
            cursor = conn.cursor()

            cursor.execute("SELECT plate, name, entry_exit_count, status FROM vehicle_info")
            data = cursor.fetchall()

            conn.close()

            # Xóa dữ liệu cũ trong bảng
            for row in tree.get_children():
                tree.delete(row)

            # Thêm dữ liệu vào bảng
            for row in data:
                tree.insert("", "end", values=row)

    def update(self):
        # Đọc frame từ camera
        ret, frame = self.vid.read()
        if ret:
            # Chuyển đổi từ BGR sang RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Chuyển frame thành ảnh PIL
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(img)

            # Cập nhật ảnh vào Canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            self.canvas.image = img_tk  # Lưu ảnh để không bị xóa

        # Tiếp tục cập nhật video
        self.window.after(10, self.update)

    def retrieve_vehicle_info(self, plate):
        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()

        # Chuẩn hóa biển số
        plate = plate.strip().replace(" ", "")  # Loại bỏ khoảng trắng thừa và dấu cách

        cursor.execute("SELECT * FROM vehicle_info WHERE plate=?", (plate,))
        data = cursor.fetchone()

        conn.close()

        if data:
            return {
                "plate": data[0],
                "name": data[1],
                "age": data[2],
                "phone": data[3],
                "address": data[4],
                "entry_exit_count": data[5],
                "status": data[6]
            }
        else:
            return None
        
    def save_vehicle_info(self, plate, name, age, phone, address):
        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()

        # Chuẩn hóa biển số (loại bỏ khoảng trắng và ký tự đặc biệt nếu có)
        plate = plate.strip().replace(" ", "")  # Loại bỏ khoảng trắng thừa và dấu cách

        # Kiểm tra nếu biển số xe đã tồn tại trong cơ sở dữ liệu
        cursor.execute("SELECT * FROM vehicle_info WHERE plate=?", (plate,))
        data = cursor.fetchone()

        if data:
            # Nếu đã tồn tại, chỉ cần cập nhật số lần xe ra vào và trạng thái
            cursor.execute("UPDATE vehicle_info SET entry_exit_count = entry_exit_count + 1, status = 'sent' WHERE plate=?", (plate,))
        else:
            # Nếu chưa có, thêm mới thông tin vào cơ sở dữ liệu
            cursor.execute("INSERT INTO vehicle_info (plate, name, age, phone, address, entry_exit_count, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (plate, name, age, phone, address, 1, 'sent'))

        conn.commit()
        conn.close()

    def capture_and_send(self):
        ret, frame = self.vid.read()
        if ret:
            plate = detect_license_plate_from_image(frame)  # Hàm nhận diện biển số từ hình ảnh
            if plate != "unknown":
                plate = plate.strip().replace(" ", "")  # Chuẩn hóa biển số

                # Kiểm tra xem xe đã có trong cơ sở dữ liệu chưa
                vehicle_info = self.retrieve_vehicle_info(plate)
                if vehicle_info:
                    # Kiểm tra trạng thái xe, nếu xe đã gửi thì không cho phép gửi lại và không chụp hình
                    if vehicle_info['status'] == 'sent':
                        messagebox.showinfo("Thông báo", f"Xe biển số {plate} đã được gửi trước đó. Không thể gửi lại.")
                        return  # Không chụp hình nữa, dừng lại ở đây

                    # Nếu xe chưa gửi, tiếp tục chụp hình
                    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_name = f"{plate}_{current_time}.jpg"
                    image_folder = "saved_images"

                    # Tạo thư mục nếu chưa tồn tại
                    if not os.path.exists(image_folder):
                        os.makedirs(image_folder)

                    # Lưu ảnh vào thư mục
                    image_path = os.path.join(image_folder, image_name)
                    cv2.imwrite(image_path, frame)

                    self.set_left_image(image_path)

                    # Cập nhật thông tin xe
                    self.save_vehicle_info(
                        plate,
                        vehicle_info['name'],
                        vehicle_info['age'],
                        vehicle_info['phone'],
                        vehicle_info['address']
                    )

                    # Cập nhật trạng thái xe thành "sent"
                    self.update_vehicle_status(plate, status="sent")

                    messagebox.showinfo("Gửi Xe", f"Xe đã được gửi với biển số: {plate}\nẢnh đã được lưu: {image_name}")
                else:
                    # Yêu cầu nhập thông tin xe nếu chưa có trong cơ sở dữ liệu
                    messagebox.showinfo("Thông báo", f"Biển số xe {plate} chưa có thông tin trong hệ thống. Hãy nhập thông tin.")
            else:
                messagebox.showerror("Error", "Không nhận diện được biển số.")
        else:
            messagebox.showerror("Error", "Không thể chụp ảnh.")



    def view_saved_images(self):
        image_folder = "saved_images"
        if os.path.exists(image_folder):
            file_path = filedialog.askopenfilename(initialdir=image_folder, title="Chọn ảnh để xem")
            if file_path:
                # Hiển thị ảnh đã chọn
                image = cv2.imread(file_path)
                cv2.imshow("Saved Image", image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
        else:
            messagebox.showinfo("Thông báo", "Không có hình ảnh nào được lưu.")

    def capture_and_retrieve(self):
        # Code lấy xe
        ret, frame = self.vid.read()
        if ret:
            plate = detect_license_plate_from_image(frame)  # Hàm nhận diện biển số từ hình ảnh
            if plate != "unknown":
                plate = plate.strip().replace(" ", "")  # Chuẩn hóa biển số

                vehicle_info = self.retrieve_vehicle_info(plate)
                if vehicle_info:
                    # Kiểm tra trạng thái của xe
                    if vehicle_info['status'] == 'sent':
                        messagebox.showinfo("Thông tin xe", f"Xe biển số: {plate} đã được lấy.")
                        
                        # Lưu ảnh khi lấy xe (tương tự như khi gửi xe)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        image_filename = f"{plate}_{timestamp}.jpg"  # Tên file ảnh
                        image_path = os.path.join("saved_images", image_filename)
                        
                        # Lưu ảnh vào thư mục
                        cv2.imwrite(image_path, frame)
                        
                        # Cập nhật trạng thái xe thành "đã lấy"
                        self.update_vehicle_status(plate)

                        self.set_left_image(image_path)
                        
                        # Hiển thị thông báo ảnh đã được lưu
                        messagebox.showinfo("Thông báo", f"Ảnh của xe biển số {plate} đã được lưu.")
                    else:
                        messagebox.showinfo("Thông báo", "Xe đã được lấy trước đó.")
                else:
                    messagebox.showerror("Error", "Không tìm thấy biển số.")
            else:
                messagebox.showerror("Error", "Không nhận diện được biển số.")
        else:
            messagebox.showerror("Error", "Không thể chụp ảnh.")


        #
        #
        #
        #Kiểm tra ảnh xe
    def view_vehicle_images(self):
        """
        Mở thư mục chứa các ảnh đã lưu và hiển thị các ảnh trong thư mục với thời gian,
        có thể lọc theo biển số xe và hiển thị kết quả trong frame "Lọc Ảnh Xe Theo Biển Số".
        """
        import os
        from PIL import Image, ImageTk
        from datetime import datetime
        import tkinter as tk
        from tkinter import messagebox

        def filter_images_by_plate_number():
            plate_number_filter = plate_number_entry.get().strip()  # Lấy biển số từ ô nhập
            view_vehicle_images_filtered(plate_number_filter)  # Gọi hàm hiển thị với biển số đã nhập

        def view_vehicle_images_filtered(plate_number_filter=None):
            """
            Lọc và hiển thị các ảnh trong frame "Lọc Ảnh Xe Theo Biển Số",
            có thể lọc theo biển số xe.
            """
            if not os.path.exists(images_folder):
                messagebox.showerror("Lỗi", "Thư mục lưu ảnh không tồn tại.")
                return

            # Lấy danh sách ảnh trong thư mục
            images = [f for f in os.listdir(images_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

            if not images:
                messagebox.showinfo("Thông báo", "Không có ảnh nào được lưu.")
                return

            # Nếu có filter biển số, chỉ chọn những ảnh có chứa biển số này
            if plate_number_filter:
                images = [f for f in images if plate_number_filter in f]

            # Sắp xếp các ảnh theo thứ tự thời gian (tên file chứa thời gian)
            images.sort(key=lambda x: x.split('_')[1] + x.split('_')[2].split('.')[0])

            # Xóa các ảnh cũ trong frame trước khi hiển thị ảnh mới
            for widget in scroll_frame.winfo_children():
                widget.destroy()

            # Hiển thị từng ảnh trong frame cuộn kèm thời gian
            for img_file in images:
                img_path = os.path.join(images_folder, img_file)

                # Lấy thời gian từ tên file ảnh
                try:
                    parts = img_file.split('_')
                    date_str = parts[1]
                    time_str = parts[2].split('.')[0]

                    full_time_str = date_str + time_str
                    formatted_time = datetime.strptime(full_time_str, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, IndexError) as e:
                    print(f"Lỗi xử lý thời gian: {e}")
                    formatted_time = "Không rõ thời gian"

                # Load ảnh bằng PIL
                img = Image.open(img_path)
                img = img.resize((300, 200))  # Resize ảnh để vừa khung hiển thị
                img_tk = ImageTk.PhotoImage(img)

                # Hiển thị ảnh và thời gian
                img_frame = tk.Frame(scroll_frame, bg="white")
                img_frame.pack(pady=10, fill="x")

                label_image = tk.Label(img_frame, image=img_tk)
                label_image.image = img_tk  # Lưu tham chiếu để không bị xóa
                label_image.pack(side="left", padx=10)

                label_time = tk.Label(img_frame, text=f"Thời gian: {formatted_time}", font=("Arial", 12), bg="white")
                label_time.pack(side="left", padx=10)

            top.mainloop()

        # Đường dẫn đến thư mục lưu ảnh
        images_folder = "saved_images"

        # Tạo cửa sổ chính để hiển thị ảnh và lọc ảnh theo biển số
        top = tk.Toplevel()
        top.title("Lọc Ảnh Xe Theo Biển Số")
        top.configure(bg="#f0f0f0")  # Màu nền của cửa sổ

        # Tạo frame chứa label, ô nhập và nút "Lọc"
        filter_frame = tk.Frame(top, bg="#f0f0f0")
        filter_frame.pack(pady=10, padx=20, fill="x")

        # Label biển số và ô nhập nằm kế nhau
        label = tk.Label(filter_frame, text="Nhập biển số xe:", font=("Arial", 12), bg="#f0f0f0")
        label.pack(side="left", padx=10)

        plate_number_entry = tk.Entry(filter_frame, font=("Arial", 14), bg="#ffffff", relief="solid", bd=2)
        plate_number_entry.pack(side="left", padx=10, fill="x", expand=True)

        # Nút "Lọc"
        filter_button = tk.Button(filter_frame, text="Lọc", font=("Arial", 12), command=filter_images_by_plate_number, bg="#4CAF50", fg="white", relief="solid", bd=2)
        filter_button.pack(side="left", padx=10)

        # Tạo canvas và scrollbar để hiển thị ảnh
        canvas = tk.Canvas(top, width=600, height=400, bg="#f0f0f0")
        scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f0f0f0")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Đặt canvas và scrollbar vào cửa sổ
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Hiển thị tất cả ảnh khi mở lần đầu
        view_vehicle_images_filtered()








        
    def update_vehicle_status(self, plate):
        conn = sqlite3.connect('parking_system.db')
        cursor = conn.cursor()

        # Cập nhật trạng thái của xe thành "đã lấy"
        cursor.execute("UPDATE vehicle_info SET status = 'retrieved' WHERE plate=?", (plate,))
        conn.commit()
        conn.close()

    def input_vehicle_info(self):
    # Cửa sổ nhập thông tin xe
        info_window = tk.Toplevel(self.window)
        info_window.title("Nhập Thông Tin Xe")
        info_window.geometry("400x400")  # Kích thước cửa sổ

        # Tạo frame chứa các trường nhập
        frame = tk.Frame(info_window, padx=20, pady=20)
        frame.pack(padx=10, pady=10)

        # Tiêu đề cửa sổ
        title_label = tk.Label(info_window, text="Nhập Thông Tin Xe", font=("Arial", 16, "bold"), fg="#4CAF50")
        title_label.pack(pady=10)

        # Các trường nhập thông tin
        plate_label = tk.Label(frame, text="Biển Số Xe:", font=("Arial", 12), anchor='w')
        plate_label.grid(row=0, column=0, pady=5, sticky="w")
        plate_entry = tk.Entry(frame, width=30, font=("Arial", 12))
        plate_entry.grid(row=0, column=1, pady=5)

        name_label = tk.Label(frame, text="Tên Chủ Xe:", font=("Arial", 12), anchor='w')
        name_label.grid(row=1, column=0, pady=5, sticky="w")
        name_entry = tk.Entry(frame, width=30, font=("Arial", 12))
        name_entry.grid(row=1, column=1, pady=5)

        age_label = tk.Label(frame, text="Tuổi:", font=("Arial", 12), anchor='w')
        age_label.grid(row=2, column=0, pady=5, sticky="w")
        age_entry = tk.Entry(frame, width=30, font=("Arial", 12))
        age_entry.grid(row=2, column=1, pady=5)

        phone_label = tk.Label(frame, text="Số Điện Thoại:", font=("Arial", 12), anchor='w')
        phone_label.grid(row=3, column=0, pady=5, sticky="w")
        phone_entry = tk.Entry(frame, width=30, font=("Arial", 12))
        phone_entry.grid(row=3, column=1, pady=5)

        address_label = tk.Label(frame, text="Địa Chỉ:", font=("Arial", 12), anchor='w')
        address_label.grid(row=4, column=0, pady=5, sticky="w")
        address_entry = tk.Entry(frame, width=30, font=("Arial", 12))
        address_entry.grid(row=4, column=1, pady=5)


        def save_info():
            plate = plate_entry.get()
            name = name_entry.get()
            age = age_entry.get()
            phone = phone_entry.get()
            address = address_entry.get()

            if plate and name and age and phone and address:
                self.save_vehicle_info(plate, name, age, phone, address)
                messagebox.showinfo("Thông báo", "Thông tin xe đã được lưu.")
                info_window.destroy()
            else:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin.")

        save_button = tk.Button(info_window, text="Lưu Thông Tin", command=save_info, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=20)
        save_button.pack(pady=20)

# Tạo giao diện Tkinter chính
root = tk.Tk()
root.title("Quét Biển Số Xe")

# Đặt màu nền cho cửa sổ
root.configure(bg='#f0f0f0')

# Tạo khung chứa nút
frame = tk.Frame(root, bg='#4CAF50', bd=10)
frame.pack(pady=20)

def start_scanning():
    try:
        # Sử dụng subprocess để gọi script webcam.py
        subprocess.Popen(['python', 'webcam.py'])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start scanning: {e}")

# Tạo nút quét biển số
scan_button = tk.Button(frame, text="Quét Biển Số Xe", command=start_scanning, height=2, width=20, bg='#ffffff', fg='#4CAF50', font=('Arial', 14, 'bold'))
scan_button.pack()

# Hàm mở cửa sổ camera cho chức năng gửi xe/lấy xe
def open_parking_interface():
    CameraApp(root, "Gửi Xe / Lấy Xe")# Mở rộng cửa sổ toàn màn hình
    


# Tạo nút gửi xe/lấy xe
parking_button = tk.Button(frame, text="Gửi Xe / Lấy Xe", command=open_parking_interface, height=2, width=20, bg='#ffffff', fg='#4CAF50', font=('Arial', 14, 'bold'))
parking_button.pack(pady=10)



# Chạy giao diện
root.mainloop()
