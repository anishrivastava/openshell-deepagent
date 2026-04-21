import pytesseract
from PIL import Image
import cv2

# OPTIONAL (only if error comes)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

image_path = r"C:\Users\shash\OneDrive\Desktop\AI_data\Images\box_1.png"

# 🔥 Read image
img = cv2.imread(image_path)

# 🔥 Convert to grayscale (improves accuracy)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 🔥 OCR
text = pytesseract.image_to_string(gray)

print("\n===== OCR OUTPUT =====\n")
print(text)