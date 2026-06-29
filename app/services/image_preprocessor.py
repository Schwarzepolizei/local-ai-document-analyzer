import cv2
import numpy as np
from PIL import Image


def deskew_image(gray: np.ndarray) -> np.ndarray:
    """
    Выравнивает изображение по углу наклона текста.
    На вход подается grayscale image.
    """
    coords = np.column_stack(np.where(gray < 255))

    if coords.size == 0:
        return gray

    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 0.3:
        return gray

    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)

    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        gray,
        matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )

    return rotated


def preprocess_image_for_ocr(file_bytes: bytes) -> Image.Image:
    nparr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Could not decode image bytes")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = deskew_image(gray)

    denoised = cv2.GaussianBlur(gray, (3, 3), 0)

    thresholded = cv2.threshold(
        denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return Image.fromarray(thresholded)


def preprocess_pil_image_for_ocr(pil_image: Image.Image) -> Image.Image:
    image = np.array(pil_image)

    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    gray = deskew_image(gray)

    denoised = cv2.GaussianBlur(gray, (3, 3), 0)

    thresholded = cv2.threshold(
        denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return Image.fromarray(thresholded)