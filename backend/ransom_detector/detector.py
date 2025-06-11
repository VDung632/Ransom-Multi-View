
# Input Folder structure:
# - images/
#   - arsc_images/
#   - dex_images/
#   - jar_images/
#   - static_images/
#   - xml_images/

import tensorflow as tf
import os
import numpy as np
from tensorflow import keras
from PIL import Image
from tensorflow.keras import layers

## LayerScale
class LayerScale(layers.Layer):
    """Layer scale module.

    References:
      - https://arxiv.org/abs/2103.17239

    Args:
      init_values (float): Initial value for layer scale. Should be within
        [0, 1].
      projection_dim (int): Projection dimensionality.

    Returns:
      Tensor multiplied to the scale.
    """

    def __init__(self, init_values, projection_dim, **kwargs):
        super().__init__(**kwargs)
        self.init_values = init_values
        self.projection_dim = projection_dim

    def build(self, input_shape):
        self.gamma = tf.Variable(
            self.init_values * tf.ones((self.projection_dim,))
        )

    def call(self, x):
        return x * self.gamma

    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "init_values": self.init_values,
                "projection_dim": self.projection_dim,
            }
        )
        return config
    
class StochasticDepth(layers.Layer):
    """Stochastic Depth module.

    It performs batch-wise dropping rather than sample-wise. In libraries like
    `timm`, it's similar to `DropPath` layers that drops residual paths
    sample-wise.

    References:
      - https://github.com/rwightman/pytorch-image-models

    Args:
      drop_path_rate (float): Probability of dropping paths. Should be within
        [0, 1].

    Returns:
      Tensor either with the residual path dropped or kept.
    """

    def __init__(self, drop_path_rate, **kwargs):
        super().__init__(**kwargs)
        self.drop_path_rate = drop_path_rate

    def call(self, x, training=None):
        if training:
            keep_prob = 1 - self.drop_path_rate
            shape = (tf.shape(x)[0],) + (1,) * (len(tf.shape(x)) - 1)
            random_tensor = keep_prob + tf.random.uniform(shape, 0, 1)
            random_tensor = tf.floor(random_tensor)
            return (x / keep_prob) * random_tensor
        return x

    def get_config(self):
        config = super().get_config()
        config.update({"drop_path_rate": self.drop_path_rate})
        return config

def load_and_preprocess_images(input_dir, image_size=(64, 64)):
    """
    Đọc và tiền xử lý ảnh từ các thư mục con, tạo thành dữ liệu đầu vào 5 chiều.

    Args:
        input_dir (str): Đường dẫn đến thư mục chứa các thư mục type1, type2, ..., type5.
        image_size (tuple): Kích thước mong muốn của ảnh (height, width).

    Returns:
        numpy.ndarray: Mảng numpy chứa dữ liệu ảnh đầu vào có kích thước (num_samples, height, width, 5).
                       Trả về None nếu không tìm thấy đủ 5 ảnh tương ứng.
    """
    image_stacks = []
    file_types = ["xml", "arsc", "dex", "jar", "static"]
    image_names = set()
    
    for type_dir in os.listdir(input_dir):
        type_path = os.path.join(input_dir, type_dir)
        if os.path.isdir(type_path):
            for filename in os.listdir(type_path):
                if filename.endswith(".png"):
                    image_names.add(filename)

    for img_name in image_names:
        image_list = []
        for file_type in file_types:
            # Tạo đường dẫn đến ảnh trong từng thư mục type
            img_path = os.path.join(input_dir, f"{file_type}_images", img_name)
            
            if os.path.isfile(img_path):
                try:
                    img = Image.open(img_path).convert("L")  # Convert to grayscale
                    img = img.resize(image_size)  # Resize to (64, 64)
                    img_array = np.array(img) / 225.0  # Scale pixel values to 0-1
                    image_list.append(img_array)
                except Exception as e:
                    print(f"Lỗi khi đọc ảnh {img_path}: {e}")
                    return None, None
            else:
                print(f"Không tìm thấy ảnh {img_name} trong thư mục {file_type}_images.")
                return None, None

        if len(image_list) == 5:
            image_stack = np.stack(image_list, axis=-1)  # Stack along the last axis to create (64, 64, 5)
            image_stacks.append(image_stack)

    if not image_stacks:
        print("Không tìm thấy đủ bộ 5 ảnh tương ứng.")
        return None, None
    
    image_names = list(image_names)

    for i, img_name in enumerate(image_names):
        image_names[i] = os.path.splitext(img_name)[0]  # Remove file extension

    return np.array(image_stacks), image_names

def load_model_once(model_path='Trained_ConvNeXt.h5'):
    """
    Tải mô hình TensorFlow chỉ một lần.
    """
    try:
        tf.keras.backend.clear_session()
        model = keras.models.load_model(model_path, custom_objects={
            'LayerScale': LayerScale,
            'StochasticDepth': StochasticDepth,
        }, compile=False)
        print(f"Đã tải mô hình thành công từ: {model_path}")
        return model
    except Exception as e:
        print(f"Lỗi khi tải mô hình từ {model_path}: {e}")
        return None

def run_prediction(model, image_input_dir):
    """
    Hàm này được tạo ra để Flask có thể gọi và thực hiện dự đoán
    sử dụng mô hình đã được tải sẵn.

    Args:
        model: Mô hình TensorFlow đã được tải.
        image_input_dir (str): Đường dẫn đến thư mục chứa các thư mục con ảnh.

    Returns:
        list: Danh sách các dict chứa tên ảnh, điểm số, và nhãn dự đoán.
    """
    tf.keras.backend.clear_session()
    if model is None:
        print("Mô hình chưa được tải. Không thể thực hiện dự đoán.")
        return []

    input_data, image_names_only = load_and_preprocess_images(image_input_dir)
    results = []
    if input_data is not None and image_names_only is not None:
        predictions = model.predict(input_data).flatten()
        print("Kết quả dự đoán:")
        for score, name in zip(predictions, image_names_only):
            label = "Ransomware" if score > 0.5 else "Benign"
            results.append({
                "image_name": name,
                "score": float(f"{score:.4f}"),
                "label": label
            })
            print(f"Điểm số dự đoán cho {name}: {score:.4f} => {label}")
    else:
        print("Không có dữ liệu ảnh để dự đoán.")
    return results

def main():
    """
    Hàm chính để tải mô hình, xử lý ảnh và thực hiện dự đoán.
    """
    model_path = 'Tuned_ConvNeXt.h5'  # Thay thế bằng đường dẫn thực tế đến tệp mô hình của bạn
    input_directory = 'images'  

    try:
        model = keras.models.load_model((model_path), custom_objects={
            'LayerScale': LayerScale,
            'StochasticDepth': StochasticDepth,
        }, compile=False)
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        # print(model.summary())
        print(f"Đã tải mô hình thành công từ: {model_path}")
    except Exception as e:
        print(f"Lỗi khi tải mô hình: {e}")
        return

    input_data, image_name = load_and_preprocess_images(input_directory)
    if input_data is not None and image_name is not None:
        predictions = model.predict(input_data).flatten()
        print("Kết quả dự đoán:")
        for score, name in zip(predictions, image_name):
            label = ""
            if score > 0.5:
                label = "Ransomware"
            else:
                label = "Benign"
            print(f"Điểm số dự đoán cho {name}: {score:.4f} => {label}")

        

if __name__ == "__main__":
    main()