import pygame
import sys
import os

# Initialize Pygame
print("Initializing Pygame...")
pygame.init()

# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Etch A Sketch - Continuous Fast Drawing Tool")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (0, 200, 100)

# Drawing settings
clock = pygame.time.Clock()
FPS = 60

# Starting position
x = SCREEN_WIDTH // 2
y = SCREEN_HEIGHT // 2
line_width = 3

# Drawing surface
drawing_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
drawing_surface.fill(WHITE)

# Speed (maximum pixel step per frame)
speed = 7

# Joystick positions
left_circle_x = 150
left_circle_y = SCREEN_HEIGHT - 100
right_circle_x = SCREEN_WIDTH - 150
right_circle_y = SCREEN_HEIGHT - 100
circle_radius = 60

# Joystick values
horizontal_value = 0
vertical_value = 0

# Auto mode variables
auto_mode = False
auto_path = []
auto_index = 0


def generate_auto_path(img_surface):
    """Ultra-fast region-based pixel tracking algorithm (O(N) Set Lookup)"""
    print("Analyzing image pixels...")

    pixels = set()
    w, h = img_surface.get_size()

    # Collect dark pixels into a set
    for i in range(w):
        for j in range(h):
            color = img_surface.get_at((i, j))
            if color.r < 200 and color.g < 200 and color.b < 200:
                cx = (SCREEN_WIDTH - w) // 2 + i
                cy = (SCREEN_HEIGHT - 220 - h) // 2 + j
                pixels.add((cx, cy))

    if not pixels:
        print("No drawable dark pixels found!")
        return []

    print(f"Total {len(pixels)} pixels found. Generating optimized path...")

    path = []

    # Start from first pixel
    current = list(pixels)[0]
    pixels.remove(current)
    path.append(current)

    # Greedy nearest-neighbor path construction
    while pixels:
        cx, cy = current
        found = False

        # Search nearby pixels first
        for r in range(1, 15):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) == r or abs(dy) == r:
                        nx, ny = cx + dx, cy + dy
                        if (nx, ny) in pixels:
                            current = (nx, ny)
                            pixels.remove(current)
                            path.append(current)
                            found = True
                            break
                if found:
                    break
            if found:
                break

        # If no nearby pixel found, jump to closest
        if not found:
            min_dist = float('inf')
            closest = None

            for px, py in pixels:
                dist_sq = (px - cx) ** 2 + (py - cy) ** 2
                if dist_sq < min_dist:
                    min_dist = dist_sq
                    closest = (px, py)

            if closest:
                current = closest
                pixels.remove(closest)
                path.append(closest)
            else:
                break

    print("Path generation completed successfully!")
    return path


def draw_joystick(surface, center_x, center_y, radius, value_x, value_y, color):
    """Draw joystick UI"""
    pygame.draw.circle(surface, LIGHT_GRAY, (center_x, center_y), radius, 3)
    inner_x = center_x + value_x * (radius - 15)
    inner_y = center_y + value_y * (radius - 15)
    pygame.draw.circle(surface, color, (int(inner_x), int(inner_y)), 20)


def get_joystick_input(mouse_x, mouse_y, center_x, center_y, radius):
    """Get manual joystick input"""
    dx = mouse_x - center_x
    dy = mouse_y - center_y
    distance = (dx**2 + dy**2) ** 0.5

    if distance < radius:
        if distance > 0:
            value_x = dx / radius
            value_y = dy / radius
        else:
            value_x = 0
            value_y = 0
        return value_x, value_y

    return 0, 0


print("Window opened. Starting main loop...")

