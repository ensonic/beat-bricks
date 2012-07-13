import json

import cv2
import numpy

from pattern import SharedPattern

# the green/blue lego plates are 32x32 knobs
# the gray lego plate is 44x44 knobs
# we're using it with 2x2 bricks

WINDOW = 'beat it'
CELL_SIZE = 16
GRID_SIZE = 16 * CELL_SIZE


def cell_start_end(id):
    start = id * CELL_SIZE + CELL_SIZE / 4
    end = start + CELL_SIZE / 2
    return start, end


def average_cell_color_hsv(img, y, x):
    y_start, y_end = cell_start_end(y)
    x_start, x_end = cell_start_end(x)
    cell = img[
      y_start:y_end,
      x_start:x_end,
      :]
    return bgr2hsv(numpy.average(numpy.average(cell, axis=0), axis=0))

# we need some auto-tuning for the colors, or atleast for brightness

def is_note_color_hsv(color):
    h, s, v = color
    return (
        #(-0.3 < h < 0.1 and s > 0.6 and v > 200) or  # red brick
        #(0.8 < h < 1.2 and s > 0.3 and v > 220) or   # yellow brick
        #(3.2 < h < 3.6 and s > 0.9 and v > 180) or   # blue brick
        #(s < 0.1 and v > 250))                       # white brick
        (-0.3 < h < 0.2 and s > 0.6 and v > 100) or  # red brick
        (0.4 < h < 1.0 and s > 0.8 and v > 100) or   # yellow brick
        (1.95 < h < 2.5 and s > 0.8 and v > 60) or   # blue brick
        (s < 0.1 and v > 250))                       # white brick

def is_clear_color_hsv(color):
    h, s, v = color
    #return 2.5 < h < 2.9 and s > 0.7 and v > 100     # green plate
    return 1.4 < h < 2.9 and s > 0.4 and v < 80     # green plate


def bgr2hsv(color):
    b, g, r = color
    v = max(b, g, r)
    m = min(b, g, r)
    if v > 0:
        s = (v - m) / v
    else:
        s = 0
    # hue is 0 for red
    if v == r:
        h = (g - b) / (v - m)
    elif v == g:
        h = 2 + (b - r) / (v - m)
    else:
        h = 4 + (r - g) / (v - m)
    return (h, s, v)


class LegoPatternDetector(object):
    def __init__(self):
        self.homography = self.compute_homography()
        self.pattern = SharedPattern()

    def compute_homography(self):
        src_points = json.load(open('rect.json'))
        dst_points = [
            [0, 0],
            [GRID_SIZE, 0],
            [GRID_SIZE, GRID_SIZE],
            [0, GRID_SIZE]]
        return cv2.findHomography(
            numpy.asarray(src_points, float),
            numpy.asarray(dst_points, float))[0]

    def process_image(self, img):
        img = cv2.warpPerspective(img, self.homography, (GRID_SIZE, GRID_SIZE))
        self.update_notes(img)
        self.mute_tracks(img)
        return img

    def update_notes(self, img):
        for track in range(self.pattern.num_tracks):
            cells = "";
            hmin = 4.0
            hmax = -4.0
            smin = 4.0
            smax = -4.0
            vmin = 300
            vmax = 0
            for step in range(self.pattern.num_steps):
                color = average_cell_color_hsv(img, track, step)
                h, s, v = color
                if h>hmax:
                  hmax=h
                if h<hmin:
                  hmin=h
                if s>smax:
                  smax=s
                if s<smin:
                  smin=s
                if v>vmax:
                  vmax=v
                if v<vmin:
                  vmin=v
                cell = "?"
                if is_clear_color_hsv(color):
                    self.pattern.clear_step(track, step)
                    cell = " "
                elif is_note_color_hsv(color):
                    self.pattern.set_step(track, step)
                    cell = "*"
                #print "%d[%2d]=%s [h %f | s %f | v %f]" % (track, step, cell, color[0], color[1], color[2])
                cells = cells + " " + cell
            print "%d [%s] [%+f %+f | %f %f | %f %f]" % (track, cells, hmin, hmax, smin, smax, vmin, vmax)

    def mute_tracks(self, img):
        for track in range(self.pattern.num_tracks):
            color = average_cell_color_hsv(img, track + 8, 0)
            if is_clear_color_hsv(color):
                self.pattern.unmute(track)
            else:
                self.pattern.mute(track)


if __name__ == '__main__':
    capture = cv2.VideoCapture(0)
    cv2.namedWindow(WINDOW)
    pattern_detector = LegoPatternDetector()

    while True:
        success, frame = capture.read()
        if success:
            img = pattern_detector.process_image(frame)
            cv2.imshow(WINDOW, img)
        if cv2.waitKey(100) == 27:
            break
