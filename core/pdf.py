from pdf2image import convert_from_path

def pdf_to_png(dirs, pdf_path):
    images = convert_from_path(pdf_path, dpi=300)

    for i, img in enumerate(images):
        out_path = dirs["video"] / f"slide_{i+1:04d}.png"
        img.save(out_path, format="png")
