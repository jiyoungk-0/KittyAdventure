import pygame
import sys
import random
import math

pygame.init()

# Set up display
window_width = 800
window_height = 300
display_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Kitty Adventure")

# Load images using relative paths
background_image = pygame.image.load('assets/background-1.png')
background_image = pygame.transform.scale(background_image, (window_width, window_height))

cat_r_image = pygame.image.load('assets/Cat-2-R(64).png')
cat_r_jump_image = pygame.image.load('assets/Cat-2-Jump-R(64).png')
heart_image = pygame.image.load('assets/heart(2).png')
meat_image = pygame.image.load('assets/meat(2).png')
monster_image = pygame.image.load('assets/monster(2).png')

# Load HP images
hp_images = [
    pygame.image.load('assets/HP-0.png'),
    pygame.image.load('assets/HP-1.png'),
    pygame.image.load('assets/HP-2.png'),
    pygame.image.load('assets/HP-3.png')
]

# Initialize icon position and state
icon_image = cat_r_image
icon_rect = icon_image.get_rect()
icon_rect.x = 100  # Fixed position for the cat
icon_rect.y = window_height - icon_rect.height
icon_speed = 5
icon_jump_speed = 10
is_jumping = False
jump_height = 0
jumping_up = True

# Item movement speed
item_speed = 5

# Background position
background_x = 0

# Define item spawn positions
ground_y = window_height - icon_rect.height
jump_y = window_height - icon_rect.height - 100

# Initialize game variables
meat_count = 0
meat_goal = 3
level = 1
level_display_time = 0  # Time to display level info
level_display_duration = 2000  # Duration to display level info (in milliseconds)
hp = 3  # Player starts with full HP (3)
max_hp = 3  # Max HP

# Function to check proximity for collision detection
def check_proximity(rect1, rect2, threshold):
    distance = math.sqrt((rect1.centerx - rect2.centerx) ** 2 + (rect1.centery - rect2.centery) ** 2)
    return distance <= threshold

# Function to check overlap
def check_overlap(rect1, rects, threshold=0):
    for rect in rects:
        if check_proximity(rect1, rect, threshold):
            return True
    return False

# Function to create random items with fixed heights and non-overlapping X coordinates
def create_random_items(num_items, item_image, existing_rects, all_other_rects):
    items = []
    item_width = item_image.get_width()
    while len(items) < num_items:
        item_rect = item_image.get_rect()
        item_rect.y = random.choice([ground_y, jump_y])
        item_rect.x = random.randint(icon_rect.right + 50, window_width * 2 - item_rect.width)
        item_rect.topleft = (item_rect.x, item_rect.y)

        if not check_overlap(item_rect, existing_rects + all_other_rects, threshold=5):
            items.append(item_rect)
            existing_rects.append(item_rect)
    return items

# Function to replace item when it collides with the cat
def replace_item(item_rect, item_image, existing_rects, all_other_rects):
    new_item = item_image.get_rect()
    new_item.y = random.choice([ground_y, jump_y])
    while True:
        new_item.x = random.randint(icon_rect.right + 50, window_width * 2 - new_item.width)
        if not check_overlap(new_item, existing_rects + all_other_rects, threshold=5):
            break
    if item_rect in existing_rects:
        existing_rects.remove(item_rect)
    existing_rects.append(new_item)
    return new_item

# Function to reset the game
def reset_game():
    global icon_rect, icon_image, background_x, hearts_rects, meats_rects, monsters_rects, hearts, meats, monsters, meat_count, level, item_speed, game_over, level_display_time, hp
    icon_rect.x = 100
    icon_rect.y = window_height - icon_rect.height
    icon_image = cat_r_image
    background_x = 0
    hearts_rects.clear()
    meats_rects.clear()
    monsters_rects.clear()
    meats = create_random_items(2, meat_image, meats_rects, hearts_rects + monsters_rects)
    monsters = create_random_items(1, monster_image, monsters_rects, hearts_rects + meats_rects)  # Spawn 1 monster
    meat_count = 0
    level = 1
    item_speed = 5
    hp = max_hp  # Reset to full HP
    game_over = False
    level_display_time = 0

# Initial items creation
hearts_rects = []  # List to store hearts' positions
meats_rects = []  # List to store meats' positions
monsters_rects = []  # List to store monsters' positions

# Initially create empty hearts if HP is full
hearts = [] if hp == max_hp else create_random_items(1, heart_image, hearts_rects, meats_rects + monsters_rects)

# Initially create meats and monsters
meats = create_random_items(2, meat_image, meats_rects, hearts_rects + monsters_rects)
monsters = create_random_items(1, monster_image, monsters_rects, hearts_rects + meats_rects)

# Set up font
font = pygame.font.Font(None, 36)  # Reset font size
font_small = pygame.font.Font(None, 24)  # Slightly smaller font

# Game state
game_over = False
game_won = False

