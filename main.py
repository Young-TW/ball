import pygame
import sys
import math
import random

# 初始化 pygame
pygame.init()

# 視窗大小設定
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("小球模擬")

# 顏色定義 (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)

# 圓形參數
circle_center = (WIDTH // 2, HEIGHT // 2)
circle_radius = 250  # 圓形半徑

# 小球參數
ball_radius = 10
num_balls = 10  # 小球數量

# 初始化小球位置和速度
balls = []
init_speed = 10
for _ in range(num_balls):
    angle = random.uniform(0, 2 * math.pi)
    ball_pos = [circle_center[0] + random.uniform(-10, 10), circle_center[1] + random.uniform(-10, 10)]
    ball_velocity = [init_speed * math.cos(angle), init_speed * math.sin(angle)]
    balls.append({'pos': ball_pos, 'velocity': ball_velocity})

# 重力設定
gravity_magnitude = 0.15  # 重力加速度大小（單位：像素/幀²）
# 初始重力方向向量 (垂直向下)
tilt = [0, 1]

# 恢復係數（0 < restitution <= 1），值越小表示碰撞後能量流失越多
restitution = 0.995

# 建立時鐘以控制更新速度
clock = pygame.time.Clock()

while True:
    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 讀取鍵盤狀態，利用 WASD 控制平面傾斜方向，從而改變重力作用方向
    keys = pygame.key.get_pressed()
    # 每次調整傾斜向量的步伐（可依需求調整靈敏度）
    tilt_step = 0.005
    if keys[pygame.K_w]:
        tilt[1] -= tilt_step
    if keys[pygame.K_s]:
        tilt[1] += tilt_step
    if keys[pygame.K_a]:
        tilt[0] -= tilt_step
    if keys[pygame.K_d]:
        tilt[0] += tilt_step
    # 正規化傾斜向量，確保重力大小不變
    norm = math.sqrt(tilt[0]**2 + tilt[1]**2)
    if norm != 0:
        tilt[0] /= norm
        tilt[1] /= norm

    # 計算有效重力向量（方向由 tilt 決定，大小固定為 gravity_magnitude）
    effective_gravity = (gravity_magnitude * tilt[0], gravity_magnitude * tilt[1])

    # 更新每個小球的位置和速度
    for ball in balls:
        ball_pos = ball['pos']
        ball_velocity = ball['velocity']

        # 加上有效重力到小球速度中
        ball_velocity[0] += effective_gravity[0]
        ball_velocity[1] += effective_gravity[1]

        # 更新小球位置
        ball_pos[0] += ball_velocity[0]
        ball_pos[1] += ball_velocity[1]

        # 計算小球中心與圓心的距離
        dx = ball_pos[0] - circle_center[0]
        dy = ball_pos[1] - circle_center[1]
        distance = math.sqrt(dx**2 + dy**2)

        # 碰撞檢測：若小球碰到圓形邊界（考慮小球半徑）
        if distance + ball_radius > circle_radius:
            # 播放音效 (注意：若音效檔案找不到會報錯)
            pygame.mixer.Sound("boing.opus").play()
            # 計算從圓心指向小球的單位法向量
            if distance != 0:
                normal = [dx / distance, dy / distance]
            else:
                normal = [1, 0]  # 避免除以 0 的情況

            # 利用反射公式計算不完全彈性碰撞
            # 公式：v' = v - (1 + restitution) * (v · n) * n
            v_dot_n = ball_velocity[0] * normal[0] + ball_velocity[1] * normal[1]
            ball_velocity[0] = ball_velocity[0] - (1 + restitution) * v_dot_n * normal[0]
            ball_velocity[1] = ball_velocity[1] - (1 + restitution) * v_dot_n * normal[1]

            # 當小球超出邊界時，調整回邊界內
            overlap = (distance + ball_radius) - circle_radius
            ball_pos[0] -= overlap * normal[0]
            ball_pos[1] -= overlap * normal[1]

    # 檢查小球之間的碰撞
    for i in range(num_balls):
        for j in range(i + 1, num_balls):
            ball1 = balls[i]
            ball2 = balls[j]
            dx = ball1['pos'][0] - ball2['pos'][0]
            dy = ball1['pos'][1] - ball2['pos'][1]
            distance = math.sqrt(dx**2 + dy**2)

            if distance < 2 * ball_radius:
                # 播放音效 (注意：若音效檔案找不到會報錯)
                pygame.mixer.Sound("boing.opus").play()
                # 計算從 ball2 指向 ball1 的單位法向量
                if distance != 0:
                    normal = [dx / distance, dy / distance]
                else:
                    normal = [1, 0]  # 避免除以 0 的情況

                # 利用反射公式計算不完全彈性碰撞
                # 公式：v' = v - (1 + restitution) * (v · n) * n
                v1_dot_n = ball1['velocity'][0] * normal[0] + ball1['velocity'][1] * normal[1]
                v2_dot_n = ball2['velocity'][0] * normal[0] + ball2['velocity'][1] * normal[1]

                ball1['velocity'][0] = ball1['velocity'][0] - (1 + restitution) * v1_dot_n * normal[0]
                ball1['velocity'][1] = ball1['velocity'][1] - (1 + restitution) * v1_dot_n * normal[1]
                ball2['velocity'][0] = ball2['velocity'][0] - (1 + restitution) * v2_dot_n * normal[0]
                ball2['velocity'][1] = ball2['velocity'][1] - (1 + restitution) * v2_dot_n * normal[1]

                # 當小球重疊時，調整回不重疊狀態
                overlap = 2 * ball_radius - distance
                ball1['pos'][0] += overlap * normal[0] / 2
                ball1['pos'][1] += overlap * normal[1] / 2
                ball2['pos'][0] -= overlap * normal[0] / 2
                ball2['pos'][1] -= overlap * normal[1] / 2

    # 繪製部分
    screen.fill(BLACK)  # 清除畫面
    # 畫出圓形邊界 (線寬 2 像素)
    pygame.draw.circle(screen, WHITE, circle_center, circle_radius, 2)
    # 畫出所有小球
    for ball in balls:
        pygame.draw.circle(screen, RED, (int(ball['pos'][0]), int(ball['pos'][1])), ball_radius)

    # （可選）在畫面上顯示目前有效重力向量，方便觀察效果
    font = pygame.font.SysFont(None, 24)
    gravity_text = font.render(f"Gravity: ({effective_gravity[0]:.3f}, {effective_gravity[1]:.3f})", True, WHITE)
    screen.blit(gravity_text, (10, 10))

    # 更新螢幕顯示
    pygame.display.flip()
    # 控制更新頻率
    clock.tick(60)
