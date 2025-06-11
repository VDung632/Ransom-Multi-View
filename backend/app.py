import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import hashlib
import shutil
import sys
import json

# Thêm đường dẫn tới thư mục backend để import main và detector
sys.path.append(os.path.join(os.path.dirname(__file__), 'apk2img_tool'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ransom_detector'))

from main import run_apk_processing
from detector import run_prediction, load_model_once
from static_analyzer import get_manifest_info

# Áp dụng Flask_cors để cho phép các yêu cầu từ frontend
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# Cấu hình thư mục tải lên và thư mục chứa ảnh đã trích xuất
UPLOAD_FOLDER = 'uploads'
EXTRACTED_IMAGES_FOLDER = 'apk_procession_output'
MODEL_PATH = os.path.join('ransom_detector', 'Tuned_ConvNeXt.h5') # Đảm bảo tệp này nằm trong thư mục backend
STATIC_FEATURES_CSV = os.path.join('Static_Features', "output.csv") # Tệp này dùng để lưu trữ các thông tin tĩnh khác nếu cần

# Tạo các thư mục nếu chúng chưa tồn tại
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_IMAGES_FOLDER, exist_ok=True)

global_loaded_model = None # Khởi tạo biến toàn cục
try:
    global_loaded_model = load_model_once(MODEL_PATH)
    if global_loaded_model is None:
        print("CẢNH BÁO: Không thể tải mô hình. Chức năng dự đoán sẽ không hoạt động.")
except Exception as e:
    print(f"Lỗi khi tải mô hình ngoài luồng yêu cầu: {e}")
    global_loaded_model = None


@app.route('/upload-apk', methods=['POST'])
def upload_apk():
    
    if global_loaded_model is None:
        return jsonify({"error": "Mô hình dự đoán chưa được tải. Vui lòng kiểm tra server."}), 503 

    if 'apk_file' not in request.files:
        return jsonify({"error": "Không có tệp APK nào được gửi"}), 400

    apk_file = request.files['apk_file']
    if apk_file.filename == '':
        return jsonify({"error": "Không có tệp APK nào được chọn"}), 400

    if apk_file:
        original_filename = secure_filename(apk_file.filename)
        
        # Lưu tệp tạm thời để tính SHA256
        temp_filepath = os.path.join(UPLOAD_FOLDER, original_filename)
        apk_file.save(temp_filepath)

        # Tính SHA256 của tệp
        sha256_hash = hashlib.sha256()
        with open(temp_filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        apk_sha256 = sha256_hash.hexdigest()

        # Đổi tên tệp thành SHA256.apk
        new_filename = f"{apk_sha256}.apk"
        final_filepath = os.path.join(UPLOAD_FOLDER, new_filename)
        os.rename(temp_filepath, final_filepath) # Đổi tên tệp tạm thời

        print(f"Đã nhận APK: {final_filepath}")

        # --- Bước 1: Trích xuất ảnh từ APK bằng main.py ---
        # output_base_dir cho main.py sẽ là thư mục EXTRACTED_IMAGES_FOLDER
        # main.py sẽ tạo các thư mục con bên trong nó (e.g., EXTRACTED_IMAGES_FOLDER/apk_name/images/...)
        
        apk_output_images_dir = os.path.join(EXTRACTED_IMAGES_FOLDER, apk_sha256)
        
        try:
            # Gọi hàm run_apk_processing từ main.py
            extracted_images_root_dir = run_apk_processing(final_filepath, EXTRACTED_IMAGES_FOLDER)
            # Đường dẫn thực tế đến các ảnh sẽ là extracted_images_root_dir/images
            actual_image_subfolder = os.path.join(extracted_images_root_dir, "images")
            
            if not os.path.exists(actual_image_subfolder) or not os.listdir(actual_image_subfolder):
                print(f"Lỗi: Không tìm thấy ảnh trích xuất trong {actual_image_subfolder}")
                return jsonify({"error": "Không thể trích xuất ảnh từ APK. Vui lòng kiểm tra lại tệp."}), 500

            # --- Bước 2: Phân loại ảnh bằng detector.py ---
            predictions = run_prediction(global_loaded_model, actual_image_subfolder)

            # Lấy danh sách các ảnh đã tạo để gửi về frontend + đọc dữ liệu từ output.csv và gửi lên frontend 
            image_urls = []
            if os.path.exists(actual_image_subfolder):
                for file_type_dir in os.listdir(actual_image_subfolder):
                    full_type_dir_path = os.path.join(actual_image_subfolder, file_type_dir)
                    if os.path.isdir(full_type_dir_path):
                        for img_file in os.listdir(full_type_dir_path):
                            if img_file.endswith(".png") and apk_sha256 in img_file:
                                # Tạo URL để frontend có thể truy cập ảnh
                                # Đường dẫn sẽ là /extracted_images/images/{file_type_dir}/{img_file}
                                relative_path = os.path.relpath(os.path.join(full_type_dir_path, img_file), EXTRACTED_IMAGES_FOLDER)
                                image_urls.append(f"/extracted_images/{relative_path.replace(os.sep, '/')}")
            
            # TODO: Cần trích xuất thông tin APK thực tế (tên gói, quyền, v.v.)
            # Hiện tại, chúng ta chỉ có thể trả về thông tin giả định hoặc cần tích hợp Androguard ở đây
            # Để đơn giản hóa, ở bước này chúng ta sẽ chỉ trả về tên tệp APK đã đổi tên.
            # Để trích xuất thông tin thực sự, bạn sẽ cần tích hợp logic tương tự như trong `apk_processor.py`
            # hoặc trực tiếp dùng thư viện androguard trong route này.
            static_feat = get_manifest_info(new_filename, STATIC_FEATURES_CSV)
            if static_feat is None:
                static_feat = {"error": "Không thể tìm thấy đặc trưng tĩnh từ APK này."}
            else:
                pass
            
                        

            # Ví dụ về thông tin trích xuất giả định
            extracted_info = {
                "package_name": "com.example.app",  # Thay thế bằng logic thực tế để lấy tên gói
                "file_sha256": apk_sha256,
                "original_filename": original_filename,
                "static_features": static_feat
            }

            extracted_info["package_name"] = static_feat["App name"]

            return jsonify({
                "message": "Xử lý APK thành công",
                "extracted_info": extracted_info,
                "predictions": predictions,
                "image_urls": image_urls
            }), 200

        except Exception as e:
            print(f"Lỗi trong quá trình xử lý: {e}")
            return jsonify({"error": f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"}), 500
        finally:
            # Dọn dẹp tệp APK đã tải lên sau khi xử lý
            if os.path.exists(final_filepath):
                os.remove(final_filepath)
            # Dọn dẹp các thư mục tạm thời của main.py trong EXTRACTED_IMAGES_FOLDER
            # main.py đã tự dọn dẹp một số, nhưng cần đảm bảo thư mục apk_sha256 cũng được dọn.
            # Ở đây, chúng ta giữ lại thư mục này để frontend có thể truy cập ảnh.
            # Logic cleanup chi tiết hơn có thể cần được thêm nếu muốn xóa ảnh sau khi frontend tải xong.

@app.route('/extracted_images/<path:filename>')
def serve_extracted_images(filename):
    """
    Phục vụ các tệp ảnh đã được trích xuất.
    """
    return send_from_directory(EXTRACTED_IMAGES_FOLDER, filename)


if __name__ == '__main__':
    # Cần đặt thư mục làm việc hiện tại thành thư mục chứa app.py
    # để đảm bảo các đường dẫn tương đối hoạt động chính xác (ví dụ: MODEL_PATH)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app.run(debug=True)