# Initialize mixer and load background music
pygame.mixer.init()
pygame.mixer.music.load('assets/music/byte-blast-8-bit-arcade-music-background-music-for-video-33-second-208777.mp3')
pygame.mixer.music.play(-1)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if not game_over and not game_won:
        # Handle key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and not is_jumping:
            is_jumping = True
            icon_image = cat_r_jump_image

        # Handle jumping
        if is_jumping:
            if jumping_up:
                icon_rect.y -= icon_jump_speed
                jump_height += icon_jump_speed
                if jump_height >= 100:  # Max jump height
                    jumping_up = False
            else:
                icon_rect.y += icon_jump_speed
                jump_height -= icon_jump_speed
                if jump_height <= 0:
                    is_jumping = False
                    jumping_up = True
                    icon_image = cat_r_image

        # Move background and items to the left automatically
        background_x -= item_speed
        if background_x <= -window_width:
            background_x = 0

        # Generate hearts only if HP is less than max HP and hearts list is empty
        if hp < max_hp and not hearts:
            hearts = create_random_items(1, heart_image, hearts_rects, meats_rects + monsters_rects)

        new_hearts = []
        for heart_rect in hearts:
            heart_rect.x -= item_speed
            if heart_rect.right < 0:  # If item goes off the screen on the left
                heart_rect = replace_item(heart_rect, heart_image, hearts_rects, meats_rects + monsters_rects)
            # Check for collision with the cat
            if check_proximity(icon_rect, heart_rect, 30):
                if hp < max_hp:  # Only increase HP if not already full
                    hp += 1
                heart_rect = replace_item(heart_rect, heart_image, hearts_rects, meats_rects + monsters_rects)
            new_hearts.append(heart_rect)
        hearts = new_hearts

        # Handle meat movement and collision
        new_meats = []
        for meat_rect in meats:
            meat_rect.x -= item_speed
            if meat_rect.right < 0:  # If item goes off the screen on the left
                meat_rect = replace_item(meat_rect, meat_image, meats_rects, hearts_rects + monsters_rects)
            # Check for collision with the cat
            if check_proximity(icon_rect, meat_rect, 30):
                meat_count += 1
                meat_rect = replace_item(meat_rect, meat_image, meats_rects, hearts_rects + monsters_rects)
                if meat_count >= meat_goal:
                    level += 1
                    meat_count = 0
                    item_speed += 1
                    meats = create_random_items(2, meat_image, meats_rects, hearts_rects + monsters_rects)  # Spawn new meats
                    monsters = create_random_items(1, monster_image, monsters_rects, hearts_rects + meats_rects)  # Spawn new monster
                    level_display_time = pygame.time.get_ticks()  # Record the time when the level changed
                    if level > 10:
                        game_won = True  # Set game won flag
                        level_display_time = 0  # Reset level display time to avoid showing level up message
            new_meats.append(meat_rect)
        meats = new_meats

        # Handle monster movement and collision
        new_monsters = []
        for monster_rect in monsters:
            monster_rect.x -= item_speed
            if monster_rect.right < 0:  # If monster goes off the screen on the left
                monster_rect = replace_item(monster_rect, monster_image, monsters_rects, hearts_rects + meats_rects)
            # Check for collision with the cat
            if check_proximity(icon_rect, monster_rect, 30):
                hp -= 1  # Reduce HP when hit by a monster
                if hp <= 0:
                    game_over = True
                monster_rect = replace_item(monster_rect, monster_image, monsters_rects, hearts_rects + meats_rects)
            new_monsters.append(monster_rect)
        monsters = new_monsters

    # Drawing
    display_surface.blit(background_image, (background_x, 0))
    display_surface.blit(background_image, (background_x + window_width, 0))

    for heart_rect in hearts:
        display_surface.blit(heart_image, heart_rect)

    for meat_rect in meats:
        display_surface.blit(meat_image, meat_rect)

    for monster_rect in monsters:
        display_surface.blit(monster_image, monster_rect)

    # Draw icon
    display_surface.blit(icon_image, icon_rect)

    # Draw meat count and level with original font size
    meat_text = font.render(f"Meat: {meat_count}/{meat_goal}", True, (255, 255, 255))
    level_text = font.render(f"Level: {level}", True, (255, 255, 255))
    display_surface.blit(meat_text, (20, 20))
    display_surface.blit(level_text, (20, 60))

    # Draw HP (hearts)
    hp_icon = hp_images[hp]  # Display correct HP icon based on current HP
    display_surface.blit(hp_icon, (window_width - 100, 10))

    # Check if the level up message should still be displayed
    if level_display_time > 0 and pygame.time.get_ticks() - level_display_time <= level_display_duration:
        level_up_text = font.render(f"Level {level}!", True, (255, 255, 255))
        display_surface.blit(level_up_text, (window_width // 2 - level_up_text.get_width() // 2, window_height // 2 - level_up_text.get_height() // 2))

    # If game over, display message
    if game_over:
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        reset_text = font_small.render("Press SPACE to restart", True, (255, 255, 255))
        display_surface.blit(game_over_text, (window_width // 2 - game_over_text.get_width() // 2, window_height // 2 - game_over_text.get_height() // 2))
        display_surface.blit(reset_text, (window_width // 2 - reset_text.get_width() // 2, window_height // 2 + 40))

        # Wait for space key press to reset the game
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            reset_game()
            pygame.mixer.music.stop()  # Stop any existing music
            pygame.mixer.music.play(-1)  # Restart the background music

    # If game won, display message
    if game_won:
        win_text = font.render("You Win!", True, (0, 255, 0))
        reset_text = font_small.render("Press SPACE to restart", True, (255, 255, 255))
        display_surface.blit(win_text, (window_width // 2 - win_text.get_width() // 2, window_height // 2 - win_text.get_height() // 2))
        display_surface.blit(reset_text, (window_width // 2 - reset_text.get_width() // 2, window_height // 2 + 40))

        # Wait for space key press to reset the game
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            reset_game()
            pygame.mixer.music.stop()  # Stop any existing music
            pygame.mixer.music.play(-1)  # Restart the background music

    pygame.display.update()
    pygame.time.Clock().tick(30)

