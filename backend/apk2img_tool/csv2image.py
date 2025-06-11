import numpy as np
import pandas as pd
import os
from PIL import Image
import sys

def csv_to_images(csv_file, output_dir, num_info_cols=12, image_size=(64, 64)):
    """
    Converts data from a CSV file to grayscale images.

    Args:
        csv_file (str): Path to the input CSV file.
        output_dir (str): Directory to save the generated images.
        num_info_cols (int): Number of initial columns containing
            non-feature information (default: 12).
        image_size (tuple): Size of the output images (default: (64, 64)).
    """
    try:
        # Read data from the CSV file
        data = pd.read_csv(csv_file)

        for i, row in data.iterrows():
            # Get image name from the first column
            image_name = row[0]
            # Get the label from the last column
            label = row.iloc[-1]

            # Determine the target directory based on the label
            if label == 'ransom':
                target_dir = os.path.join(output_dir, "ransom", "static_images") # Changed folder name
            elif label == 'benign':
                target_dir = os.path.join(output_dir, "benign", "static_images") # Changed folder name
            else:
                # Skip the row if the label is not valid
                print(f"Skipping row {i}: Invalid label {label}")
                continue
            os.makedirs(target_dir, exist_ok=True)
            # Extract data for image creation from columns after the
            # basic info columns
            feature_data = row[num_info_cols + 1:-1].values

            # If data is not enough to create the image, pad with zeros
            required_length = image_size[0] * image_size[1]
            if len(feature_data) < required_length:
                feature_data = np.concatenate(
                    [feature_data, np.zeros(required_length - len(feature_data))])
            else:
                feature_data = feature_data[:required_length]

            # Reshape the data to the specified image size and cast to uint8
            img_array = feature_data.reshape(image_size).astype(np.uint8)

            # Create and save the image
            img = Image.fromarray(img_array, mode='L')
            img.save(os.path.join(target_dir, f"{image_name}.png"))
            print(f"Saved image {image_name}.png to {target_dir}")

        print(f"Images created and saved to {output_dir}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python csv_to_image.py <csv_file> <output_dir>"
                " [num_info_cols] [image_width] [image_height]")
        sys.exit(1)

    csv_file = sys.argv[1]
    output_dir = sys.argv[2]
    num_info_cols = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    image_width = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    image_height = int(sys.argv[5]) if len(sys.argv) > 5 else 64
    image_size = (image_width, image_height)

    csv_to_images(csv_file, output_dir, num_info_cols, image_size)