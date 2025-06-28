import os
from static_analyzer import extract_manifest_info
import subprocess
import shutil
try:
    from androguard.core.bytecodes.apk import APK
except ImportError:
    from androguard.core.apk import APK

def extract_apk_info(apk_path, dest_dir, static_out_dir=""):
    """
    Extracts AndroidManifest.xml and optionally classes.dex from an APK.

    Args:
        apk_path (str): Path to the APK file.
        dest_dir (str): Directory to extract files to.
        static_out_dir (str): Directory to extract static features to. default is current directory.
    
    Returns:
        str: Path to the extracted AndroidManifest.xml.
    """
    try:
        apk = APK(apk_path) 
        manifest_path = "AndroidManifest.xml"
        # Extract files from APK
        with open(os.path.join(dest_dir, "AndroidManifest.xml"), "wb") as f:
            f.write(apk.get_file(manifest_path))
        # TODO: Retrain model with all dex files bytescode in apk and write it to one file
        # serialize_dex(apk, dest_dir)
        # For now, extract only classes.dex
        with open(os.path.join(dest_dir, "classes.dex"), "wb") as f:
            f.write(apk.get_file("classes.dex"))
        with open(os.path.join(dest_dir, "resources.arsc"), "wb") as f:
            f.write(apk.get_file("resources.arsc"))

        # Extract manifest info
        # Call extract_manifest_info to extract information
        
        extract_manifest_info(apk, static_out_dir)  # Pass the APK object
        return os.path.join(dest_dir, "AndroidManifest.xml")
    except Exception as e:
        print(f"Error extracting APK info from {apk_path}: {e}")
        return None

def get_dex_bytes(apk):
    for f in apk.get_files():
        if f.endswith(".dex"):
            yield apk.get_file(f)

def serialize_dex(apk, output_dir):
    """
    Serializes DEX files from an APK to a specified directory.

    Args:
        apk (APK): The APK object.
        output_dir (str): Directory to save the serialized DEX files.
    """
    os.makedirs(output_dir, exist_ok=True)
    dex_bytes = bytes()
    for byte_stream in get_dex_bytes(apk):
        dex_bytes += byte_stream
    with open(os.path.join(output_dir, "classes.dex"), "wb") as f:
        f.write(dex_bytes)

def dex2jar(apk_path, output_dir, jar_name):
    """
    Converts a DEX file to a JAR file using dex2jar.

    Args:
        apk_path (str): Path to the APK file.
        output_dir (str): Directory to save the JAR file.
        jar_name (str): Name of the output JAR file.
    """

    dex2jar_dir = r"/opt/dex2jar" # path to dex2jar directory for docker
    error_dir = r"errors"

    try:
        # Check os platform
        dex2jar_path = "d2j-dex2jar.sh" # path to dex2jar script
        error_file = os.path.join(error_dir, f"{os.path.basename(apk_path)}.zip") # Exception file
        if os.name == 'nt':
            dex2jar_path = "d2j-dex2jar.bat"
            # execute the command using subprocess
            dex2jar_path = os.path.join(dex2jar_dir, dex2jar_path)
            command = ["cmd.exe", "/c", dex2jar_path, "-f", apk_path, "-o",
                        os.path.join(output_dir, jar_name), "-e", error_file]
            subprocess.run(command, check=True)
        elif os.name == 'posix':
            # local testing
            dex2jar_dir = os.environ["DEX2JAR_PATH"]
            dex2jar_path = "d2j-dex2jar.sh"
            dex2jar_path = os.path.join(dex2jar_dir, dex2jar_path)
            subprocess.run(
                ["sh", dex2jar_path, "-f", apk_path, "-o",
                    os.path.join(output_dir, jar_name)], check=True
            )
        return os.path.join(output_dir, jar_name)
    except subprocess.CalledProcessError as e:
        print(f"Error converting DEX to JAR: {e}")
        return None

def cleanup_dir(dir_path):
    """
    Removes a directory and its contents.

    Args:
        dir_path (str): Path to the directory to remove.
    """
    shutil.rmtree(dir_path, ignore_errors=True)


if __name__ == "__main__":
    # # Example usage
    # apk_path = "path/to/your.apk"
    # dest_dir = "output_directory"
    # extract_dex = True

    # # Create output directory if it doesn't exist
    # os.makedirs(dest_dir, exist_ok=True)

    # # Extract APK info
    # manifest_path = extract_apk_info(apk_path, dest_dir, extract_dex)
    # if manifest_path:
    #     print(f"Extracted AndroidManifest.xml to {manifest_path}")
    
    # # Convert DEX to JAR
    # dex_path = os.path.join(dest_dir, "classes.dex")
    # jar_name = "output.jar"
    # jar_output_dir = dest_dir
    # jar_path = dex2jar(dex_path, jar_output_dir, jar_name)
    # if jar_path:
    #     print(f"Converted DEX to JAR: {jar_path}")

    # # Cleanup
    # cleanup_dir(dest_dir)
    print("APK processing completed.")