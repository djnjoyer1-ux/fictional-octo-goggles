import cv2
import matplotlib.pyplot as plt

def cartoonize_image(img_path):
    # Load image
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 1️⃣ Apply bilateral filter to smooth colors while preserving edges
    color = cv2.bilateralFilter(img_rgb, d=9, sigmaColor=250, sigmaSpace=250)

    # 2️⃣ Convert to grayscale and apply median blur
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    blur = cv2.medianBlur(gray, 7)

    # 3️⃣ Detect edges using adaptive thresholding
    edges = cv2.adaptiveThreshold(blur, 255, 
                                  cv2.ADAPTIVE_THRESH_MEAN_C, 
                                  cv2.THRESH_BINARY, 
                                  blockSize=9, C=2)

    # 4️⃣ Combine color image with edges
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    # Show results
    plt.figure(figsize=(10, 10))
    plt.subplot(1, 3, 1)
    plt.title("Original")
    plt.imshow(img_rgb)
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.title("Edges")
    plt.imshow(edges, cmap="gray")
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.title("Cartoon")
    plt.imshow(cartoon)
    plt.axis("off")

    plt.show()

# Example usage
cartoonize_image("input.jpg")
