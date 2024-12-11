# import requests
# import csv
# import os
# from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage

# def download_image(url, save_path):
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             image_content = response.content
#             saved_path = default_storage.save(save_path, ContentFile(image_content))
#             return saved_path
#         else:
#             print(f"Failed to download image. Status code: {response.status_code}")
#             return None
#     except requests.RequestException as e:
#         print(f"Error occurred while downloading the image: {e}")
#         return None

# def download_images_from_csv(csv_file, dataset_name, save_directory, downloaded_log):
#     dataset_folder = os.path.join(save_directory, dataset_name)
#     os.makedirs(dataset_folder, exist_ok=True)

#     with open(downloaded_log, 'a+') as log_file:
#         log_file.seek(0)
#         downloaded_files = set(line.strip() for line in log_file)

#         try:
#             with open(csv_file, newline='', encoding='utf-8') as file:
#                 reader = csv.reader(file)
                
#                 for i, row in enumerate(reader):
#                     if row:
#                         image_url = row[0].strip()
#                         image_name = f"{dataset_name}_image_{i + 1}.jpg"  # Rename image with dataset name
#                         save_path = os.path.join(dataset_folder, image_name)

#                         if image_name not in downloaded_files:
#                             downloaded_image_path = download_image(image_url, save_path)
#                             if downloaded_image_path:
#                                 print(f"Image downloaded and saved at {downloaded_image_path}")
#                                 log_file.write(f"{image_name}\n")
#                             else:
#                                 print(f"Failed to download image {image_name}")
#         except FileNotFoundError:
#             print(f"Error: The file at {csv_file} was not found.")
#         except Exception as e:
#             print(f"Error occurred: {e}")

# def download_images_from_multiple_csv(csv_files, save_directory, downloaded_log):
#     for csv_file in csv_files:
#         dataset_name = os.path.splitext(os.path.basename(csv_file))[0]
#         print(f"Processing dataset: {dataset_name}")
#         download_images_from_csv(csv_file, dataset_name, save_directory, downloaded_log)

# def get_all_csv_files(directory, start_from=None):
#     files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')]
#     print(f"CSV files found in directory: {[os.path.basename(f) for f in files]}")
    
#     if start_from:
#         matching_files = [file for file in files if os.path.basename(file) == start_from]
#         if matching_files:
#             start_index = files.index(matching_files[0])
#             files = files[start_index:]
#         else:
#             print(f"File '{start_from}' not found in the directory '{directory}'. Starting from the first file.")
    
#     return files

# # Example usage
# directory_with_csv_files = 'ml_model/data/filipino_food/'  # Directory containing the CSV files
# save_directory = 'ml_model/data_collection/filipino_food/'  # Directory to save images
# downloaded_log = 'downloaded_log.txt'  # Log file to track downloaded images

# # Get all CSV files in the directory, starting from 'tapa.csv' if it exists
# csv_files = get_all_csv_files(directory_with_csv_files, start_from='tapa.csv')

# # Download images from all CSV files
# download_images_from_multiple_csv(csv_files, save_directory, downloaded_log)


from bing_image_downloader import downloader

# Downloads images for "afritada" into the existing folder
downloader.download("afritada", limit=100, output_dir="ml_model/data_collection/filipino_food", adult_filter_off=True, force_replace=False, timeout=60)
