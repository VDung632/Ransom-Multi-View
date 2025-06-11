import argparse
import os
import pandas as pd
import numpy as np
from PIL import Image
import math

from static_analyzer import create_unique_lists, create_vector
from apk_processor import extract_apk_info, dex2jar, cleanup_dir
from image_converter import convert_file_to_image, convert_jar_to_image
from utils import create_directories, cleanup_directories, cleanup_files
import androguard
import androguard.util

androguard.util.set_log("CRITICAL")

def process_apk(input_dir, output_dir, file_types,
                auto_create_unique=False, auto_feature_selected=False,
                auto_use_default_unique_list=False,
                auto_use_default_feature=False,
                all_in_one=False):
    """Processes APK files in the input directory."""
    apk_filenames = []
    output_img_types = ""
    static_out_dir = "" # output.csv save path

    

    if all_in_one:
        output_img_types = os.path.join(output_dir, "images")
        create_directories([output_img_types])
    

    for root, dirs, files in os.walk(input_dir):
        for apk_file in files:
            if apk_file.endswith(".apk"):
                apk_path = os.path.join(root, apk_file)
                apk_name = os.path.splitext(apk_file)[0]
                # Directory store extracted APK files
                dest_dir = os.path.join(output_dir, "APK",
                                        os.path.relpath(root, input_dir), apk_name)
                create_directories([dest_dir])

                manifest_path = extract_apk_info(apk_path, dest_dir, static_out_dir)

                if all_in_one:
                    output_img = output_img_types
                elif 'benign' in apk_path.lower():
                    output_img = os.path.join(output_dir, 'benign')
                elif 'ransom' in apk_path.lower():
                    output_img = os.path.join(output_dir, 'ransomware')

                if "jar" in file_types:
                    jar_path = create_jar_from_apk(apk_path, output_dir, apk_name)
                    
                    if jar_path:
                        output_img_dir = os.path.join(output_img,
                                                        "jar_images")
                        create_directories([output_img_dir])
                        convert_jar_to_image(jar_path, output_img_dir)

                if manifest_path:
                    process_files(dest_dir, output_img, apk_name, file_types,
                                    auto_create_unique, auto_feature_selected,
                                    auto_use_default_unique_list,
                                    auto_use_default_feature)
                cleanup_dir(dest_dir)
                apk_filenames.append(apk_path)

    if 'txt' in file_types:
        unique_lists = create_unique_lists(static_out_dir)
        static_analysis = pd.read_csv(os.path.join(static_out_dir, "Static_Features", "output.csv"))
        # Create images from unique lists and output.csv (no feature selection)
        for filename in apk_filenames:
            apk_vector = create_vector(static_analysis, unique_lists, filename)
            # TODO: add feature selection and write a seperate function
            # no feature selection, directly create images
            # remove the first 13 element and the last element in the list
            image_vector = apk_vector[13:-1]
            # Create 2D images from the vector
            # image_size = (64, 64)
            length = len(image_vector)
            side = math.ceil(math.sqrt(length))
            padding = side * side - length
            image_vector += [0] * padding
            # Convert to numpy array and reshape
            img_arr = np.array(image_vector).reshape(side, side).astype(np.uint8)
            img = Image.fromarray(img_arr, mode='L').resize((64, 64))
            # Save the image
            if all_in_one:
                output_img = output_img_types
            elif image_vector[-1] == 0:
                output_img = os.path.join(output_dir, 'benign')
            elif image_vector[-1] == 1:
                output_img = os.path.join(output_dir, 'ransomware')

            output_img_dir = os.path.join(output_img,
                                            "static_images")
            create_directories([output_img_dir])
            filename_without_ext = os.path.splitext(os.path.basename(filename))[0]
            img.save(os.path.join(output_img_dir, filename_without_ext + ".png"))
            

def process_files(apk_dir, output_dir, apk_name, file_types,
                    auto_create_unique=False, auto_feature_selected=False,
                    auto_use_default_unique_list=False,
                    auto_use_default_feature=False):
    """Processes specified file types within an APK directory."""

    output_files_dir = os.path.join(output_dir, "filesave")
    create_directories([output_files_dir])

    for file_type in file_types:
        if file_type in ["dex", "xml", "arsc"]:
            convert_apk_file_to_image(apk_dir, output_dir, file_type)


def create_jar_from_apk(apk_dir, output_dir, apk_name):
    """Converts APK to JAR and returns the JAR path."""
    jar_name = f"{apk_name}.jar"
    jar_output_dir = os.path.join(output_dir, "output_directory",
                                    os.path.dirname(apk_dir).split(os.sep)[-2])
    create_directories([jar_output_dir])
    return dex2jar(apk_dir, jar_output_dir, jar_name)

def convert_apk_file_to_image(apk_dir, output_dir, file_type):
    """Converts specified files within the APK to images."""
    target_file = {
        "dex": "classes.dex",
        "xml": "AndroidManifest.xml",
        "arsc": "resources.arsc"
    }.get(file_type)
    if target_file:
        output_img_dir = os.path.join(output_dir,
                                        f"{file_type}_images")  # Changed folder name
        create_directories([output_img_dir])
        convert_file_to_image(os.path.join(apk_dir, target_file), output_img_dir)

