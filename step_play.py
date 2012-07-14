import numpy
import pygame
import time

from pattern import Pattern, PatternListener

LATENCY = 8

usleep = lambda x: time.sleep(x/1000000.0)

class StepSequencer(object):
    def __init__(self, pattern=Pattern()):
        pygame.init()
        basepath = "/home/ensonic/Samples/[TR-808 Zone]/TR-909/"
        self.snd = []
        self.snd.append(pygame.mixer.Sound(basepath + "BD/BT7A0D0.WAV"))
        self.snd.append(pygame.mixer.Sound(basepath + "SD/ST0T7S3.WAV"))
        self.snd.append(pygame.mixer.Sound(basepath + "HH/CLOP3.WAV"))
        self.snd.append(pygame.mixer.Sound(basepath + "CP/HANDCLP1.WAV"))
        self.snd.append(pygame.mixer.Sound(basepath + "RI/RIM127.WAV"))
        self.snd.append(pygame.mixer.Sound(basepath + "RI/RIM127.WAV"))
        self.snd.append(pygame.mixer.Sound(basepath + "RI/RIM127.WAV"))
        self.snd.append(pygame.mixer.Sound(basepath + "RI/RIM127.WAV"))
        self.bpm = 120.0
        self.pattern = pattern

    @property
    def bpm(self):
        return 15000000.0 / self._step_time

    @bpm.setter
    def bpm(self, bpm):
        self._step_time = 15000000.0 / bpm
        print "tick time: %f" % self._step_time

    def play(self):
        step = -1
        while True:
            step = (step + 1) % 16
            self.trigger_step(step)
            usleep(self._step_time)

    def trigger_step(self, step):
        #print "tick"
        for track, note_on in enumerate(self.pattern.steps[step]):
            if note_on and not self.pattern.muted[track]:
                self.snd[track].play()


if __name__ == '__main__':
    pattern_listener = PatternListener()
    pattern_listener.start()
    step = StepSequencer(pattern_listener.pattern)
    step.play()
