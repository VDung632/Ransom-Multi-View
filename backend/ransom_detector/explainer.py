import numpy as np
from lime import lime_image
from skimage.segmentation import mark_boundaries, felzenszwalb
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import os

# ---  Hàm dự đoán cho LIME ---
def predict_fn_for_5_channels(images, model):
    """ Hàm xử lý cho các mô hình chỉ cho ra xác suất 1 lớp"""
    predictions_1 = model.predict(images)
    predictions_0 = 1 - predictions_1
    predictions = np.concatenate((predictions_0, predictions_1), axis=1)
    return predictions

def create_channel_specific_predict_fn(keras_model, channel_index_to_explain, original_full_image):
    def channel_predict_fn(lime_input_images_1_channel):
        num_samples = lime_input_images_1_channel.shape[0]
        full_images_for_model = np.tile(np.expand_dims(original_full_image, axis=0), (num_samples, 1, 1, 1))
        for i in range(num_samples):
            full_images_for_model[i, :, :, channel_index_to_explain] = lime_input_images_1_channel[i, :, :, 0]
        predictions = predict_fn_for_5_channels(full_images_for_model, keras_model)
        return predictions
    return channel_predict_fn

def Image_explainer(original_image_5_channels, model, output_dir = "lime_explanations_per_channel_two_classes"):
    """
    Hàm giải thích kết quả cho mô hình trên từng kênh ảnh trong ảnh gốc
    Arg:
        original_image_5_channels: Ảnh xám 5 kênh từ khâu trích xuất
        model: mô hình CNN dùng để dự đoán
        output_dir: thư mục lưu ảnh đã qua giải thích
    """

    # ---  Khởi tạo LimeImageExplainer ---
    explainer = lime_image.LimeImageExplainer(
        feature_selection='auto',
        random_state=42,
    )

    # ---  Chạy LIME và Lưu ảnh ---

    initial_prediction = predict_fn_for_5_channels(np.expand_dims(original_image_5_channels, axis=0), model)
    print(f"Mô hình dự đoán ảnh gốc các xác suất cho từng lớp: {initial_prediction[0]}")

    # Ở đây, chúng ta muốn giải thích cho cả hai lớp 0 và 1.
    # target_classes_for_explanation = [0, 1]

    os.makedirs(output_dir, exist_ok=True)

    for i in range(original_image_5_channels.shape[2]): # Lặp qua 5 kênh (0 đến 4)
        print(f"\nĐang tạo giải thích LIME cho Kênh {i+1}...")
        
        image_for_lime_input = np.expand_dims(original_image_5_channels[:, :, i], axis=2) # (64, 64, 1)

        channel_predict_fn = create_channel_specific_predict_fn(model, i, original_image_5_channels)

        # Chạy LIME một lần để lấy giải thích cho TẤT CẢ các lớp (top_labels=số lượng lớp của bạn)
        # Nếu bạn chỉ có 2 lớp, top_labels=2
        explanation = explainer.explain_instance(
            image_for_lime_input,
            channel_predict_fn,
            top_labels=2, # <--- Quan trọng: để LIME tính toán trọng số cho cả 2 lớp
            hide_color=0,
            num_samples=1000,
            segmentation_fn=felzenszwalb, # Sử dụng felzenszwalb cho ảnh xám
        )
        
        # Lấy mask cho lớp 0 (ví dụ: tô màu xanh lá cây)
        temp0, mask0 = explanation.get_image_and_mask(
            0, # Lớp 0
            positive_only=True, # Chỉ lấy đóng góp tích cực
            num_features=10,
            hide_rest=False # Rất quan trọng: KHÔNG ẨN CÁC PHẦN CÒN LẠI để chúng ta có thể vẽ lên chúng
        )

        # Lấy mask cho lớp 1 (ví dụ: tô màu đỏ)
        temp1, mask1 = explanation.get_image_and_mask(
            1, # Lớp 1
            positive_only=True, # Chỉ lấy đóng góp tích cực
            num_features=10,
            hide_rest=False # Rất quan trọng: KHÔNG ẨN CÁC PHẦN CÒN LẠI
        )

        # Khởi tạo một ảnh RGB trống để vẽ lên (hoặc dùng ảnh gốc nếu bạn muốn)
        # Original image is (64, 64, 5). We are explaining a single channel (64, 64).
        # Let's create an RGB image from the original channel to draw on.
        # Scale original image channel to [0, 1] if not already.
        display_image_channel = original_image_5_channels[:, :, i]
        # Ensure it's 3 channels for coloring
        display_image_rgb = np.stack([display_image_channel, display_image_channel, display_image_channel], axis=-1)

        # Chuẩn hóa để đảm bảo giá trị màu nằm trong khoảng [0, 1] cho hiển thị
        display_image_rgb = (display_image_rgb - display_image_rgb.min()) / (display_image_rgb.max() - display_image_rgb.min())

        # Tạo một bản sao ảnh để vẽ các mask lên
        explanation_image = np.copy(display_image_rgb)

        # Tô màu cho lớp 0 (xanh lá cây)
        explanation_image[mask0 == True] = explanation_image[mask0 == True] * 0.5 + np.array([0, 1, 0]) * 0.5
        # Hoặc chỉ đơn giản gán màu: explanation_image[mask0 == True] = [1, 0, 0]

        # Tô màu cho lớp 1 (đỏ)
        explanation_image[mask1 == True] = explanation_image[mask1 == True] * 0.5 + np.array([1, 0, 0]) * 0.5
        # Hoặc chỉ đơn giản gán màu: explanation_image[mask1 == True] = [0, 1, 0]

        # Xử lý các vùng trùng lặp: nếu một vùng ảnh hưởng đến cả 2 lớp, màu sẽ là sự pha trộn.
        # Ví dụ: nếu trùng lặp, tô màu vàng (đỏ + xanh lá)
        # Trùng lặp sẽ được xử lý sau cùng để tránh bị tô đè bởi các màu khác
        overlapping_mask = np.logical_and(mask0, mask1)
        explanation_image[overlapping_mask] = explanation_image[overlapping_mask] * 0.5 + np.array([1, 1, 0]) * 0.5


        plt.figure(figsize=(6, 6))
        # mark_boundaries có thể hữu ích để thêm đường viền cho các superpixel
        # Tuy nhiên, nếu bạn đã tự tô màu, mark_boundaries có thể không cần thiết.
        # Nếu bạn vẫn muốn đường viền, bạn có thể truyền ảnh gốc 1 kênh và một mask kết hợp.
        # For now, let's just display the colored image.
        plt.imshow(explanation_image)
        
        # plt.title(f"LIME Explanation - Channel {i+1} (Class 0: {initial_prediction[0][0]:.2f} (Green), Class 1: {initial_prediction[0][1]:.2f}) (Red)")
        plt.axis('off')
        
        file_name = os.path.join(output_dir, f"lime_explanation_channel_{i+1}_two_classes.png")
        plt.savefig(file_name, bbox_inches='tight', pad_inches=0.1)
        plt.close()

        print(f"Đã lưu giải thích cho Kênh {i+1} tại: {file_name}")

    print("\nĐã hoàn tất việc tạo và lưu các ảnh giải thích LIME cho từng kênh và hai lớp.")



if __name__ == "__main__":
    # Ví dụ
    # ---  Giả lập dữ liệu và mô hình Keras ---
    original_image_5_channels = np.random.rand(64, 64, 5).astype(np.float32)

    def build_simple_cnn_model(input_shape=(64, 64, 5), num_classes=1): # Bây giờ mô hình có 2 lớp đầu ra
        model = keras.Sequential([
            keras.Input(shape=input_shape),
            layers.Conv2D(16, kernel_size=(3, 3), activation="relu", padding="same"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Flatten(),
            layers.Dense(num_classes, activation="sigmoid") # Vẫn dùng sigmoid cho 2 lớp độc lập
        ])
        return model

    model = build_simple_cnn_model(num_classes=1) # Ví dụ 2 lớp đầu ra
    # Giả lập khởi tạo trọng số
    _ = model.predict(np.expand_dims(original_image_5_channels, axis=0))

    Image_explainer(original_image_5_channels, model)