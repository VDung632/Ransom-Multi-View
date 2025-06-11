# Static Analyzer for Android APKs
import os
import math
from androguard.core.apk import APK
from lxml import etree
import json
import csv
import pandas as pd
import itertools

import numpy as np
from PIL import Image

def convert_file_size(size_in_bytes, suffix='B'):
    """
    Converts file size from bytes to a human-readable format.

    Args:
        size_in_bytes (int): Size in bytes.

    Returns:
        str: Converted size in a human-readable format (with unit).
    """
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(size_in_bytes) < 1024.0:
            return f"{size_in_bytes:3.1f}{unit}{suffix}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f}Yi{suffix}"

# filename + no. icon + no. Audio + no. Videos + App_size + no. Activities + no. Meta + no. Service + no. Perm + no. Action + no. Provider + no. receiver + no. Category + Perm + Action + Serv + Cate
csv_header = ["App name", "Number of Icons", "Number of Audio", 
              "Number of Videos", "App size",
              "Number of Activities", "Number of Meta-Data", 
              "Number of Services", "Number of Permissions",
              "Number of Actions", "Number of Providers", "Number of Receivers", "Number of Categories",
              "Permissions", "Actions", "Services", "Categories", "FileName"]



def extract_manifest_info(apk_raw, output_dir):
    """
    Extracts information from AndroidManifest.xml using androguard
    and saves it to a csv file. csv file location is Static_Features/output.csv.
    the path is relative to output_dir.

    Args:
        apk_raw (APK): Already analyzed APK object.
        output_dir (str): Path to the output directory.
    """

    try:
        apk = apk_raw
        axml = apk.get_android_manifest_xml()
        output_file_path = os.path.join(output_dir, "Static_Features",
                                            "output.csv")
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        file_exists = os.path.isfile(output_file_path)

        Value = []
        
        # Package Info
        Value.append(apk.get_package())
        
        # Activities
        activities = apk.get_activities()

        # Services
        services = apk.get_services()

        # Providers
        providers = apk.get_providers()
        
        # Receivers
        receivers = apk.get_receivers()

        # Actions
        actions = []
        for elem in axml.iter():
            if elem.tag == 'action':
                action_str = etree.tostring(elem).decode()
                actions.append(action_str)

        # Categories
        categories = []
        for elem in axml.iter():
            if elem.tag == 'category':
                category_str = etree.tostring(elem).decode()
                categories.append(category_str)

        # Permissions (using extracted values)
        permissions = apk.get_permissions()

        # Meta-Data (Example - adapt as needed)
        meta_data = []
        for elem in axml.iter():
            if  elem.tag == 'meta-data':
                meta_str = etree.tostring(elem).decode()
                meta_data.append(meta_str)

        # Get all files in APK
        apk_files = apk.get_files()

        # Number of Icons (approximation - counts files in the APK directory)

        icon_count = len(
            [file for file in apk_files
                if file.lower().endswith(('.png'))])

        # Number of Pictures (JPGs)
        picture_count = len(
            [file for file in apk_files
                if file.lower().endswith(('.jpg'))])

        # Number of Audio Files (MP3s)
        audio_count = len(
            [file for file in apk_files
                if file.lower().endswith(('.mp3'))])

        # Number of Video Files (MP4s)
        video_count = len(
            [file for file in apk_files
                if file.lower().endswith(('.mp4'))])

        # Size of the App
        size_output = os.path.getsize(apk.get_filename())
        size_output = convert_file_size(size_output)

        # Append numeric to the Value list
        Value.append(icon_count + picture_count)
        Value.append(audio_count)
        Value.append(video_count)
        Value.append(size_output)
        Value.append(len(activities))
        Value.append(len(meta_data))
        Value.append(len(services))
        Value.append(len(permissions))
        Value.append(len(actions))
        Value.append(len(providers))
        Value.append(len(receivers))
        Value.append(len(categories))

        # Append permissions, actions, services, and categories to the Value list
        Value.append(json.dumps(permissions))
        Value.append(json.dumps(actions))
        Value.append(json.dumps(services))
        Value.append(json.dumps(categories))

        # Append the filename to the Value list
        file_name = os.path.basename(apk.get_filename())
        Value.append(file_name)

        with open(output_file_path, 'a+', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            if not file_exists or os.path.getsize(output_file_path) == 0:
                writer.writerow(csv_header)
            # Only write values if there is no filename in the csv file
            if file_name not in outfile.read():
                writer.writerow(Value)
        print("Static Features Done!!!")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e

def create_unique_lists(input_dir):
    """
    Creates unique lists from the input dir (the one that has output.csv).

    Args:
        input_dir (str): Path to the directory containing output.csv.

    Returns:
        tuple: Unique lists of permissions, actions, services, and categories.
    """
    csv_file = os.path.join(input_dir, "Static_Features", "output.csv")
    
    # Read specific columns in csv file
    list_of_feat = pd.read_csv(csv_file, usecols=["Permissions", "Actions", "Services", "Categories"])
    # Load all features
    list_of_perm = list_of_feat["Permissions"].tolist()
    list_of_actions = list_of_feat["Actions"].tolist()
    list_of_services = list_of_feat["Services"].tolist()
    list_of_categories = list_of_feat["Categories"].tolist()
    
    # Convert JSON strings to lists
    list_of_perm = [json.loads(i) for i in list_of_perm]
    list_of_actions = [json.loads(i) for i in list_of_actions]
    list_of_services = [json.loads(i) for i in list_of_services]
    list_of_categories = [json.loads(i) for i in list_of_categories]
    
    # Flatten the lists
    list_of_perm = list(itertools.chain.from_iterable(list_of_perm))
    list_of_actions = list(itertools.chain.from_iterable(list_of_actions))
    list_of_services = list(itertools.chain.from_iterable(list_of_services))
    list_of_categories = list(itertools.chain.from_iterable(list_of_categories))

    # Create unique lists
    unique_perm = set(list_of_perm)
    unique_actions = set(list_of_actions)
    unique_services = set(list_of_services)
    unique_categories = set(list_of_categories)

    return unique_perm, unique_actions, unique_services, unique_categories
    
def create_vector(static_analysis, unique_lists, filename):
    """
    Creates a vector for an APK file based on the unique lists and output.csv.
    Args:
        static_analysis (pd.DataFrame): DataFrame containing output.csv content.
        unique_lists (tuple): Unique lists of permissions, actions, services, and categories.
        filename (str): absolute path to the APK file.
    Returns:
        a vector of features for the APK (not including the label).
    """
    unique_perm, unique_actions, unique_services, unique_categories = unique_lists
    
    apk_name = os.path.basename(filename)
    # Read specific row that contain APK name in csv file
    # Only one row should be returned
    list_of_feat = static_analysis[static_analysis["FileName"] == apk_name]
    
    # Load all features
    list_of_perm = list_of_feat["Permissions"].tolist()
    list_of_actions = list_of_feat["Actions"].tolist()
    list_of_services = list_of_feat["Services"].tolist()
    list_of_categories = list_of_feat["Categories"].tolist()
    
    # Convert JSON strings to lists
    list_of_perm = [json.loads(i) for i in list_of_perm]
    list_of_actions = [json.loads(i) for i in list_of_actions]
    list_of_services = [json.loads(i) for i in list_of_services]
    list_of_categories = [json.loads(i) for i in list_of_categories]
    
    # Flatten the lists
    flat_perm = set(itertools.chain.from_iterable(list_of_perm))
    flat_actions = set(itertools.chain.from_iterable(list_of_actions))
    flat_services = set(itertools.chain.from_iterable(list_of_services))
    flat_categories = set(itertools.chain.from_iterable(list_of_categories))

    # Create a vector of features
    vector = []

    # Add APK name and other numeric features
    for header in csv_header[:-5]:
        value = list_of_feat[header]
        # Flatten the value if it's a list
        if isinstance(value, list):
            value = set(itertools.chain.from_iterable(value))
        vector.append(list_of_feat[header])
    
    # Check if each feature is present and append 1 or 0 to the vector
    perm_binary = [1 if perm in unique_perm else 0 for perm in flat_perm]
    action_binary = [1 if action in unique_actions else 0 for action in flat_actions]
    service_binary = [1 if service in unique_services else 0 for service in flat_services]
    category_binary = [1 if category in unique_categories else 0 for category in flat_categories]

    # Extend the vector with binary values
    vector.extend(perm_binary)
    vector.extend(action_binary)
    vector.extend(service_binary)
    vector.extend(category_binary)

    # Append the label (benign or ransomware)
    ## Simple checker for benign or ransomware based on file path
    if "benign" in filename:
        vector.append(0)
    else:
        vector.append(1)

    return vector

def get_manifest_info(apk_name, output_csv):
    """
    Lấy thông tin từ file APK trong output.csv

    Args:
        apk_name (str): Tên file APK cần tìm thông tin.
        output_csv (str): Đường dẫn đến file CSV chứa thông tin APK.
    Returns:
        dict: Thông tin của APK dưới dạng từ điển, hoặc None nếu không tìm thấy.
    """
    if not os.path.exists(output_csv):
        print(f"CSV file {output_csv} does not exist.")
        return None
    
    try:
        df = pd.read_csv(output_csv)

        df['FileBaseName'] = df['FileName'].apply(os.path.basename)
        apk_basename = os.path.basename(apk_name)

        df_filtered = df[df['FileBaseName'] == apk_basename]
        if not df_filtered.empty:
            # Lấy bản phân tích mới nhất
            feature = df_filtered.iloc[-1].to_dict()

            del feature['FileBaseName']  # Remove the base name key

            return {k:v if pd.notna(v) else None for k, v in feature.items()}
        else:
            print(f"Không tìm thấy thông tin cho APK: {apk_name}")
            return None
    except Exception as e:
        print(f"Đã xảy ra lỗi khi đọc file CSV: {e}")
        return None

if __name__ == "__main__":
    # example usage
    img_output_dir = r"D:\KLTN_code\image_dataset" # Change this to your output directory
    output_path = r"D:\KLTN_code\image_dataset\Static_Features\output.csv" # Change this to your output csv file
    unique_lists = create_unique_lists(img_output_dir)
    output_read = pd.read_csv(output_path)
    for filename in output_read["FileName"]:
        # Check filename
        try:
            parts = filename.split(".")
            if len(parts) == 2:

                apk_vector = create_vector(output_read, unique_lists, filename)
                image_vector = apk_vector[13:-1]
                length = len(image_vector)
                side = math.ceil(math.sqrt(length))
                padding = side * side - length
                image_vector += [0] * padding
                # Convert to numpy array and reshape
                img_arr = np.array(image_vector).reshape(side, side).astype(np.uint8)
                img = Image.fromarray(img_arr, mode='L').resize((64, 64))
                # Save the image
                if apk_vector[-1] == 0:
                    output_img = os.path.join(img_output_dir, 'benign')
                elif apk_vector[-1] == 1:
                    output_img = os.path.join(img_output_dir, 'ransomware')

                output_img_dir = os.path.join(output_img,
                                                "static_images")

                filename_without_ext = os.path.splitext(os.path.basename(filename))[0]
                img.save(os.path.join(output_img_dir, filename_without_ext + ".png"))
                print(f"Done one vector: {filename_without_ext}")
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            continue
    print("Done all vectors")