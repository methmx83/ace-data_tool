import os
import re
import pandas as pd

def clean_base_name(base_name):
    """Clean the base name of a file by replacing spaces with underscores and removing special characters.
    
    Args:
        base_name (str): The base name of the file (without extension).
    
    Returns:
        str: The cleaned base name containing only letters, numbers, underscores, and hyphens.
    """
    # Replace spaces with underscores
    base_name = base_name.replace(' ', '_')
    # Remove any character that is not a letter, number, underscore, or hyphen
    base_name = re.sub(r'[^a-zA-Z0-9_-]', '', base_name)
    return base_name

def clean_filename(filename):
    """Generate a cleaned file name from the original file name.
    
    Args:
        filename (str): The original file name with extension.
    
    Returns:
        str: The cleaned file name with the original extension.
    """
    base_name, extension = os.path.splitext(filename)
    cleaned_base_name = clean_base_name(base_name)
    return cleaned_base_name + extension

def rename_files(directory):
    """Rename all .wav files in the directory and its subdirectories to remove spaces and special characters, 
    and update labels.csv in the main directory if present.
    
    Args:
        directory (str): The path to the main directory containing the .wav files.
    """
    # Check if labels.csv exists in the main directory and load it
    labels_csv = os.path.join(directory, "labels.csv")
    if os.path.exists(labels_csv):
        df = pd.read_csv(labels_csv)
    else:
        df = None
    
    # Dictionary to store mapping from old relative path to new relative path
    name_mapping = {}
    
    # Traverse the directory and all subdirectories
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".wav"):
                # Full path to the original file
                original_path = os.path.join(root, filename)
                # Relative path from the main directory
                rel_path = os.path.relpath(original_path, directory)
                # Generate the cleaned filename
                new_filename = clean_filename(filename)
                
                # Only rename if the cleaned name is different
                if new_filename != filename:
                    new_path = os.path.join(root, new_filename)
                    counter = 1
                    
                    # Handle name conflicts within the same directory
                    while os.path.exists(new_path):
                        base_name, extension = os.path.splitext(new_filename)
                        new_filename = f"{base_name}_{counter}{extension}"
                        new_path = os.path.join(root, new_filename)
                        counter += 1
                    
                    # Perform the rename
                    os.rename(original_path, new_path)
                    # Compute the new relative path
                    new_rel_path = os.path.join(os.path.dirname(rel_path), new_filename)
                    # Store the mapping
                    name_mapping[rel_path] = new_rel_path
                    print(f"Renamed {rel_path} to {new_rel_path}")
                else:
                    print(f"Filename {rel_path} is already clean.")
    
    # Update labels.csv if it exists
    if df is not None:
        df['filename'] = df['filename'].map(name_mapping).fillna(df['filename'])
        df.to_csv(labels_csv, index=False)
        print("Updated labels.csv with new file names.")

if __name__ == "__main__":
    # Directory containing the .wav files
    AUDIO_DIR = "files"
    rename_files(AUDIO_DIR)