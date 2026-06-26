"""
Pool Game — Trò chơi Bi-a 2D mô phỏng vật lý.

Sử dụng Pygame để render đồ họa và Pymunk làm engine vật lý 2D (rigid-body).
Người chơi điều khiển cơ bi-a bằng chuột, tích lực bằng cách giữ chuột,
và cố gắng đánh hết tất cả các bi vào lỗ trước khi hết mạng.

Thư viện:
    - pygame: Render đồ họa, xử lý sự kiện, quản lý vòng lặp game.
    - pymunk: Mô phỏng vật lý 2D (va chạm, ma sát, đàn hồi).
"""

import math
import sys

import pygame
import pymunk
import pymunk.pygame_util

# ============================================================================
# HẰNG SỐ CẤU HÌNH
# ============================================================================

# --- Cửa sổ & giao diện ---
TITLE = "Pool Game"
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 678
BOTTOM_PANEL = 50
BACKGROUND_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)

# --- Thông số bi ---
BALL_COUNT = 16  # Tổng số bi (15 bi màu + 1 bi trắng)
BALL_MASS = 5  # Khối lượng mỗi bi (đơn vị Pymunk)
BALL_ELASTICITY = 0.8  # Hệ số đàn hồi khi va chạm
BALL_DIAMETER = 36  # Đường kính bi (pixel)
BALL_RADIUS = BALL_DIAMETER / 2  # Bán kính bi (pixel)

# --- Thông số bàn (tường & lỗ) ---
FRICTION = 1000  # Lực ma sát mô phỏng qua PivotJoint
CUSHION_ELASTICITY = 0.6  # Hệ số đàn hồi của thành bàn
POCKET_DIAMETER = 70  # Đường kính lỗ bi (pixel)

# --- Thông số bắn ---
MAX_FORCE = 10000  # Lực bắn tối đa
FORCE_STEP = 100  # Bước tăng lực mỗi frame khi giữ chuột

# --- Thanh lực (power bar) ---
BAR_WIDTH = 10  # Chiều rộng mỗi ô thanh lực (pixel)
BAR_HEIGHT = 20  # Chiều cao mỗi ô thanh lực (pixel)
BAR_SENSITIVITY = 1000  # Số lực cần cho mỗi ô hiển thị
BAR_COLOR = (255, 0, 0)  # Màu thanh lực (đỏ)

# --- Vị trí bi trắng ---
CUE_BALL_X = 888  # Tọa độ X đặt bi trắng (bên phải bàn)

# --- Vị trí xếp tam giác bi ---
RACK_START_X = 250  # Tọa độ X bắt đầu xếp tam giác
RACK_START_Y = 267  # Tọa độ Y bắt đầu xếp tam giác

# --- Vị trí ngoài màn hình (khi bi rơi vào lỗ) ---
OFFSCREEN_POS = (-444, -444)

# --- Thanh lực: offset hiển thị so với bi trắng ---
POWER_BAR_OFFSET_X = 70  # Khoảng cách ngang từ bi trắng đến thanh lực
POWER_BAR_OFFSET_Y = 30  # Khoảng cách dọc từ bi trắng đến thanh lực
POWER_BAR_SPACING = 15  # Khoảng cách giữa các ô thanh lực

# --- Panel dưới: hiển thị bi đã vào lỗ ---
POTTED_BALL_X_START = 10  # Tọa độ X bắt đầu vẽ bi đã vào lỗ
POTTED_BALL_SPACING = 50  # Khoảng cách giữa các bi đã vào lỗ
POTTED_BALL_Y_OFFSET = 10  # Khoảng cách dọc từ đường kẻ panel

# --- Vị trí text ---
LIVES_TEXT_X_OFFSET = 200  # Khoảng cách từ cạnh phải cho text "LIVES"
LIVES_TEXT_Y_OFFSET = 10  # Khoảng cách dọc từ đường kẻ panel
GAMEOVER_X_OFFSET = 160  # Offset X từ tâm cho text "GAME OVER"/"YOU WIN"
GAMEOVER_Y_OFFSET = 100  # Offset Y từ tâm cho text "GAME OVER"/"YOU WIN"

# --- Tọa độ 6 lỗ bi trên bàn (x, y) ---
POCKETS = [
    (55, 63), (592, 48), (1134, 64),  # 3 lỗ phía trên
    (55, 616), (592, 629), (1134, 616),  # 3 lỗ phía dưới
]

