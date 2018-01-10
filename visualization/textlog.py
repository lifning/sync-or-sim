import pygame


class TextLog:
    instance = None

    color_fg = (150, 150, 150)
    line_height = 11
    padding = 4

    def __init__(self, log_size):
        assert TextLog.instance is None
        TextLog.instance = self
        pygame.font.init()
        self.log_font = pygame.font.Font("visualization/opti.pcf", 16)
        _, h = log_size
        self.surface = pygame.Surface(log_size)
        self.max_lines = (h - (2 * self.padding)) // self.line_height
        self.text_log = []

    def blit_text(self):
        self.surface.fill((0, 0, 0))
        for i in range(min(len(self.text_log), self.max_lines)):
            self.surface.blit(self.log_font.render(self.text_log[i], True, self.color_fg),
                              (self.padding, i * self.line_height + self.padding))

    def log_text(self, text):
        self.text_log.append(text)
        if len(self.text_log) > self.max_lines:
            self.text_log.pop(0)
        self.blit_text()

