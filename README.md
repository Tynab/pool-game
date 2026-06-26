# 🎱 Pool Game

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.x-00D162?logo=pygame)](https://www.pygame.org/)
[![Pymunk](https://img.shields.io/badge/Pymunk-Physics-FF6B35)](http://www.pymunk.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Trò chơi **Bi-a 2D** mô phỏng vật lý thực tế, xây dựng bằng **Python** với **Pygame** (render đồ họa) và **Pymunk** (engine vật lý rigid-body). Người chơi sử dụng chuột để điều khiển cơ bi-a, tích lực bằng cách giữ chuột, và đánh tất cả 15 bi màu vào lỗ trước khi hết mạng.

## 📸 Demo

<p align="center">
<img src="pic/0.jpg" alt="Pool Game Demo">
</p>

## 🏗️ Kiến trúc kỹ thuật

### Hằng số cấu hình

| Nhóm | Hằng số | Giá trị | Mô tả |
|------|---------|---------|-------|
| Cửa sổ | `SCREEN_WIDTH × SCREEN_HEIGHT` | 1200 × 678 | Kích thước bàn bi-a (pixel) |
| Bi | `BALL_COUNT` | 16 | 15 bi màu + 1 bi trắng |
| Bi | `BALL_MASS` / `BALL_ELASTICITY` | 5 / 0.8 | Khối lượng & đàn hồi |
| Bàn | `FRICTION` | 1000 | Ma sát mô phỏng qua PivotJoint |
| Bàn | `CUSHION_ELASTICITY` | 0.6 | Đàn hồi thành bàn |
| Bắn | `MAX_FORCE` / `FORCE_STEP` | 10000 / 100 | Lực tối đa & bước tăng mỗi frame |
| FPS | `FPS` | 120 | Tốc độ khung hình |

### Engine vật lý (Pymunk)

- **Không gian (Space)**: Quản lý toàn bộ thân vật lý, shape, và joint.
- **Bi (Ball)**: `pymunk.Circle` gắn với `pymunk.Body` — có khối lượng, đàn hồi.
- **Ma sát lăn**: Mô phỏng bằng `PivotJoint` với `max_force` giới hạn, `max_bias = 0`.
- **Thành bàn (Cushion)**: `pymunk.Poly` tĩnh (`STATIC body`) — 6 polygon.
- **Lỗ bi (Pocket)**: Kiểm tra khoảng cách Euclid (`math.dist`) giữa bi và tâm lỗ.

### Các class & hàm chính

| Thành phần | Loại | Mô tả |
|------------|------|-------|
| `Cue` | Class | Cơ bi-a — xoay theo hướng chuột, vẽ bằng `pygame.transform.rotate` |
| `create_ball()` | Function | Tạo bi vật lý: Body + Circle + PivotJoint (ma sát) |
| `create_cushion()` | Function | Tạo thành bàn tĩnh từ tọa độ polygon |
| `draw_text()` | Function | Render text lên surface tại tọa độ (x, y) |
| `main()` | Function | Hàm chính — khởi tạo, game loop, xử lý sự kiện |

### Game Loop

```
┌─────────────────────────────────────────────┐
│  clock.tick(FPS)  →  space.step(1/FPS)      │
│                                             │
│  1. Vẽ nền + bàn                            │
│  2. Kiểm tra bi vào lỗ (gom → xóa an toàn) │
│  3. Vẽ các bi                               │
│  4. Kiểm tra bi đã dừng → cho phép bắn     │
│  5. Vẽ cơ + tính góc theo chuột            │
│  6. Tích lực / bắn xung lực                │
│  7. Vẽ panel dưới (bi đã vào lỗ + mạng)    │
│  8. Kiểm tra thắng/thua                    │
│  9. Xử lý sự kiện (chuột, thoát)           │
│ 10. pygame.display.update()                 │
└─────────────────────────────────────────────┘
```

## 📁 Cấu trúc dự án

```
Pool Game/
├── main.py                  # Source code chính
├── requirements.txt         # Thư viện phụ thuộc
├── Pool Game.sln            # Visual Studio Solution
├── Pool Game.pyproj         # Visual Studio Python Project
├── assets/
│   └── images/
│       ├── table.png        # Ảnh bàn bi-a
│       ├── cue.png          # Ảnh cơ bi-a
│       ├── ball_1.png       # Bi số 1
│       ├── ...              # Bi số 2–15
│       └── ball_16.png      # Bi trắng (cue ball)
├── pic/
│   └── 0.jpg                # Ảnh demo cho README
├── .github/
│   ├── FUNDING.yml          # Cấu hình sponsor
│   └── workflows/
│       └── deploy-pygame.yml # CI/CD build WebAssembly (Pygbag)
├── .gitattributes           # Git LFS tracking
└── .gitignore               # Ignore rules
```

## 🚀 Cài đặt & Chạy

### Yêu cầu
- Python 3.11+
- pip

### Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Chạy game

```bash
python main.py
```

## 🎮 Điều khiển

| Thao tác | Hành động |
|----------|-----------|
| **Di chuột** | Xoay cơ bi-a theo hướng chuột |
| **Giữ chuột trái** | Tích lực (thanh đỏ dao động) |
| **Thả chuột trái** | Bắn bi trắng theo hướng cơ |
| **Đóng cửa sổ** | Thoát game |

## 📜 Luật chơi

- Bạn có **3 mạng**. Mỗi lần bi trắng rơi vào lỗ sẽ mất 1 mạng.
- Đánh hết **15 bi màu** vào lỗ để **thắng**.
- Hết mạng → **GAME OVER**.

## 💖 Sponsor

- [GitHub Sponsors](https://github.com/sponsors/tynab)
- [Patreon](https://patreon.com/yamiannephilim)
- [PayPal](https://paypal.me/yamiannephilim)
