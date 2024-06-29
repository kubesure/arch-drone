from PIL import Image
import os

image_folder = "../data/images/rings/"


if __name__ == '__main__':
    for filename in os.listdir(image_folder):
        if filename.endswith(".jpeg"):
            img_path = os.path.join(image_folder, filename)
            image = Image.open(img_path)
            exif_data = image._getexif()
            if 37386 in exif_data:
                focal_length = exif_data[37386]
                print(f"Focal Length: {focal_length}mm")



