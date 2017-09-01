import pygame

text_log = []
text_log_surface = pygame.Surface((512, 512))

pygame.font.init()
log_font = pygame.font.Font("visualization/opti.pcf", 16)

line_height = 11
max_lines_to_show = text_log_surface.get_height() // line_height

color_fg = (150, 150, 150)

def blit_text_to_surface():
    for i in range(min(len(text_log), max_lines_to_show)):
        text_log_surface.blit(log_font.render(text_log[i], True, color_fg), (4, i * line_height + 4))

def log_text(text):
    text_log.append(text)
    if len(text_log) > max_lines_to_show:
        text_log.pop(0)
    blit_text_to_surface()


def draw():
    return text_log_surface
