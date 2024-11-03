import pygame
from pygame import mixer
import random
import sys
import os
import traceback
import math

# Initialize Pygame and mixer
pygame.init()
mixer.init()

# Constants
WIDTH = 1200
HEIGHT = 800
FPS = 60

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Adventure Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (147, 0, 211)
CYAN = (0, 255, 255)

def load_sprite_sheets(dir1, width, height, direction=False):
    path = os.path.join("assets", dir1)
    images = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(os.path.join(path, image)).convert_alpha()
        
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = [
                pygame.transform.flip(sprite, True, False) for sprite in sprites
            ]
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game  # Store the game instance
        
        # Animation setup
        self.SPRITES = load_sprite_sheets("Mask Dude", 32, 32, True)
        self.animation_count = 0
        self.animation_delay = 3
        self.current_sprite = 0
        
        # Basic setup
        self.image = self.SPRITES["idle_right"][0]
        self.rect = self.image.get_rect()
        
        # Position and movement
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 100
        
        # Movement attributes
        self.vel_x = 0
        self.vel_y = 0
        self.acceleration = 0.8
        self.friction = 0.85
        self.max_speed = 8
        self.jump_power = -16
        self.gravity = 0.5
        self.ground_y = HEIGHT - 100
        
        # State attributes
        self.jumping = False
        self.double_jump_available = True
        self.facing_right = True
        
        print("Available animations:", list(self.SPRITES.keys()))

    def apply_movement(self):
        # Apply gravity
        self.vel_y += self.gravity
        
        # Apply friction
        self.vel_x *= self.friction
        
        # Limit horizontal speed
        self.vel_x = max(-self.max_speed, min(self.max_speed, self.vel_x))
        
        # Update position horizontally first
        self.rect.x += int(self.vel_x)
        # Check for horizontal collisions
        blocks_hit = pygame.sprite.spritecollide(self, self.game.blocks, False)
        for block in blocks_hit:
            if self.vel_x > 0:  # Moving right
                self.rect.right = block.rect.left
            elif self.vel_x < 0:  # Moving left
                self.rect.left = block.rect.right
            self.vel_x = 0
    
        # Update position vertically
        self.rect.y += int(self.vel_y)
        # Check for vertical collisions
        blocks_hit = pygame.sprite.spritecollide(self, self.game.blocks, False)
        for block in blocks_hit:
            if self.vel_y > 0:  # Moving down
                self.rect.bottom = block.rect.top
                self.vel_y = 0
                self.jumping = False
                self.double_jump_available = True
            elif self.vel_y < 0:  # Moving up
                self.rect.top = block.rect.bottom
                self.vel_y = 0
    
        # Ground collision (optional, you might want to remove this if using only blocks)
        if self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            self.vel_y = 0
            self.jumping = False
            self.double_jump_available = True
    def update_sprite(self):
        try:
            sprite_sheet = "idle"
            if self.vel_y < 0:
                if not self.double_jump_available:
                    sprite_sheet = "double_jump"
                else:
                    sprite_sheet = "jump"
            elif self.vel_y > self.gravity * 2:
                sprite_sheet = "fall"
            elif abs(self.vel_x) > 0.5:
                sprite_sheet = "run"

            sprite_sheet_name = sprite_sheet + "_right" if self.facing_right else sprite_sheet + "_left"
            
            # Check if sprite sheet exists
            if sprite_sheet_name not in self.SPRITES:
                sprite_sheet_name = "idle_right" if self.facing_right else "idle_left"
                
            sprites = self.SPRITES[sprite_sheet_name]
            
            # Make sure current_sprite stays within bounds
            if len(sprites) > 0:  # Check if sprites list is not empty
                if self.animation_count >= self.animation_delay:
                    self.current_sprite = (self.current_sprite + 1) % len(sprites)
                    self.animation_count = 0
                
                self.image = sprites[min(self.current_sprite, len(sprites) - 1)]
                self.animation_count += 1
            else:
                # Fallback to a default sprite if no sprites are available
                self.image = self.SPRITES["idle_right"][0]
                
        except Exception as e:
            print(f"Error in update_sprite: {e}")
            # Fallback to first idle sprite
            self.image = self.SPRITES["idle_right"][0]
            self.current_sprite = 0
            self.animation_count = 0

    def jump(self):
        try:
            if not self.jumping:
                self.vel_y = self.jump_power
                self.jumping = True
                print("First jump executed")
            elif self.double_jump_available:
                self.vel_y = self.jump_power
                self.double_jump_available = False
                print("Double jump executed")
        except Exception as e:
            print(f"Error in jump method: {e}")
            traceback.print_exc()

    def update(self):
        self.apply_movement()
        self.update_sprite()

    def jump(self):
        try:
            if not self.jumping:
                self.vel_y = self.jump_power
                self.jumping = True
                print("First jump executed")
            elif self.double_jump_available:
                self.vel_y = self.jump_power
                self.double_jump_available = False
                print("Double jump executed")
        except Exception as e:
            print(f"Error in jump method: {e}")
            traceback.print_exc()

    def move_left(self):
        self.vel_x -= self.acceleration
        self.facing_right = False

    def move_right(self):
        self.vel_x += self.acceleration
        self.facing_right = True

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, name):
        super().__init__()
        self.SPRITES = load_sprite_sheets("Rock Head", 42, 42, True)
        self.animation_count = 0
        self.animation_delay = 5
        self.current_sprite = 0
        
        # Make sure we start with a valid sprite
        self.image = self.SPRITES["Idle_right"][0] if "Idle_right" in self.SPRITES else pygame.Surface((42, 42))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.name = name
        
        # Quiz setup
        self.questions = [
            {
                "question": "Apa kepanjangan dari BPJS?",
                "options": [
                    "A. Badan Penyelenggara Jaminan Sosial",
                    "B. Badan Pelayanan Jaminan Sosial",
                    "C. Badan Pemberi Jaminan Sosial",
                    "D. Badan Penyedia Jaminan Sosial"
                ],
                "correct": 0  # Index of correct answer (A)
            },
            {
                "question": "Berapa iuran BPJS Kesehatan kelas 3?",
                "options": [
                    "A. Rp35.000",
                    "B. Rp42.000",
                    "C. Rp50.000",
                    "D. Rp45.000"
                ],
                "correct": 1  # Index of correct answer (B)
            },
            {
                "question": "Apa yang TIDAK termasuk dalam layanan BPJS Kesehatan?",
                "options": [
                    "A. Rawat Inap",
                    "B. Rawat Jalan",
                    "C. Operasi Plastik Kecantikan",
                    "D. Persalinan"
                ],
                "correct": 2  # Index of correct answer (C)
            }
        ]
        
        # Quiz state
        self.current_question_index = 0
        self.score = 0
        self.answered_questions = set()
        self.show_dialog = False
        self.show_result = False
        self.result_message = ""
        self.result_timer = 0
        
        # Dialog box settings
        self.dialog_box_color = (50, 50, 50, 200)
        self.dialog_box_padding = 20
        self.font = pygame.font.Font(None, 32)
        
        # Interaction distance
        self.interaction_distance = 100
        
        self.dialog_alpha = 0
        self.question_y = HEIGHT
        self.options_x = [WIDTH] * 4
        
        # Button settings
        self.button_color = (100, 100, 255)
        self.button_hover_color = (150, 150, 255)
        self.correct_color = (100, 255, 100)
        self.wrong_color = (255, 100, 100)
        self.buttons = []
        
        # Add back button initialization here
        self.back_button = {
            'rect': pygame.Rect(WIDTH - 120, HEIGHT - 60, 100, 40),
            'text': 'Back',
            'hover': False
        }
        
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)
        self.question_font = pygame.font.Font(None, 36)

        
        self.create_buttons()
        
    def handle_hover(self, pos):
        if self.show_dialog:
            # Update hover state untuk tombol back
            self.back_button['hover'] = self.back_button['rect'].collidepoint(pos)

            # Update hover state untuk tombol opsi
            for button in self.buttons:
                button['hover'] = button['rect'].collidepoint(pos)

    def create_buttons(self):
        try:
            # Pengaturan ukuran dan jarak
            button_width = WIDTH * 0.6
            button_height = 50
            button_spacing = 30
            
            current_q = self.questions[self.current_question_index]
            total_buttons = len(current_q['options'])
            
            # Hitung total tinggi yang dibutuhkan untuk semua button
            total_height = (button_height * total_buttons) + (button_spacing * (total_buttons - 1))
            
            # Hitung posisi Y awal
            start_y = (HEIGHT - total_height) // 2 + 50
            
            self.buttons = []
            
            # Buat button hanya untuk jumlah opsi yang tersedia
            for i in range(total_buttons):
                x = (WIDTH - button_width) // 2
                y = start_y + (i * (button_height + button_spacing))
                
                button_rect = pygame.Rect(x, y, button_width, button_height)
                self.buttons.append({
                    'rect': button_rect,
                    'index': i,
                    'hover': False
                })
        except Exception as e:
            print(f"Error in create_buttons: {e}")
            self.buttons = []  # Reset buttons jika terjadi error
    
    def draw_dialog(self, screen):
        if self.show_dialog:
            try:
                # Background semi-transparan
                dialog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(dialog_surface, (0, 0, 0, 200), dialog_surface.get_rect())
                screen.blit(dialog_surface, (0, 0))

                # Judul Quiz
                title_text = "BPJS Quiz"
                title_surface = self.title_font.render(title_text, True, WHITE)
                title_rect = title_surface.get_rect(centerx=WIDTH//2, top=50)
                screen.blit(title_surface, title_rect)

                # Score dan nomor pertanyaan
                score_text = f"Score: {self.score}"
                score_surface = self.font.render(score_text, True, WHITE)
                screen.blit(score_surface, (20, 20))

                question_num_text = f"Question {self.current_question_index + 1}/{len(self.questions)}"
                question_num_surface = self.font.render(question_num_text, True, WHITE)
                screen.blit(question_num_surface, (WIDTH - question_num_surface.get_width() - 20, 20))

                # Pertanyaan
                current_q = self.questions[self.current_question_index]
                question_surface = self.question_font.render(current_q['question'], True, WHITE)
                question_rect = question_surface.get_rect(centerx=WIDTH//2, top=150)
                screen.blit(question_surface, question_rect)

                # Opsi jawaban
                options = current_q['options']
                button_width = WIDTH * 0.7
                button_height = 60
                button_spacing = 20
                start_y = 250

                for i, (button, option) in enumerate(zip(self.buttons, options)):
                    button_rect = pygame.Rect((WIDTH - button_width) // 2, 
                                              start_y + i * (button_height + button_spacing),
                                              button_width, button_height)
                    button['rect'] = button_rect  # Update button rect

                    # Warna button
                    color = self.button_hover_color if button['hover'] else self.button_color
                    pygame.draw.rect(screen, color, button_rect, border_radius=10)

                    # Teks opsi
                    text_surface = self.font.render(option, True, WHITE)
                    text_rect = text_surface.get_rect(center=button_rect.center)
                    screen.blit(text_surface, text_rect)

                # Pesan hasil jika ada
                if self.show_result and self.result_timer > 0:
                    result_surface = self.font.render(self.result_message, True, WHITE)
                    result_rect = result_surface.get_rect(centerx=WIDTH//2, bottom=HEIGHT-20)
                    screen.blit(result_surface, result_rect)

                # Tombol back di pojok kanan bawah
                pygame.draw.rect(screen, 
                               self.button_hover_color if self.back_button['hover'] else self.button_color, 
                               self.back_button['rect'], 
                               border_radius=5)
                back_text_surface = self.font.render(self.back_button['text'], True, WHITE)
                back_text_rect = back_text_surface.get_rect(center=self.back_button['rect'].center)
                screen.blit(back_text_surface, back_text_rect)

            except Exception as e:
                print(f"Error in draw_dialog: {e}")
    def handle_click(self, pos):
        if self.show_dialog:
            if self.back_button['rect'].collidepoint(pos):
                self.show_dialog = False
                self.show_result = False
                return True

            current_q = self.questions[self.current_question_index]
            
            for button in self.buttons:
                if button['rect'].collidepoint(pos):
                    if button['index'] == current_q['correct']:
                        # Correct answer
                        self.score += 1  # Increment score
                        self.result_message = "Correct!"
                        self.show_correct_animation(button['rect'])
                    else:
                        # Wrong answer
                        self.result_message = "Wrong! The correct answer was: " + current_q['options'][current_q['correct']]
                        self.show_wrong_animation(button['rect'])
                    
                    self.show_result = True
                    self.result_timer = 60
                    
                    # Always move to next random question after answering
                    self.move_to_random_question()
                    return True
        return False

    def move_to_random_question(self):
        available_questions = [i for i in range(len(self.questions)) 
                             if i != self.current_question_index]
        if available_questions:
            self.current_question_index = random.choice(available_questions)
        self.create_buttons()  # Recreate buttons for new question

    def can_interact(self, player):
        # Calculate distance between NPC and player
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        return distance <= self.interaction_distance

    def update_sprite(self):
        sprite_sheet_name = "Idle_right"  # Default animation
        
        if "Idle_right" in self.SPRITES:
            sprites = self.SPRITES["Idle_right"]
            
            if self.animation_count >= self.animation_delay:
                self.current_sprite = (self.current_sprite + 1) % len(sprites)
                self.animation_count = 0

            self.image = sprites[self.current_sprite]
            self.animation_count += 1
        else:
            print("Warning: 'Idle_right' animation not found in sprites")

    def update(self):
        self.update_sprite()
        
        # Update result timer
        if self.result_timer > 0:
            self.result_timer -= 1
            if self.result_timer == 0:
                self.show_result = False

    
    def create_buttons(self):
        current_q = self.questions[self.current_question_index]
        for i, option in enumerate(current_q['options']):
            rect = pygame.Rect(100 + (i % 2) * 300, 250 + (i // 2) * 50, 250, 40)
            self.buttons.append({'rect': rect, 'index': i, 'hover': False})

    def update_sprite(self):
        sprite_sheet_name = "Idle_right"  # Default animation
        
        if "Idle_right" in self.SPRITES:
            sprites = self.SPRITES["Idle_right"]
            
            if self.animation_count >= self.animation_delay:
                self.current_sprite = (self.current_sprite + 1) % len(sprites)
                self.animation_count = 0

            self.image = sprites[self.current_sprite]
            self.animation_count += 1
        else:
            print("Warning: 'Idle_right' animation not found in sprites")
    
    def show_correct_animation(self, rect):
        # Implementasikan animasi jawaban benar di sini
        # Misalnya, buat efek kilat hijau
        for _ in range(5):
            pygame.draw.rect(screen, GREEN, rect, border_radius=10)
            pygame.display.flip()
            pygame.time.wait(50)
            pygame.draw.rect(screen, self.button_color, rect, border_radius=10)
            pygame.display.flip()
            pygame.time.wait(50)

    def show_wrong_animation(self, rect):
        # Implementasikan animasi jawaban salah di sini
        # Misalnya, buat efek getaran
        original_x = rect.x
        for _ in range(5):
            rect.x = original_x - 5
            pygame.draw.rect(screen, RED, rect, border_radius=10)
            pygame.display.flip()
            pygame.time.wait(50)
            rect.x = original_x + 5
            pygame.draw.rect(screen, RED, rect, border_radius=10)
            pygame.display.flip()
            pygame.time.wait(50)
        rect.x = original_x
        
    def update(self):
        self.update_sprite()
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, size=32):  # increased size for better visibility
        super().__init__()
        try:
            # Load the terrain sprite sheet
            sprite_sheet = pygame.image.load(os.path.join("assets", "Terrain (16x16).png")).convert_alpha()
            # Create a surface for our block
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            # Scale and draw the terrain texture onto our block
            scaled_terrain = pygame.transform.scale(sprite_sheet.subsurface((0, 0, 16, 16)), (size, size))
            self.image.blit(scaled_terrain, (0, 0))
        except pygame.error as e:
            print(f"Error loading sprite: {e}")
            self.image = pygame.Surface((size, size))
            self.image.fill((100, 100, 100))  # Gray color for missing texture
        
        self.image = pygame.Surface((size, size))
        self.image.fill((100, 100, 100))  # Gray color
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        
# Add these new classes after the existing imports

class VirtualJoystick:
    def __init__(self):
        self.radius = 50
        self.position = (100, HEIGHT - 100)  # Bottom left position
        self.touch_position = None
        self.active = False
        
    def draw(self, screen):
        # Draw base circle
        pygame.draw.circle(screen, (100, 100, 100), self.position, self.radius, 2)
        
        # Draw joystick knob
        if self.active and self.touch_position:
            knob_pos = self.get_constrained_knob_pos()
            pygame.draw.circle(screen, (200, 200, 200), knob_pos, self.radius//2)
        else:
            pygame.draw.circle(screen, (200, 200, 200), self.position, self.radius//2)
    
    def get_constrained_knob_pos(self):
        if not self.touch_position:
            return self.position
            
        dx = self.touch_position[0] - self.position[0]
        dy = self.touch_position[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance <= self.radius:
            return self.touch_position
        else:
            angle = math.atan2(dy, dx)
            x = self.position[0] + math.cos(angle) * self.radius
            y = self.position[1] + math.sin(angle) * self.radius
            return (int(x), int(y))
    
    def get_value(self):
        if not self.active or not self.touch_position:
            return (0, 0)
            
        knob_pos = self.get_constrained_knob_pos()
        dx = knob_pos[0] - self.position[0]
        dy = knob_pos[1] - self.position[1]
        
        # Normalize values between -1 and 1
        return (dx/self.radius, dy/self.radius)

class TouchButton:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.pressed = False
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, screen):
        color = (150, 150, 150) if self.pressed else (100, 100, 100)
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

# Modify the Game class to include touch controls
class Game:
    def __init__(self):
        # ... (existing initialization code) ...
        
        # Add touch controls
        self.joystick = VirtualJoystick()
        self.jump_button = TouchButton(WIDTH - 150, HEIGHT - 150, 100, 100, "Jump")
        self.interact_button = TouchButton(WIDTH - 150, HEIGHT - 270, 100, 100, "Action")
        
    def events(self):
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Handle touch/mouse events
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    # Check joystick
                    if math.dist(pos, self.joystick.position) <= self.joystick.radius:
                        self.joystick.active = True
                        self.joystick.touch_position = pos
                    
                    # Check buttons
                    if self.jump_button.rect.collidepoint(pos):
                        self.jump_button.pressed = True
                        self.player.jump()
                    
                    if self.interact_button.rect.collidepoint(pos):
                        self.interact_button.pressed = True
                        if self.npc.can_interact(self.player):
                            self.npc.show_dialog = True
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.joystick.active = False
                    self.joystick.touch_position = None
                    self.jump_button.pressed = False
                    self.interact_button.pressed = False
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.joystick.active:
                        self.joystick.touch_position = pygame.mouse.get_pos()
            
            # Handle joystick movement
            if self.joystick.active:
                x_value, _ = self.joystick.get_value()
                if x_value < -0.2:
                    self.player.move_left()
                elif x_value > 0.2:
                    self.player.move_right()
            
        except Exception as e:
            print(f"Error in events: {e}")

    def draw(self):
        screen.fill(BLACK)
        self.all_sprites.draw(screen)
        
        # Draw touch controls
        self.joystick.draw(screen)
        self.jump_button.draw(screen)
        self.interact_button.draw(screen)
        
        # ... (rest of the existing draw code) ...

class Game:
    def __init__(self):
        self.running = True
        self.debug_font = pygame.font.Font(None, 36)

        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()

        # Create player
        self.player = Player(self)
        self.all_sprites.add(self.player)

        # Create NPC
        self.npc = NPC(WIDTH // 2, 100, "Rock Head")
        self.all_sprites.add(self.npc)
        self.npcs.add(self.npc)

        # Create some initial blocks for the ground
        self.create_ground()

        # Add touch controls
        self.joystick = VirtualJoystick()
        self.jump_button = TouchButton(WIDTH - 150, HEIGHT - 150, 100, 100, "Jump")
        self.interact_button = TouchButton(WIDTH - 150, HEIGHT - 270, 100, 100, "Action")

    def events(self):
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    elif event.key == pygame.K_ESCAPE:
                        if self.npc.show_dialog:
                            self.npc.show_dialog = False
                            self.npc.show_result = False
                        else:
                            self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if math.dist(pos, self.joystick.position) <= self.joystick.radius:
                        self.joystick.active = True
                        self.joystick.touch_position = pos
                    elif self.jump_button.rect.collidepoint(pos):
                        self.jump_button.pressed = True
                        self.player.jump()
                    elif self.interact_button.rect.collidepoint(pos):
                        self.interact_button.pressed = True
                        if self.npc.can_interact(self.player):
                            self.npc.show_dialog = True
                    elif self.npc.show_dialog:
                        self.npc.handle_click(pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.joystick.active = False
                    self.joystick.touch_position = None
                    self.jump_button.pressed = False
                    self.interact_button.pressed = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.joystick.active:
                        self.joystick.touch_position = pygame.mouse.get_pos()
                    if self.npc.show_dialog:
                        self.npc.handle_hover(pos)

            # Handle joystick movement
            if self.joystick.active:
                x_value, _ = self.joystick.get_value()
                if x_value < -0.2:
                    self.player.move_left()
                elif x_value > 0.2:
                    self.player.move_right()

            # Handle continuous key presses
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move_left()
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move_right()

        except Exception as e:
            print(f"Error in events: {e}")

    def update(self):
        self.all_sprites.update()

    def draw(self):
        screen.fill(BLACK)
        self.all_sprites.draw(screen)

        # Draw touch controls
        self.joystick.draw(screen)
        self.jump_button.draw(screen)
        self.interact_button.draw(screen)

        if self.npc.show_dialog:
            self.npc.draw_dialog(screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.events()
            self.update()
            self.draw()
            pygame.time.Clock().tick(FPS)
            
    def create_ground(self):
        """Create the initial ground blocks"""
        # Create ground blocks
        block_size = 32
        ground_height = HEIGHT - 100  # Height where the ground starts
        
        # Calculate how many blocks we need to fill the width of the screen
        num_blocks = WIDTH // block_size + 1
        
        # Create blocks across the bottom of the screen
        for i in range(num_blocks):
            block = Block(i * block_size, ground_height, block_size)
            self.blocks.add(block)
            self.all_sprites.add(block)
            
        # Add some platforms (optional)
        platform_positions = [
            (WIDTH // 4, HEIGHT - 200),
            (WIDTH // 2, HEIGHT - 300),
            (3 * WIDTH // 4, HEIGHT - 200)
        ]
        
        for x, y in platform_positions:
            # Create a small platform (3 blocks wide)
            for i in range(3):
                block = Block(x + (i * block_size), y, block_size)
                self.blocks.add(block)
                self.all_sprites.add(block)
    def quit(self):
        pygame.quit()
        sys.exit()
# Main game loop
if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()