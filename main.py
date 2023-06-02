import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from pathlib import Path
from tempfile import TemporaryDirectory
from multiprocessing import Pool, cpu_count


def convert_pdf_to_image_and_ocr(args):
    pdf_path, tempdir, page_num, output_file, resolution = args
    if not pdf_path.exists():
        raise FileNotFoundError(f"The file {pdf_path} was not found.")

    pdf_page = convert_from_path(
        str(pdf_path), dpi=resolution, first_page=page_num, last_page=page_num)[0]
    img_file = tempdir / f"page_{page_num:03}.jpg"
    pdf_page.save(img_file, "JPEG")

    text = pytesseract.image_to_string(str(img_file))
    text = text.replace("-\n", "")
    with output_file.open("w") as file:
        file.write(text)

    img_file.unlink()


def main():
    PDF_file = Path("d5.pdf")
    out_directory = Path("out")
    out_directory.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)

        with open(PDF_file, "rb") as file:
            num_pages = len(PdfReader(file).pages)

        resolution = 500
        args = [(PDF_file, tempdir, page_num, out_directory /
                 f"out_text_{page_num:03}.txt", resolution) for page_num in range(1, num_pages+1)]

        with Pool(min(cpu_count(), num_pages)) as p:
            p.map(convert_pdf_to_image_and_ocr, args)

        # Merge all output files into one
        with (out_directory / "out_text.txt").open("w") as outfile:
            for page_num in range(1, num_pages+1):
                temp_file = out_directory / f"out_text_{page_num:03}.txt"
                with temp_file.open("r") as infile:
                    outfile.write(infile.read())
                temp_file.unlink()


if __name__ == "__main__":
    main()
