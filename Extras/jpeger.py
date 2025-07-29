from PIL import Image
import os

input_dir = "Extras/input_pics"
output_dir = "Extras/input_pics/output"
os.makedirs(output_dir, exist_ok=True)

# Set a max width/height in pixels
max_size = (1200, 1200)

for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        input_path = os.path.join(input_dir, filename)
        img = Image.open(input_path)
        img = img.convert("RGB")  # Needed for JPEG
        img.thumbnail(max_size, Image.LANCZOS)

        output_filename = os.path.splitext(filename)[0] + ".jpg"
        output_path = os.path.join(output_dir, output_filename)

        img.save(output_path, "JPEG", quality=80, optimize=True)

print("All images resized and compressed.")