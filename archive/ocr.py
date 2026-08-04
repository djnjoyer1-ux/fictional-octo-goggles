import pytesseract
from pdf2image import convert_from_path
from sympy import sympify, pretty
from PIL import Image
import os

# Path to tesseract executable (update if necessary)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows path

def ocr_pdf(pdf_path, output_text="output_text.txt"):
    """Converts PDF to images, performs OCR, and optionally parses math expressions."""
    # Convert PDF pages to images
    print("📄 Converting PDF pages to images...")
    pages = convert_from_path(pdf_path, 300)  # 300 DPI for better accuracy

    all_text = ""
    for i, page in enumerate(pages):
        print(f"🔍 OCR on page {i + 1}...")
        text = pytesseract.image_to_string(page, config='--psm 6')
        all_text += f"\n--- Page {i + 1} ---\n{text}\n"

    # Save the extracted text
    with open(output_text, 'w', encoding='utf-8') as f:
        f.write(all_text)
    print(f"✅ OCR text saved to {output_text}")

    # Attempt to parse mathematical expressions with SymPy
    try:
        print("\n🔢 Attempting to parse math expressions with SymPy...")
        math_expr = sympify(all_text)
        print("\n🧮 Parsed Math Expression:\n", pretty(math_expr))
    except Exception as e:
        print("⚠️ Could not parse math expressions:", e)

if __name__ == "__main__":
    # Provide the path to your PDF file here
    pdf_path = "C:\Users\user\Downloads\OCR TEST ch2 review Advanced Engineering Mathematics -- Michael Greenberg (1).pdf"
    ocr_pdf(pdf_path)