# --- Tọa độ đỉnh của 6 thành bàn (polygon) ---
CUSHIONS = [
    [(88, 56), (109, 77), (555, 77), (564, 56)],  # Thành trên-trái
    [(621, 56), (630, 77), (1081, 77), (1102, 56)],  # Thành trên-phải
    [(89, 621), (110, 600), (556, 600), (564, 621)],  # Thành dưới-trái
    [(622, 621), (630, 600), (1081, 600), (1102, 621)],  # Thành dưới-phải
    [(56, 96), (77, 117), (77, 560), (56, 581)],  # Thành trái
    [(1143, 96), (1122, 117), (1122, 560), (1143, 581)],  # Thành phải
]

# --- Tốc độ khung hình ---
FPS = 120


# ============================================================================
# HÀM TIỆN ÍCH
# ============================================================================


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    x: float,
    y: float,
) -> None:
    """Vẽ chuỗi text lên bề mặt tại tọa độ (x, y).

    Args:
        surface: Bề mặt Pygame để vẽ lên.
        text: Nội dung chuỗi cần hiển thị.
        font: Font chữ sử dụng.
        color: Màu chữ dạng RGB tuple.
        x: Tọa độ X góc trên-trái của text.
        y: Tọa độ Y góc trên-trái của text.
    """
    surface.blit(font.render(text, True, color), (x, y))


def create_ball(
    space: pymunk.Space,
    static_body: pymunk.Body,
    radius: float,
    pos: tuple[float, float],
) -> pymunk.Circle:
    """Tạo một bi vật lý trong không gian Pymunk.

    Mỗi bi gồm:
        - Body: thân vật lý có vị trí và vận tốc.
        - Circle shape: hình tròn với bán kính, khối lượng, đàn hồi.
        - PivotJoint: khớp nối giả để mô phỏng ma sát lăn.

    Args:
        space: Không gian vật lý Pymunk.
        static_body: Thân tĩnh của space, dùng làm neo cho PivotJoint.
        radius: Bán kính bi (pixel).
        pos: Vị trí ban đầu (x, y).

    Returns:
        Shape hình tròn (pymunk.Circle) đại diện cho bi.
    """
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.mass = BALL_MASS
    shape.elasticity = BALL_ELASTICITY
    # Dùng PivotJoint để mô phỏng ma sát lăn trên mặt bàn
    pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
    pivot.max_bias = 0  # Tắt tự hiệu chỉnh vị trí của joint
    pivot.max_force = FRICTION  # Giới hạn lực = mô phỏng ma sát tuyến tính
    space.add(body, shape, pivot)
    return shape


def create_cushion(
    space: pymunk.Space,
    poly_dims: list[tuple[int, int]],
) -> None:
    """Tạo một thành bàn (cushion) tĩnh trong không gian vật lý.

    Args:
        space: Không gian vật lý Pymunk.
        poly_dims: Danh sách tọa độ đỉnh polygon của thành bàn.
    """
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Poly(body, poly_dims)
    shape.elasticity = CUSHION_ELASTICITY
    space.add(body, shape)


class Cue:
    """Cơ bi-a — hiển thị và xoay theo hướng chuột.

    Attributes:
        original_image: Ảnh gốc của cơ (không xoay).
        angle: Góc xoay hiện tại (độ).
        image: Ảnh đã xoay theo góc hiện tại.
        rect: Hình chữ nhật bao quanh ảnh, dùng để định vị.
    """

    def __init__(self, image: pygame.Surface, pos: tuple[float, float]) -> None:
        """Khởi tạo cơ bi-a tại vị trí cho trước.

        Args:
            image: Ảnh gốc của cơ bi-a.
            pos: Vị trí tâm ban đầu (x, y).
        """
        self.original_image = image
        self.angle = 0.0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self, angle: float) -> None:
        """Cập nhật góc xoay của cơ.

        Args:
            angle: Góc mới (độ), tính từ trục X dương ngược chiều kim đồng hồ.
        """
        self.angle = angle

    def draw(self, surface: pygame.Surface) -> None:
        """Vẽ cơ bi-a lên bề mặt, xoay quanh tâm rect.

        Args:
            surface: Bề mặt Pygame để vẽ lên.
        """
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(
            self.image,
            (
                self.rect.centerx - self.image.get_width() / 2,
                self.rect.centery - self.image.get_height() / 2,
            ),
        )


# ============================================================================
# HÀM CHÍNH
# ============================================================================


