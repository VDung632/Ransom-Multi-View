import os
import math
from PIL import Image
import numpy as np

def bytes_to_image(data: bytes, output_path: str, width: int = 64, height: int = 64):
    """
    Converts bytes data to a grayscale image.

    Args:
        data (bytes): The byte data to convert.
        output_path (str): Path to save the generated image.
        width (int): Width of the output image (default: 64).
        height (int): Height of the output image (default: 64).
    """
    try:
        length = len(data)
        side = math.ceil(math.sqrt(length))
        padding = side * side - length
        data += b'\0' * padding  # Pad with null bytes

        _image = Image.frombytes(mode='L', data=data, size=(1, side**2))
        img_array = np.array(_image).reshape((side, side))
        img = Image.fromarray(img_array).resize((width, height))
        img.save(output_path)
    except SyntaxError as se:
        print(f"SyntaxError while converting bytes to image: {se}")
    except Exception as e:
        print(f"Error converting bytes to image: {e}")

def convert_file_to_image(file_path: str, output_dir: str, width: int = 64,
                            height: int = 64):
    """
    Converts a file's content to a grayscale image.

    Args:
        file_path (str): Path to the file to convert.
        output_dir (str): Directory to save the generated image.
        width (int): Width of the output image (default: 64).
        height (int): Height of the output image (default: 64).
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        output_path = os.path.join(output_dir,
                                    os.path.dirname(file_path).split(os.sep)[-1] + ".png")
        bytes_to_image(data, output_path, width, height)
    except Exception as e:
        print(f"Error converting file to image: {e}")

def convert_jar_to_image(jar_path: str, output_dir: str, width: int = 64,
                            height: int = 64):
    """
    Converts the contents of a JAR file to a grayscale image.

    Args:
        jar_path (str): Path to the JAR file.
        output_dir (str): Directory to save the generated image.
        width (int): Width of the output image (default: 64).
        height (int): Height of the output image (default: 64).
    """
    try:
        import zipfile
        data = b''
        with zipfile.ZipFile(jar_path, 'r') as jar:
            for item in jar.infolist():
                if item.filename.endswith('.class'):
                    data += jar.read(item)
        # Remove .jar extension from the filename
        jar_name = os.path.splitext(os.path.basename(jar_path))[0]
        output_path = os.path.join(output_dir,
                                    jar_name + ".png")
        bytes_to_image(data, output_path, width, height)
    except Exception as e:
        print(f"Error converting JAR to image: {e}")