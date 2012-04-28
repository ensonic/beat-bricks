import numpy as np
import cv2

MAIN_WINDOW = 'hello'
RECT_WINDOW = 'rect'
CELL_SIZE = 32
GRID_SIZE = 16 * CELL_SIZE

def global_on_mouse(event, x, y, unknown, lego_player):
    lego_player.on_mouse(event, x, y)

class LegoPlayer(object):
    def __init__(self):
        self.homography = None
        self.rect = np.empty((4, 2))
        self.rect_index = -1

        cv2.namedWindow(MAIN_WINDOW)
        cv2.setMouseCallback(MAIN_WINDOW, global_on_mouse, self)
        cv2.namedWindow(RECT_WINDOW)
        self.capture = cv2.VideoCapture(0)

    def on_mouse(self, event, x, y):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.has_roi():
                self.rect_index = -1
            self.rect_index += 1
            self.rect[self.rect_index] = [x, y]
            if self.has_roi():
                self.compute_homography()

    def has_roi(self):
        return self.rect_index == 3

    def compute_homography(self):
        src_points = self.rect
        dst_points = np.zeros_like(src_points)
        dst_points[1][0] = GRID_SIZE
        dst_points[2] = [GRID_SIZE, GRID_SIZE]
        dst_points[3][1] = GRID_SIZE
        self.homography = cv2.findHomography(src_points, dst_points)[0]

    def process_frame(self, frame):
        if self.homography is not None:
            return cv2.warpPerspective(frame, self.homography, (GRID_SIZE, GRID_SIZE))

    def loop(self):
        while True:
            success, frame = self.capture.read()
            cv2.imshow(MAIN_WINDOW, frame)
            result = self.process_frame(frame)
            if result is not None:
                cv2.imshow(RECT_WINDOW, result)
            cv2.waitKey(10)

if __name__ == '__main__':
    lego_player = LegoPlayer()
    lego_player.loop()