def run_apk_processing(input_apk_path, output_base_dir, file_types=["xml", "arsc", "dex", "jar", "txt"]):
    """
    Hàm này được tạo ra để Flask có thể gọi và xử lý một APK cụ thể,
    đồng thời trả về đường dẫn thư mục chứa ảnh.
    """
    
    apk_filename_with_ext = os.path.basename(input_apk_path)
    apk_name_without_ext = os.path.splitext(apk_filename_with_ext)[0]

    # Tạo thư mục tạm thời cho APK đã giải nén và ảnh trích xuất
    temp_apk_extract_dir = os.path.join(output_base_dir, "temp_apk_extract", apk_name_without_ext)
    temp_image_output_dir = os.path.join(output_base_dir, "extracted_images", apk_name_without_ext)
    
    create_directories([temp_apk_extract_dir, temp_image_output_dir])

    # Giả định process_apk có thể xử lý một tệp APK đơn lẻ
    # Chúng ta cần mô phỏng cấu trúc thư mục mà process_apk mong đợi
    # Để đơn giản, chúng ta sẽ sao chép APK vào một thư mục input giả định
    # và sau đó gọi process_apk với thư mục đó.
    
    # Tạo một thư mục input tạm thời chứa duy nhất APK này
    single_apk_input_dir = os.path.join(output_base_dir, "single_apk_input", apk_name_without_ext)
    create_directories([single_apk_input_dir])
    
    # Sao chép APK vào thư mục input tạm thời
    import shutil
    shutil.copy(input_apk_path, single_apk_input_dir)

    print(f"Bắt đầu xử lý APK: {input_apk_path}")
    process_apk(single_apk_input_dir, temp_image_output_dir, file_types, all_in_one=True)
    print(f"Hoàn thành xử lý APK: {input_apk_path}")
    
    # Dọn dẹp thư mục input tạm thời
    cleanup_directories([single_apk_input_dir, temp_apk_extract_dir])
    cleanup(temp_image_output_dir)  
    
    # Trả về đường dẫn đến thư mục chứa ảnh đã trích xuất
    return temp_image_output_dir

def main():
    parser = argparse.ArgumentParser(
        description="APKs to Images Converting Tool")
    parser.add_argument("-i", "--input", required=True,
                        help="Input folder where you store APKs")
    parser.add_argument("-o", "--output", required=True,
                        help="Output folder to store output images")
    parser.add_argument("-t", "--type", nargs='+', required=True,
                        help="Type of file to process (AndroidManifest.xml, "
                                "resources.arsc, classes.dex, .jar, .txt for "
                                "xml static analysis)")
    parser.add_argument("-y", "--yes", action='count', default=2,
                        help="(txt mode only) First -y will automatically "
                                "create unique list without prompting, second "
                                "-y will automatically use feature selected")
    parser.add_argument("-n", "--no", action='count', default=0,
                        help="(txt mode only) First -y will use the default "
                                "unique list, second -n will stop using feature "
                                "selected")
    parser.add_argument("--no-split", action='store_true', default=False,
                        help="Store all images types in one folder")
    args = parser.parse_args()

    if args.yes > 2 or args.no > 2 or (
            args.yes > 0 and args.no > 1) or (args.yes > 1 and args.no > 0):
        parser.print_help()
        return

    file_types = args.type
    if file_types == ["all"]:
        file_types = ["xml", "arsc", "dex", "jar", "txt"]
    input_dir = args.input
    output_dir = args.output
    process_txt_files = any(ft in file_types for ft in ["txt", "all"])
    auto_create_unique = args.yes >= 1 and process_txt_files
    auto_feature_selected = args.yes >= 2 and process_txt_files
    auto_use_default_unique_list = args.no >= 1 and process_txt_files
    auto_use_default_feature = args.no >= 2 and process_txt_files

    all_in_one = args.no_split

    create_directories([output_dir, "errors"]) # Ensure main output dir exists
    process_apk(input_dir, output_dir, file_types, auto_create_unique,
                auto_feature_selected, auto_use_default_unique_list,
                auto_use_default_feature, all_in_one)
    # if process_txt_files:
    #     # Unique list creation and feature selection logic moved here
    #     process_text_files(input_dir, output_dir, auto_create_unique,
    #                         auto_feature_selected, auto_use_default_unique_list,
    #                         auto_use_default_feature)
    cleanup(output_dir)

def cleanup(output_dir):
    """Cleans up temporary directories and files."""

    dirs_to_remove = [
        os.path.join(output_dir, "output_directory"),
        "Unique_Lists", "errors",
        os.path.join(output_dir, "benign", "filesave"),
        os.path.join(output_dir, "ransomware", "filesave"),
        os.path.join(output_dir, "images", "filesave"),
        os.path.join(output_dir, "APK")
    ]
    files_to_remove = [
        os.path.join(output_dir, "Static_Binary_Features.csv"),
        os.path.join(output_dir, "Selected_Features.csv")
    ]
    cleanup_directories(dirs_to_remove)
    cleanup_files(files_to_remove)

if __name__ == "__main__":
    main()