# Main loop
running = True
while running:
    clock.tick(FPS)

    screen.fill(WHITE)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_c:
                # Clear canvas
                drawing_surface.fill(WHITE)
                x = SCREEN_WIDTH // 2
                y = SCREEN_HEIGHT // 2
                auto_mode = False
                print("Canvas cleared.")

            if event.key == pygame.K_q:
                # Quit
                running = False

            if event.key == pygame.K_a:
                # Auto draw mode
                if os.path.exists("monalisa.png"):
                    try:
                        img = pygame.image.load("monalisa.png")

                        max_size = 400
                        img_w, img_h = img.get_size()

                        if img_w > max_size or img_h > max_size:
                            scale = min(max_size / img_w, max_size / img_h)
                            img = pygame.transform.scale(
                                img,
                                (int(img_w * scale), int(img_h * scale))
                            )

                        auto_path = generate_auto_path(img)

                        if auto_path:
                            drawing_surface.fill(WHITE)
                            x, y = auto_path[0]
                            auto_index = 0
                            auto_mode = True

                    except Exception as e:
                        print(f"Error loading image: {e}")

                else:
                    print("Error: 'monalisa.png' not found in directory!")

    # Drawing logic
    if auto_mode:
        if auto_index >= len(auto_path):
            auto_mode = False
            horizontal_value = 0
            vertical_value = 0
            print("Auto drawing completed!")
        else:
            steps_moved = 0

            while steps_moved < speed and auto_index < len(auto_path):
                target_x, target_y = auto_path[auto_index]
                dx = target_x - x
                dy = target_y - y
                dist = (dx**2 + dy**2) ** 0.5

                if dist == 0:
                    auto_index += 1
                    continue

                allowed_dist = speed - steps_moved

                if dist <= allowed_dist:
                    old_pos = (int(x), int(y))
                    x, y = target_x, target_y
                    pygame.draw.line(drawing_surface, BLACK, old_pos, (int(x), int(y)), line_width)
                    steps_moved += dist
                    auto_index += 1
                else:
                    ratio = allowed_dist / dist
                    old_pos = (int(x), int(y))
                    x += dx * ratio
                    y += dy * ratio
                    pygame.draw.line(drawing_surface, BLACK, old_pos, (int(x), int(y)), line_width)
                    steps_moved += allowed_dist

            if auto_index < len(auto_path):
                nxt_x, nxt_y = auto_path[auto_index]
                tdx, tdy = nxt_x - x, nxt_y - y
                tdist = (tdx**2 + tdy**2) ** 0.5
                if tdist > 0:
                    horizontal_value = tdx / tdist
                    vertical_value = tdy / tdist

    else:
        # Manual left joystick
        if mouse_pressed:
            dist_to_left = ((mouse_x - left_circle_x)**2 + (mouse_y - left_circle_y)**2)**0.5
            if dist_to_left < circle_radius:
                horizontal_value, _ = get_joystick_input(
                    mouse_x, mouse_y,
                    left_circle_x, left_circle_y,
                    circle_radius
                )
            else:
                horizontal_value = 0
        else:
            horizontal_value = 0

        # Manual right joystick
        if mouse_pressed:
            dist_to_right = ((mouse_x - right_circle_x)**2 + (mouse_y - right_circle_y)**2)**0.5
            if dist_to_right < circle_radius:
                _, vertical_value = get_joystick_input(
                    mouse_x, mouse_y,
                    right_circle_x, right_circle_y,
                    circle_radius
                )
            else:
                vertical_value = 0
        else:
            vertical_value = 0

        old_x, old_y = x, y
        x += horizontal_value * speed
        y += vertical_value * speed

        x = max(0, min(x, SCREEN_WIDTH - 1))
        y = max(0, min(y, SCREEN_HEIGHT - 1))

        if (old_x, old_y) != (x, y):
            pygame.draw.line(
                drawing_surface,
                BLACK,
                (int(old_x), int(old_y)),
                (int(x), int(y)),
                line_width
            )

    # Render drawing surface
    screen.blit(drawing_surface, (0, 0))

    # UI
    draw_joystick(screen, left_circle_x, left_circle_y, circle_radius, horizontal_value, 0, BLUE)
    draw_joystick(screen, right_circle_x, right_circle_y, circle_radius, 0, vertical_value, RED)

    pygame.draw.circle(screen, BLACK, (int(x), int(y)), 6)
    pygame.draw.circle(screen, WHITE, (int(x), int(y)), 4)

    font_small = pygame.font.Font(None, 20)
    font_large = pygame.font.Font(None, 24)

    label_left = font_small.render("Left-Right", True, BLUE)
    label_right = font_small.render("Up-Down", True, RED)

    screen.blit(label_left, (left_circle_x - 40, left_circle_y + circle_radius + 10))
    screen.blit(label_right, (right_circle_x - 60, right_circle_y + circle_radius + 10))

    instructions = font_small.render(
        "C: Clear | Q: Quit | A: Auto Draw (monalisa.png)",
        True,
        BLACK
    )
    screen.blit(instructions, (SCREEN_WIDTH // 2 - 150, 20))

    if auto_mode and len(auto_path) > 0:
        progress = int((auto_index / len(auto_path)) * 100)
        status_text = font_large.render(
            f"AUTO MODE ACTIVE (%{progress})",
            True,
            GREEN
        )
        screen.blit(status_text, (SCREEN_WIDTH // 2 - 120, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()