import cv2

def image_to_ascii(img_path):
    # Characters from darkest to lightest
    ascii_chars = "@%#*+=-:. "
    num_chars = len(ascii_chars)

    # Load image
    img = cv2.imread(img_path)
    if img is None:
        print("❌ Error: Could not load image.")
        return

    # Resize to 512x512
    img = cv2.resize(img, (512, 512))

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Build ASCII art
    ascii_art = []
    for y in range(512):
        row = ""
        for x in range(512):
            pixel = gray[y, x]
            char_idx = int(pixel / 255 * (num_chars - 1))
            row += ascii_chars[char_idx]
        ascii_art.append(row)

    # Output
    for row in ascii_art:
        print(row)

# Example usage
image_to_ascii("input.jpg")
