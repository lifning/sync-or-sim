import pygame_sdl2 as pygame

text_log = []

text_log_surface = None
max_lines_to_show = 0

pygame.font.init()
log_font = pygame.font.Font("visualization/opti.pcf", 16)

line_height = 11
padding_from_edges = 4

color_fg = (150, 150, 150)

def init_text_log_surface(log_size):
    global text_log_surface, max_lines_to_show
    _, h = log_size
    text_log_surface = pygame.Surface(log_size)
    max_lines_to_show = (h - (2 * padding_from_edges)) // line_height

def blit_text_to_surface():
    if text_log_surface is None:
        return

    text_log_surface.fill((0, 0, 0))
    for i in range(min(len(text_log), max_lines_to_show)):
        text_log_surface.blit(log_font.render(text_log[i], True, color_fg), (padding_from_edges, i * line_height + padding_from_edges))

def log_text(text):
    text_log.append(text)
    if len(text_log) > max_lines_to_show:
        text_log.pop(0)
    blit_text_to_surface()

def draw():
    return text_log_surface
