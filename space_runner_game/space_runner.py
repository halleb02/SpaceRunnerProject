import pygame
import sys
import random
import os
from pygame.sprite import Sprite

IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), 'images')

class SpaceShip(Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        original_image = pygame.image.load(os.path.join(IMAGE_FOLDER, "spaceship.png"))
        rotated_image = pygame.transform.rotate(original_image, -90)
        self.image = pygame.transform.scale(rotated_image, (100, 75))
        self.rect = self.image.get_rect().move(100, 300)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.rect.move_ip(0, -5)
        if keys[pygame.K_DOWN]:
            self.rect.move_ip(0, 5)

class SpaceRunnerGame:
    def __init__(self):
        pygame.init()  # Initialize pygame
        pygame.font.init()  # Initialize the font module
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Space Runner")
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load(os.path.join(IMAGE_FOLDER, "background.png"))
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        self.spaceship = SpaceShip()
        self.asteroids = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.enemy_ships = pygame.sprite.Group()  # Group to hold enemy ships
        self.explosions = pygame.sprite.Group()   # Group to hold explosions
        self.score = 0
        self.spawn_rate = 40
        self.spawn_counter = self.spawn_rate
        self.level_duration = 30 * 60  #
        self.level = 1  # Set initial level to 1
        self.level_timer = 0  # Initialize level timer to 0
        self.asteroid_speed = 5  # Speed of asteroid movement
        self.ufo_speed = 3  # Speed of UFO movement
        self.enemy_ship_speed = 8
        self.game_over_flag = False  # Flag to track game over state
        self.show_avoid_text = True  # Flag to track whether to display "Avoid the asteroids!" text
        self.avoid_text_timer = 300
        self.show_game_over_text = False  # Flag to track whether to display "Game Over!" text
        self.game_over_text_timer = 300
        self.show_enemy_avoid_text = False  # Flag to track whether to display "Avoid the enemy spaceships!" text
        self.enemy_avoid_text_timer = 300
        self.paused = False  # Flag to track whether the game is paused
        self.game_over_timer = 300

        # Font initialization for text rendering
        self.font = pygame.font.SysFont("Arial", 36)

    def game_loop(self):
        level_timer = self.level_duration
        while not self.game_over_flag:
            self.handle_events()
            if not self.paused:  # Only update and draw if the game is not paused
                self.update()
                self.draw()
                pygame.display.flip()
                self.clock.tick(60)
                level_timer -= 1
            if level_timer == 0:
                if self.level == 1:
                    self.transition_to_level_2()
                else:
                    self.end_game()
        self.display_game_over()

    def spawn_enemy_ships(self):
        if self.level == 2:
            self.spawn_counter -= 1
            if self.spawn_counter <= 0:
                x = random.randint(self.screen_width, self.screen_width * 2)
                y = random.randint(0, self.screen_height)
                new_enemy_ship = EnemyShip(x, y)
                self.enemy_ships.add(new_enemy_ship)
                self.spawn_counter = self.spawn_rate

    def transition_to_level_2(self):

        self.level_timer = self.level_duration
        self.level = 2
        self.spawn_rate = 40  #
        self.spawn_counter = self.spawn_rate
        self.level_duration = 30 * 60
        self.show_enemy_avoid_text = True

    def display_game_over(self):
        while self.game_over_timer > 0:
            self.handle_events()
            self.draw_game_over()
            pygame.display.flip()
            self.clock.tick(60)
            self.game_over_timer -= 1

        sys.exit(0)  # Exit the game

    def draw_game_over(self):
        # Render the "Game Over!" message
        game_over_text = self.font.render("Game Over!", True, (255, 0, 0))
        self.screen.blit(game_over_text, (self.screen_width // 2 - game_over_text.get_width() // 2,
                                          self.screen_height // 2 - game_over_text.get_height() // 2))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.toggle_pause()

    def update(self):
        self.spaceship.update()
        self.spawn_asteroids()
        self.spawn_aliens()
        self.spawn_enemy_ships()
        self.asteroids.update()
        self.aliens.update()
        self.enemy_ships.update()
        self.explosions.update()

        collided = False  # Flag to track collision with an obstacle

        for asteroid in self.asteroids:
            if self.spaceship.rect.colliderect(asteroid.rect):
                self.trigger_explosion(self.spaceship.rect.center)
                collided = True

        for alien in self.aliens:
            if self.spaceship.rect.colliderect(alien.rect):
                self.trigger_explosion(self.spaceship.rect.center)
                collided = True

        for enemy_ship in self.enemy_ships:
            if self.spaceship.rect.colliderect(enemy_ship.rect):
                self.trigger_explosion(self.spaceship.rect.center)
                collided = True

        if collided:
            self.end_game(win=False)  # Call end_game with "Game Over" message
            self.game_over_flag = True  # Set game_over_flag to True

        else:
            self.score += 1
            self.update_level()

    def end_game(self, win=False):
        if win:
            if self.level == 2 and not self.game_over_flag:
                self.show_game_over_text = True
                self.game_over_text_timer = 300
                self.paused = True  # Pause the game when level 2 is completed
            else:
                self.show_game_over_text = True
                self.game_over_text_timer = 300
        else:
            self.show_game_over_text = True
            self.game_over_text_timer = 300
            if self.level == 2:  # Pause the game at the end of level 2 if the player loses
                self.paused = True

    def update_level(self):

        self.level_timer -= 1
        if self.level_timer == 0:
            if self.level == 1:
                self.transition_to_level_2()
            else:
                self.end_game(win=True)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.spaceship.draw(self.screen)
        self.asteroids.draw(self.screen)
        self.aliens.draw(self.screen)
        self.enemy_ships.draw(self.screen)
        self.explosions.draw(self.screen)

        # Render level text
        level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (20, 20))

        # Render game over or win text if applicable
        if self.show_game_over_text:
            if self.level == 2 and not self.game_over_flag:
                game_over_text = self.font.render("Congratulations!! You Win!!", True, (0, 255, 0))
            else:
                game_over_text = self.font.render("Game Over!", True, (255, 0, 0))
            self.screen.blit(game_over_text, (self.screen_width // 2 - game_over_text.get_width() // 2,
                                              self.screen_height // 2 - game_over_text.get_height() // 2))

        # Render "Avoid the asteroids!" message
        if self.show_avoid_text and not self.show_enemy_avoid_text:
            avoid_text = self.font.render("Avoid the asteroids and UFOs!", True, (255, 255, 255))
            self.screen.blit(avoid_text, (self.screen_width // 2 - avoid_text.get_width() // 2, 20))

        # Render "Avoid the enemy spaceships!" message
        if self.show_enemy_avoid_text:
            enemy_avoid_text = self.font.render("Avoid the enemy spaceships and UFOs!", True, (255, 255, 255))
            self.screen.blit(enemy_avoid_text, (self.screen_width // 2 - enemy_avoid_text.get_width() // 2, 60))

    def spawn_asteroids(self):
        self.spawn_counter -= 1
        if self.spawn_counter <= 0:
            x = random.randint(self.screen_width, self.screen_width * 2)
            y = random.randint(0, self.screen_height)
            new_asteroid = Asteroid(x, y, self.asteroid_speed)
            self.asteroids.add(new_asteroid)
            self.spawn_counter = self.spawn_rate

    def spawn_aliens(self):
        if self.level == 1:
            if not self.aliens and self.spawn_counter % self.spawn_rate == 0:
                # Spawn UFOs when asteroids appear
                x1 = 800
                y1 = 100
                new_alien1 = Alien(x1, y1, self.ufo_speed)
                self.aliens.add(new_alien1)

                x2 = 500
                y2 = 200
                new_alien2 = Alien(x2, y2, self.ufo_speed)
                self.aliens.add(new_alien2)

    def trigger_explosion(self, position):
        # Start explosion animation at the specified position
        explosion = Explosion(position)
        self.explosions.add(explosion)
        self.paused = True  # Pause the game when explosion occurs

    def toggle_pause(self):
        self.paused = not self.paused




class Asteroid(Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        original_image = pygame.image.load(os.path.join(IMAGE_FOLDER, "asteroid.png"))
        self.image = pygame.transform.scale(original_image, (50, 50))
        self.rect = self.image.get_rect().move(x, y)
        self.speed = speed

    def update(self):
        self.rect.move_ip(-self.speed, 0)

class Alien(Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        original_image = pygame.image.load(os.path.join(IMAGE_FOLDER, "alien_ufo.png"))
        # Maintain aspect ratio while resizing
        aspect_ratio = original_image.get_width() / original_image.get_height()
        new_height = 100
        new_width = int(new_height * aspect_ratio)
        self.image = pygame.transform.scale(original_image, (new_width, new_height))
        self.rect = self.image.get_rect().move(x, y)
        self.direction = random.choice([-1, 1])  # Random initial movement direction (left or right)
        self.speed = speed  # Movement speed

    def update(self):
        # Move the alien UFO horizontally
        self.rect.move_ip(self.direction * self.speed, 0)

        # Reverse direction when hitting left or right bounds of the screen
        if self.rect.left <= 0 or self.rect.right >= 1024:
            self.direction *= -1

class EnemyShip(Sprite):
    def __init__(self, x, y):
        super().__init__()
        original_image = pygame.image.load(os.path.join(IMAGE_FOLDER, "enemy_ship.png"))
        rotated_image = pygame.transform.rotate(original_image, 90)
        self.image = pygame.transform.scale(rotated_image, (100, 50))
        self.rect = self.image.get_rect().move(x, y)
        self.speed = 8

    def update(self):
        self.rect.move_ip(-self.speed, 0)

class Explosion(Sprite):
    def __init__(self, position):
        super().__init__()
        self.images = [pygame.image.load(os.path.join(IMAGE_FOLDER, f"explosion_{i}.png")) for i in range(1, 11)]
        self.index = 0
        self.image = pygame.transform.scale(self.images[self.index], (200, 200))
        self.rect = self.image.get_rect(center=position)
        self.timer = 12

    def update(self):
        self.timer -= 1
        if self.timer == 0:
            self.index += 1
            if self.index < len(self.images):
                self.image = pygame.transform.scale(self.images[self.index], (200, 200))
            else:
                self.kill()



if __name__ == '__main__':
    SpaceRunnerGame().game_loop()