def main() -> None:
    """Hàm chính — khởi tạo game và chạy vòng lặp chính.

    Luồng thực thi:
        1. Khởi tạo Pygame, Pymunk, tải tài nguyên.
        2. Tạo các bi, thành bàn, cơ bi-a.
        3. Vòng lặp game: xử lý sự kiện → cập nhật vật lý → vẽ → hiển thị.
        4. Thoát khi người chơi đóng cửa sổ.
    """
    # --- Khởi tạo Pygame ---
    pygame.init()
    font = pygame.font.SysFont("Lato", 30)
    large_font = pygame.font.SysFont("Lato", 60)
    clock = pygame.time.Clock()

    # --- Tạo cửa sổ game ---
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + BOTTOM_PANEL))
    pygame.display.set_caption(TITLE)

    # --- Khởi tạo không gian vật lý Pymunk ---
    space = pymunk.Space()
    static_body = space.static_body

    # --- Biến trạng thái game ---
    lives = 3  # Số mạng còn lại
    force = 0  # Lực bắn hiện tại
    force_direction = 1  # Hướng tăng/giảm lực (+1 tăng, -1 giảm)
    game_running = True  # Game đang chạy (chưa thua/thắng)
    cue_ball_potted = False  # Bi trắng vừa rơi vào lỗ
    taking_shot = True  # Đang ở trạng thái chờ bắn
    powering_up = False  # Đang giữ chuột tích lực
    potted_balls = []  # Danh sách ảnh bi đã vào lỗ (hiển thị ở panel dưới)
    cue_angle = 0.0  # Góc cơ bi-a (khởi tạo tránh lỗi tham chiếu)

    # --- Tải hình ảnh ---
    cue_image = pygame.image.load("assets/images/cue.png").convert_alpha()
    table_image = pygame.image.load("assets/images/table.png").convert_alpha()
    ball_images = [
        pygame.image.load(f"assets/images/ball_{i}.png").convert_alpha()
        for i in range(1, BALL_COUNT + 1)
    ]

    # --- Tạo các bi trên bàn ---
    balls = []
    rows = 5
    # Xếp 15 bi màu theo hình tam giác (5 cột, số hàng giảm dần)
    for col in range(5):
        for row in range(rows):
            pos = (
                RACK_START_X + col * (BALL_DIAMETER + 1),
                RACK_START_Y + row * (BALL_DIAMETER + 1) + col * BALL_RADIUS,
            )
            balls.append(create_ball(space, static_body, BALL_RADIUS, pos))
        rows -= 1

    # Bi trắng (luôn ở cuối danh sách balls)
    cue_ball_pos = (CUE_BALL_X, SCREEN_HEIGHT / 2)
    cue_ball = create_ball(space, static_body, BALL_RADIUS, cue_ball_pos)
    balls.append(cue_ball)

    # --- Tạo 6 thành bàn ---
    for cushion_vertices in CUSHIONS:
        create_cushion(space, cushion_vertices)

    # --- Tạo cơ bi-a ---
    cue = Cue(cue_image, balls[-1].body.position)

    # --- Tạo thanh lực (power bar) ---
    power_bar = pygame.Surface((BAR_WIDTH, BAR_HEIGHT))
    power_bar.fill(BAR_COLOR)

    # ========================================================================
    # VÒNG LẶP CHÍNH
    # ========================================================================
    game_on = True

    while game_on:
        clock.tick(FPS)
        space.step(1 / FPS)

        # --- Vẽ nền và bàn bi-a ---
        screen.fill(BACKGROUND_COLOR)
        screen.blit(table_image, (0, 0))

        # --- Kiểm tra bi rơi vào lỗ ---
        # Gom các bi cần xóa để tránh lỗi khi sửa list đang duyệt
        balls_to_remove = []
        for i, ball in enumerate(balls):
            for pocket in POCKETS:
                ball_pos = ball.body.position
                distance = math.dist((ball_pos[0], ball_pos[1]), pocket)
                if distance <= POCKET_DIAMETER / 2:
                    if i == len(balls) - 1:
                        # Bi trắng rơi vào lỗ → mất mạng, đặt ra ngoài tạm
                        lives -= 1
                        cue_ball_potted = True
                        ball.body.position = OFFSCREEN_POS
                        ball.body.velocity = (0.0, 0.0)
                    else:
                        # Bi màu rơi vào lỗ → đánh dấu cần xóa
                        balls_to_remove.append(i)
                        ball.body.position = OFFSCREEN_POS
                        ball.body.velocity = (0.0, 0.0)
                    break  # Mỗi bi chỉ rơi vào 1 lỗ

        # Xóa bi từ index lớn → nhỏ để không bị lệch index
        for idx in sorted(balls_to_remove, reverse=True):
            removed_ball = balls.pop(idx)
            space.remove(removed_ball.body)
            potted_balls.append(ball_images.pop(idx))

        # --- Vẽ các bi trên bàn ---
        for i, ball in enumerate(balls):
            screen.blit(
                ball_images[i],
                (ball.body.position[0] - ball.radius, ball.body.position[1] - ball.radius),
            )

        # --- Kiểm tra tất cả bi đã dừng chưa ---
        taking_shot = True
        for ball in balls:
            if int(ball.body.velocity[0]) != 0 or int(ball.body.velocity[1]) != 0:
                taking_shot = False
                break

        # --- Vẽ cơ bi-a khi đang chờ bắn ---
        if taking_shot and game_running:
            if cue_ball_potted:
                # Đặt lại bi trắng về vị trí ban đầu
                balls[-1].body.position = (CUE_BALL_X, SCREEN_HEIGHT / 2)
                cue_ball_potted = False
            # Tính góc cơ theo hướng chuột
            mouse_pos = pygame.mouse.get_pos()
            cue.rect.center = balls[-1].body.position
            cue_ball_pos_current = balls[-1].body.position
            cue_angle = math.degrees(
                math.atan2(
                    -(cue_ball_pos_current[1] - mouse_pos[1]),
                    cue_ball_pos_current[0] - mouse_pos[0],
                )
            )
            cue.update(cue_angle)
            cue.draw(screen)

        # --- Tích lực hoặc bắn ---
        if powering_up and game_running:
            # Đang giữ chuột → tăng/giảm lực theo hướng dao động
            force += FORCE_STEP * force_direction
            if force >= MAX_FORCE or force <= 0:
                force_direction *= -1
            # Vẽ các ô thanh lực
            for bar_idx in range(math.ceil(force / BAR_SENSITIVITY)):
                screen.blit(
                    power_bar,
                    (
                        balls[-1].body.position[0] - POWER_BAR_OFFSET_X + bar_idx * POWER_BAR_SPACING,
                        balls[-1].body.position[1] + POWER_BAR_OFFSET_Y,
                    ),
                )
        elif not powering_up and taking_shot:
            # Vừa thả chuột → áp dụng xung lực lên bi trắng
            impulse_x = force * -math.cos(math.radians(cue_angle))
            impulse_y = force * math.sin(math.radians(cue_angle))
            balls[-1].body.apply_impulse_at_local_point((impulse_x, impulse_y), (0, 0))
            force = 0
            force_direction = 1

        # --- Vẽ panel dưới ---
        pygame.draw.rect(
            screen, BACKGROUND_COLOR, (0, SCREEN_HEIGHT, SCREEN_WIDTH, BOTTOM_PANEL)
        )

        # Vẽ các bi đã vào lỗ ở panel dưới
        for i, ball_img in enumerate(potted_balls):
            screen.blit(
                ball_img,
                (POTTED_BALL_X_START + i * POTTED_BALL_SPACING, SCREEN_HEIGHT + POTTED_BALL_Y_OFFSET),
            )

        # Hiển thị số mạng còn lại
        draw_text(
            screen,
            f"LIVES: {lives}",
            font,
            TEXT_COLOR,
            SCREEN_WIDTH - LIVES_TEXT_X_OFFSET,
            SCREEN_HEIGHT + LIVES_TEXT_Y_OFFSET,
        )

        # --- Kiểm tra thua ---
        if lives <= 0:
            draw_text(
                screen,
                "GAME OVER",
                large_font,
                TEXT_COLOR,
                SCREEN_WIDTH / 2 - GAMEOVER_X_OFFSET,
                SCREEN_HEIGHT / 2 - GAMEOVER_Y_OFFSET,
            )
            game_running = False

        # --- Kiểm tra thắng (chỉ còn bi trắng) ---
        if len(balls) == 1:
            draw_text(
                screen,
                "YOU WIN",
                large_font,
                TEXT_COLOR,
                SCREEN_WIDTH / 2 - GAMEOVER_X_OFFSET,
                SCREEN_HEIGHT / 2 - GAMEOVER_Y_OFFSET,
            )
            game_running = False

        # --- Xử lý sự kiện ---
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and taking_shot:
                powering_up = True
            if event.type == pygame.MOUSEBUTTONUP and taking_shot:
                powering_up = False
            if event.type == pygame.QUIT:
                game_on = False

        pygame.display.update()

    pygame.quit()
    sys.exit()


# ============================================================================
# ĐIỂM VÀO CHƯƠNG TRÌNH
# ============================================================================

if __name__ == "__main__":
    main()
