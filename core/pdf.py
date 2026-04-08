from pdf2image import convert_from_path
import os

def pdf_to_png(pdf_path, output_dir):
    images = convert_from_path(pdf_path, dpi=300)

    for i, img in enumerate(images):
        img.save(os.path.join(output_dir, f"slide_{i+1:04d}.png"), "png")
