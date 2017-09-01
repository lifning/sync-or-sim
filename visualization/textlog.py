import pygame

current_frame = 0
text_log = []
text_log_surface = pygame.Surface((250, 64))

pygame.font.init()
log_font = pygame.font.Font(None, 10)

def get_surface

def log_text(text)
    text_log.append((current_frame, text))
def draw()
    text_lines = [string for (added_in_frame, string) in text_log].reverse()
    text_log_surface.blit(log_font.render("\n".join(text_lines), True, black), (0,0))

    current_frame += 1
