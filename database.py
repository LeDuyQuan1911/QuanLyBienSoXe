import sqlite3

# Tạo cơ sở dữ liệu và bảng
def create_database():
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()

    # Tạo bảng vehicle_info nếu chưa tồn tại
    cursor.execute('''CREATE TABLE IF NOT EXISTS vehicle_info (
                        plate TEXT PRIMARY KEY,
                        name TEXT,
                        age INTEGER,
                        phone TEXT,
                        address TEXT,
                        entry_exit_count INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'sent',
                        entry_time TEXT,
                        exit_time TEXT
                    )''')
    conn.commit()
    conn.close()

create_database()

# Lưu thông tin biển số xe vào cơ sở dữ liệu
def save_license_plate(plate, name, age, phone, address):
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()

    # Kiểm tra xem biển số đã có trong cơ sở dữ liệu chưa
    cursor.execute("SELECT * FROM vehicle_info WHERE plate=?", (plate,))
    data = cursor.fetchone()

    if data:
        # Nếu đã có, cập nhật số lần ra vào và trạng thái
        cursor.execute("UPDATE vehicle_info SET entry_exit_count = entry_exit_count + 1 WHERE plate=?", (plate,))
    else:
        # Nếu chưa có, thêm mới
        cursor.execute('''INSERT INTO vehicle_info (plate, name, age, phone, address, entry_exit_count, status)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''', (plate, name, age, phone, address, 1, 'sent'))
    
    conn.commit()
    conn.close()

# Kiểm tra biển số xe có tồn tại trong cơ sở dữ liệu không
def check_license_plate(plate):
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM vehicle_info WHERE plate=?", (plate,))
    data = cursor.fetchone()

    conn.close()

    return data is not None

# Xóa biển số xe khỏi cơ sở dữ liệu (sử dụng khi lấy xe)
def remove_license_plate(plate):
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM vehicle_info WHERE plate=?", (plate,))
    
    conn.commit()
    conn.close()

# Cập nhật trạng thái xe (gửi/đã lấy)
def update_vehicle_status(plate, status):
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE vehicle_info SET status=? WHERE plate=?", (status, plate))
    
    conn.commit()
    conn.close()

# Lấy thông tin xe từ biển số
def get_vehicle_info(plate):
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM vehicle_info WHERE plate=?", (plate,))
    data = cursor.fetchone()

    conn.close()

    return data

def get_vehicle_data():
    conn = sqlite3.connect('parking_system.db')
    cursor = conn.cursor()

    cursor.execute("SELECT plate, name, entry_exit_count, status FROM vehicle_info")
    data = cursor.fetchall()

    conn.close()
    return data