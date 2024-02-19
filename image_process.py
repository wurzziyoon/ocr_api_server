import cv2
import numpy as np

def _convert(src):
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    low_hsv = np.array([0, 0, 0])
    high_hsv = np.array([180, 255, 46])
    mask = cv2.inRange(hsv, lowerb=low_hsv, upperb=high_hsv)
    mask = 255 - mask  # invert color
    mask = mask[10:28, 20:130]  # crop

    # Reduce noise
    for i in range(1, mask.shape[0] - 1):
        for j in range(1, mask.shape[1] - 1):
            if mask[i, j] == 0 \
                    and mask[i - 1, j] == 255 and mask[i + 1, j] == 255 \
                    and mask[i, j - 1] == 255 and mask[i, j + 1] == 255:
                mask[i, j] = 255

    # cv2.imwrite('file.png', mask)  # debug

    success, encoded_image = cv2.imencode('.png', mask)
    return encoded_image.tobytes()