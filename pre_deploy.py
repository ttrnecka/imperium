import os
import shutil

ROOT = os.path.dirname(__file__)

# clean static folder
static_npm_folders = [
  "css", "fonts", "img", "js"
]
static_folder = "static"
print("Cleaning static folder")
for folder in static_npm_folders:
  folder_path = file_path = os.path.join(ROOT,static_folder, folder)
  if os.path.exists(folder_path):
    shutil.rmtree(folder_path)
print("Done")
