import cv2
import numpy as np
from arg_parser import get_args

SCREEN_SIZE = (1280, 720)
DEBUG_SCREEN_SIZE = (600, 400)
DILATED_ITRS = 11
TRESHOLD_VAL = 38
FPS = 20
GAUSS_KERNEL_VAL = 3


def calc_frame(mask, list_of_regions, a=255, b=-1):
    for (mask_upper_left, mask_lower_right) in list_of_regions:
        cv2.rectangle(mask, mask_upper_left, mask_lower_right, a, b)


def main():
    args = get_args()
    debug = args.debug
    link = args.link

    cap = cv2.VideoCapture(link)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("output.mp4", fourcc, FPS, SCREEN_SIZE)

    size = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    # print(size)
    smallest_area = args.smallest_area * size[0] * size[1] // 1000
    print(smallest_area)

    cord_ = tuple[int, int]
    list_of_regions: list[tuple[cord_, cord_]] = []
    for (upper_left_arg, lower_right_arg) in zip(args.mask_upper_left, args.mask_lower_right):
        if upper_left_arg is not None and lower_right_arg is not None:
            mask_upper_left = tuple(int(el_1 * el_2 / 100) for el_1, el_2 in zip(upper_left_arg, size))
            mask_lower_right = tuple(int(el_1 * el_2 / 100) for el_1, el_2 in zip(lower_right_arg, size))
            print(mask_lower_right, mask_upper_left)
            list_of_regions.append((mask_upper_left, mask_lower_right))
        else:
            mask_upper_left = None
            mask_lower_right = None

    _, frame1 = cap.read()
    _, frame2 = cap.read()

    mask = np.zeros(frame1.shape[:2], dtype="uint8")
    calc_frame(mask, list_of_regions)


    while cap.isOpened():
        # if mask is not None:
        frame1_with_mask = cv2.bitwise_and(frame1, frame1, mask=mask)
        frame2_with_mask = cv2.bitwise_and(frame2, frame2, mask=mask)
        diff = cv2.absdiff(frame1_with_mask, frame2_with_mask)
        calc_frame(frame1, list_of_regions, (255, 0, 0), 3)

        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (GAUSS_KERNEL_VAL, GAUSS_KERNEL_VAL), 0)
        _, thresh = cv2.threshold(blur, TRESHOLD_VAL, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=DILATED_ITRS)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cv2.putText(frame1, "Movement video status", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            if cv2.contourArea(contour) < smallest_area:
                continue
            else:
                cv2.rectangle(frame1, (x, y), (x + w, y + h), (255, 0, 255), 3)


        image = cv2.resize(frame1, SCREEN_SIZE)
        out.write(image)

        if debug:
            titles = ["Frame1", "Frame2", "Frame1 and Frame2 diff", "Gray on diff", "Blurred grey",
                      "Threshold", "Dilated with threshold", "Result"]
            images = [frame1, frame2, diff, gray, blur, thresh, dilated, frame1]
            images = [cv2.resize(image, DEBUG_SCREEN_SIZE) for image in images]
            for title_and_image in zip(titles, images):
                cv2.imshow(*title_and_image)

            cv2.waitKey(0)
        else:
            frame1 = cv2.resize(frame1, SCREEN_SIZE)
            cv2.imshow("Result", frame1)
            # frame1_with_mask = cv2.resize(frame1_with_mask, SCREEN_SIZE)
            # cv2.imshow("Result", frame1_with_mask)

        frame1 = frame2
        _, frame2 = cap.read()

        if cv2.waitKey(7) == ord('q') or frame2 is None:
            break

    cv2.destroyAllWindows()
    cap.release()
    out.release()


if __name__ == "__main__":
    main()
