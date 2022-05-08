import cv2
import numpy as np
from arg_parser import get_args

SCREEN_SIZE = (1280, 720)
DEBUG_SCREEN_SIZE = (600, 400)
DILATED_ITRS = 11
TRESHOLD_VAL = 38
FPS = 20
GAUSS_KERNEL_VAL = 3


def main():
    args = get_args()
    debug = args.debug
    link = args.link
    mask_upper_left = args.mask_upper_left
    mask_lower_right = args.mask_lower_right
    smallest_area = args.smallest_area

    cap = cv2.VideoCapture(link)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("output.mp4", fourcc, FPS, SCREEN_SIZE)

    _, frame1 = cap.read()
    _, frame2 = cap.read()

    mask = None
    if mask_lower_right is not None and mask_upper_left is not None:
        mask = np.zeros(frame1.shape[:2], dtype="uint8")
        cv2.rectangle(mask, mask_upper_left, mask_lower_right, 255, -1)

    while cap.isOpened():
        if mask is not None:
            frame1 = cv2.bitwise_and(frame1, frame1, mask=mask)
            frame2 = cv2.bitwise_and(frame2, frame2, mask=mask)

        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (GAUSS_KERNEL_VAL, GAUSS_KERNEL_VAL), 0)
        _, thresh = cv2.threshold(blur, TRESHOLD_VAL, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=DILATED_ITRS)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            if cv2.contourArea(contour) < smallest_area:
                continue
            else:
                cv2.rectangle(frame1, (x, y), (x + w, y + h), (255, 0, 255), 3)
                cv2.putText(frame1, "Status: {}".format('Movement'), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 3)

        image = cv2.resize(frame1, SCREEN_SIZE)
        out.write(image)

        if debug:

            resized_frame1 = cv2.resize(frame1, DEBUG_SCREEN_SIZE)
            resized_frame2 = cv2.resize(frame2, DEBUG_SCREEN_SIZE)
            resized_diff = cv2.resize(diff, DEBUG_SCREEN_SIZE)
            resized_gray = cv2.resize(gray, DEBUG_SCREEN_SIZE)
            resized_blur = cv2.resize(blur, DEBUG_SCREEN_SIZE)
            resized_thresh = cv2.resize(thresh, DEBUG_SCREEN_SIZE)
            resized_dilated = cv2.resize(dilated, DEBUG_SCREEN_SIZE)
            result = cv2.resize(frame1, DEBUG_SCREEN_SIZE)
            cv2.imshow("Frame1", resized_frame1)
            cv2.imshow("Frame2", resized_frame2)
            cv2.imshow("Difference between frame1 and frame2", resized_diff)
            cv2.imshow("Gray on diff image", resized_gray)
            cv2.imshow("Blurred gray image", resized_blur)
            cv2.imshow("Thresh image", resized_thresh)
            cv2.imshow("Dilated image with thresh", resized_dilated)
            cv2.imshow("result", result)
            cv2.waitKey(0)
        else:
            frame1 = cv2.resize(frame1, SCREEN_SIZE)
            cv2.imshow("result", frame1)

        frame1 = frame2
        _, frame2 = cap.read()

        if cv2.waitKeyEx(1) == ord('q') or frame2 is None:
            break

    cv2.destroyAllWindows()
    cap.release()
    out.release()


if __name__ == "__main__":
    main()
