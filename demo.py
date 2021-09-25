"""

"""

import os
import pygame
import aseprite


if __name__ == '__main__':
    pygame.init()
    json_file = os.path.join('resources', 'sprite_data', 'sprite.json')
    image_dir = os.path.join('resources', 'sprite_sheets')
    demo = aseprite.Animation(image_dir, json_file, "down", "walk")

    surface = pygame.display.set_mode((200, 200))
    clock = pygame.time.Clock()
    frame_rate = 60
    font = pygame.font.SysFont('Courier New', 12)
    running = True
    keys_pressed = {}

    while running:
        delta_time = clock.tick(frame_rate) / 1000.0
        moving = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                keys_pressed[event.key] = True
            if event.type == pygame.KEYUP:
                keys_pressed[event.key] = False

        if keys_pressed.get(pygame.K_UP):
            demo.change_layer("up")
            moving = True
        if keys_pressed.get(pygame.K_DOWN):
            demo.change_layer("down")
            moving = True
        if keys_pressed.get(pygame.K_LEFT):
            demo.change_layer("left")
            moving = True
        if keys_pressed.get(pygame.K_RIGHT):
            demo.change_layer("right")
            moving = True

        if moving:
            demo.change_tag("walk")
        else:
            demo.change_tag("idle")

        demo.update(delta_time)
        surface.fill((0, 0, 0))

        sprite_surface = demo.get_surface()
        surface.blit(pygame.transform.scale(sprite_surface, (128, 128)), (90, 20))

        lines = [
            f"FPS: {round(clock.get_fps(),2)}",
            f"FRAME: {demo.current_frame}/{demo.get_tag_frame_length()}",
            f"TIME: {round(demo.elapsed_time,1)}/{round(demo.get_frame_duration(),1)}",
            f"TAG: {demo.current_tag}",
            f"LAYER: {demo.current_layer}"
        ]
        x, y, = 2, 2
        for line in lines:
            text = font.render(line, True, (255, 255, 255))
            surface.blit(text, (x, y))
            y += font.get_linesize()

        pygame.display.update()
