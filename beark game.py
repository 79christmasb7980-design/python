#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 블럭깨기(브릭 브레이커) 게임
키/마우스로 패들을 조작하여 공으로 블럭을 깨세요.

의존성: pygame

기본 조작:
  좌/우 화살표 또는 A/D로 패들 이동
  마우스 이동으로 패들 제어 가능
  스페이스바로 게임 시작/재시작

작성: 자동 생성 코드 (예제)
"""

import urllib.request
import os
from io import BytesIO
from PIL import Image
import sys
try:
	import pygame
except Exception as e:
	print("pygame 모듈을 불러올 수 없습니다. 먼저 'pip install pygame'로 설치하세요.")
	raise

from pygame import Rect
import random

# 화면 설정
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
RED = (200, 30, 30)
GREEN = (30, 180, 30)
BLUE = (30, 100, 240)
YELLOW = (240, 200, 30)


class Paddle:
	def __init__(self, w=160, h=16):
		self.w = w
		self.h = h
		self.rect = Rect((SCREEN_WIDTH - w) // 2, SCREEN_HEIGHT - 60, w, h)
		self.speed = 7

	def move(self, dx):
		self.rect.x += dx
		self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.w))

	def update_mouse(self, mouse_x):
		self.rect.centerx = mouse_x
		self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.w))

	def draw(self, surf):
		pygame.draw.rect(surf, BLUE, self.rect)


class Ball:
	def __init__(self):
		self.radius = 8
		self.reset()

	def reset(self):
		self.x = SCREEN_WIDTH // 2
		self.y = SCREEN_HEIGHT // 2
		angle = random.uniform(-1, 1)
		self.vx = 5 * (1 if random.random() < 0.5 else -1)
		self.vy = -4

	def rect(self):
		return Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

	def update(self):
		self.x += self.vx
		self.y += self.vy

		# 벽 충돌
		if self.x - self.radius <= 0:
			self.x = self.radius
			self.vx = -self.vx
		if self.x + self.radius >= SCREEN_WIDTH:
			self.x = SCREEN_WIDTH - self.radius
			self.vx = -self.vx
		if self.y - self.radius <= 0:
			self.y = self.radius
			self.vy = -self.vy

	def draw(self, surf):
		pygame.draw.circle(surf, RED, (int(self.x), int(self.y)), self.radius)


class Brick:
	def __init__(self, x, y, w, h, color, hits=1):
		self.rect = Rect(x, y, w, h)
		self.color = color
		self.hits = hits

	def hit(self):
		self.hits -= 1
		return self.hits <= 0

	def draw(self, surf):
		pygame.draw.rect(surf, self.color, self.rect)
		pygame.draw.rect(surf, BLACK, self.rect, 2)


class Item:
	"""낙하 아이템: 'gun' 또는 'big_ball'"""
	def __init__(self, x, y, kind):
		self.kind = kind
		self.w = 24
		self.h = 12
		self.rect = Rect(int(x - self.w // 2), int(y - self.h // 2), self.w, self.h)
		self.vy = 3

	def update(self):
		self.rect.y += self.vy

	def draw(self, surf):
		if self.kind == 'gun':
			color = (255, 200, 50)
		else:
			color = (150, 50, 255)
		pygame.draw.rect(surf, color, self.rect)
		pygame.draw.rect(surf, BLACK, self.rect, 2)


class Bullet:
	def __init__(self, x, y):
		self.w = 4
		self.h = 12
		self.x = x
		self.y = y
		self.vy = -10
		self.rect = Rect(int(x - self.w // 2), int(y - self.h), self.w, self.h)

	def update(self):
		self.y += self.vy
		self.rect.y = int(self.y - self.h)

	def draw(self, surf):
		pygame.draw.rect(surf, (255, 240, 100), self.rect)


class Game:
	def __init__(self):
		pygame.init()
		pygame.display.set_caption("블럭깨기 게임")
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		self.clock = pygame.time.Clock()
		self.font = pygame.font.SysFont(None, 28)

		# 배경 이미지 로드 (로컬 파일)
		self.bg_image = None
		try:
			img_path = r"c:\work\image\장원영.jpg"
			if os.path.exists(img_path):
				img = pygame.image.load(img_path)
				# 화면 크기에 맞게 스케일
				self.bg_image = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
			else:
				print(f"Background image not found: {img_path}")
		except Exception as e:
			print("Failed to load background image:", e)
			self.bg_image = None

		self.paddle = Paddle()
		self.ball = Ball()
		# 아이템/총알 상태
		self.items = []          # 떨어지는 아이템들
		self.bullets = []        # 발사된 총알들
		self.has_gun = False
		self.gun_expires = 0
		self.gun_duration = 15000  # ms
		self.last_shot = 0
		self.shot_cooldown = 350  # ms

		# 구슬 크기 파워업 상태
		self.ball_original_radius = self.ball.radius
		self.big_ball_expires = 0
		self.big_ball_duration = 15000  # ms

		self.bricks = []
		self.score = 0
		self.lives = 3
		self.paused = True
		self.build_level()

	def build_level(self, rows=6, cols=10):
		self.bricks.clear()
		pad = 5
		brick_w = (SCREEN_WIDTH - pad * (cols + 1)) // cols
		brick_h = 22
		# 상단 블럭은 화려한 무지개 팔레트 사용
		bright_colors = [
			(255, 82, 82),    # vivid red
			(255, 188, 82),   # orange
			(255, 238, 88),   # yellow
			(102, 255, 102),  # light green
			(102, 204, 255),  # sky blue
			(102, 102, 255),  # blue
			(178, 102, 255),  # purple
			(255, 102, 204),  # pink
		]
		base_colors = [YELLOW, GREEN, GREY, BLUE, RED, (180, 80, 160)]
		top_rows = 2
		for row in range(rows):
			for col in range(cols):
				x = pad + col * (brick_w + pad)
				y = pad + row * (brick_h + pad) + 40
				if row < top_rows:
					# 컬럼에 따라 색을 배치해 무지개처럼 보이게 함
					color = bright_colors[(col + row) % len(bright_colors)]
				else:
					color = base_colors[row % len(base_colors)]
				hits = 1 + (row // 3)
				self.bricks.append(Brick(x, y, brick_w, brick_h, color, hits))

	def reset_ball_and_paddle(self):
		self.paddle = Paddle()
		self.ball = Ball()
		self.paused = True

	def draw_hud(self):
		txt = f"Score: {self.score}  Lives: {self.lives}  Bricks: {len(self.bricks)}"
		surf = self.font.render(txt, True, WHITE)
		self.screen.blit(surf, (10, 10))
		# 파워업 상태 표시
		x = SCREEN_WIDTH - 10
		if self.has_gun and self.gun_expires > pygame.time.get_ticks():
			remaining = (self.gun_expires - pygame.time.get_ticks()) // 1000
			s = f"GUN:{remaining}s"
			surf2 = self.font.render(s, True, (255, 200, 50))
			r = surf2.get_rect(topright=(x, 10))
			self.screen.blit(surf2, r)
		if self.big_ball_expires > pygame.time.get_ticks():
			remaining = (self.big_ball_expires - pygame.time.get_ticks()) // 1000
			s = f"BIGx3:{remaining}s"
			surf3 = self.font.render(s, True, (180, 100, 255))
			r2 = surf3.get_rect(topright=(x, 34))
			self.screen.blit(surf3, r2)

	def handle_collisions(self):
		ball_rect = self.ball.rect()
		# 패들 충돌
		if ball_rect.colliderect(self.paddle.rect) and self.ball.vy > 0:
			overlap_x = (ball_rect.centerx - self.paddle.rect.centerx) / (self.paddle.w / 2)
			self.ball.vx += overlap_x * 2
			self.ball.vy = -abs(self.ball.vy)
			# 공 속도 제한
			self.ball.vx = max(-8, min(8, self.ball.vx))

		# 블럭 충돌
		for brick in self.bricks[:]:
			if ball_rect.colliderect(brick.rect):
				# 충돌 방향 판별 (단순)
				# 공의 중심이 블럭의 어느 쪽에 있는지에 따라 방향 반전
				bx, by = brick.rect.center
				if abs(self.ball.x - bx) > abs(self.ball.y - by):
					self.ball.vx = -self.ball.vx
				else:
					self.ball.vy = -self.ball.vy

				destroyed = brick.hit()
				if destroyed:
					# 블럭 파괴: 블럭 제거, 점수, 아이템 드랍 확률 적용
					cx, cy = brick.rect.center
					self.bricks.remove(brick)
					self.score += 10
					self.maybe_spawn_item(cx, cy)
				else:
					self.score += 5
				break

	def maybe_spawn_item(self, x, y):
		# 일정 확률로 아이템 드랍 (25%)
		if random.random() < 0.25:
			kind = 'gun' if random.random() < 0.5 else 'big_ball'
			self.items.append(Item(x, y, kind))

	def update_items(self):
		# 떨어지는 아이템 이동, 패들과 충돌 처리
		for item in self.items[:]:
			item.update()
			# 바닥 아래로 나가면 삭제
			if item.rect.top > SCREEN_HEIGHT:
				self.items.remove(item)
				continue
			if item.rect.colliderect(self.paddle.rect):
				# 아이템 획득
				self.apply_item(item.kind)
				try:
					self.items.remove(item)
				except ValueError:
					pass

	def update_bullets(self):
		# 총알 이동 및 블럭 충돌 처리
		for b in self.bullets[:]:
			b.update()
			if b.rect.bottom < 0:
				self.bullets.remove(b)
				continue
			# 총알-블럭 충돌
			for brick in self.bricks[:]:
				if b.rect.colliderect(brick.rect):
					destroyed = brick.hit()
					if destroyed:
						cx, cy = brick.rect.center
						try:
							self.bricks.remove(brick)
						except ValueError:
							pass
						self.score += 10
						self.maybe_spawn_item(cx, cy)
					else:
						self.score += 5
					# 총알은 블럭에 닿으면 사라짐
					try:
						self.bullets.remove(b)
					except ValueError:
						pass
					break

	def shoot_bullet(self):
		x = self.paddle.rect.centerx
		y = self.paddle.rect.top
		self.bullets.append(Bullet(x, y))

	def apply_item(self, kind):
		now = pygame.time.get_ticks()
		if kind == 'gun':
			self.has_gun = True
			self.gun_expires = now + self.gun_duration
		elif kind == 'big_ball':
			# 구슬 크기 3배
			if self.ball.radius == self.ball_original_radius:
				self.ball.radius = int(self.ball_original_radius * 3)
			# 갱신된 지속시간
			self.big_ball_expires = now + self.big_ball_duration

	def update_powerups(self):
		now = pygame.time.get_ticks()
		if self.has_gun and now > self.gun_expires:
			self.has_gun = False
			self.gun_expires = 0
		if self.big_ball_expires and now > self.big_ball_expires:
			# 효과 종료: 반지름 원복
			self.ball.radius = self.ball_original_radius
			self.big_ball_expires = 0

	def update(self):
		if self.paused:
			return

		self.ball.update()
		# 아이템/총알 업데이트
		self.update_items()
		self.update_bullets()
		self.update_powerups()
		# 공이 바닥에 닿음
		if self.ball.y - self.ball.radius > SCREEN_HEIGHT:
			self.lives -= 1
			if self.lives <= 0:
				self.game_over()
			else:
				self.reset_ball_and_paddle()
			return

		self.handle_collisions()

		if not self.bricks:
			# 다음 레벨
			self.build_level(rows=6, cols=10)
			self.reset_ball_and_paddle()

	def game_over(self):
		self.paused = True
		# 초기화
		self.score = 0
		self.lives = 3
		self.build_level()
		self.reset_ball_and_paddle()
		# 아이템/총알 초기화
		self.items.clear()
		self.bullets.clear()
		self.has_gun = False
		self.gun_expires = 0
		self.big_ball_expires = 0

	def draw(self):
		if self.bg_image:
			self.screen.blit(self.bg_image, (0, 0))
		else:
			self.screen.fill((24, 24, 24))
		for brick in self.bricks:
			brick.draw(self.screen)
		self.paddle.draw(self.screen)
		self.ball.draw(self.screen)
		# 아이템 및 총알 그리기
		for item in self.items:
			item.draw(self.screen)
		for b in self.bullets:
			b.draw(self.screen)
		self.draw_hud()

		if self.paused:
			msg = "Press SPACE to start / restart. Use ← → or mouse to move"
			surf = self.font.render(msg, True, WHITE)
			r = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
			self.screen.blit(surf, r)

		pygame.display.flip()

	def run(self):
		running = True
		while running:
			dt = self.clock.tick(FPS)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						running = False
					elif event.key == pygame.K_SPACE:
						# 스페이스: 총 보유 시 발사, 아니면 일시정지 토글
						if not self.paused and self.has_gun:
							# 발사 (쿨다운 적용)
							now = pygame.time.get_ticks()
							if now - self.last_shot >= self.shot_cooldown:
								self.shoot_bullet()
								self.last_shot = now
						else:
							# 시작 또는 재개
							if self.paused and (self.ball.y > SCREEN_HEIGHT - 100 or self.ball.y < SCREEN_HEIGHT):
								self.ball.reset()
							self.paused = not self.paused
				elif event.type == pygame.MOUSEMOTION:
					# 마우스 이동으로 패들 제어
					mx, my = event.pos
					self.paddle.update_mouse(mx)

			# 키 입력 처리
			keys = pygame.key.get_pressed()
			if keys[pygame.K_LEFT] or keys[pygame.K_a]:
				self.paddle.move(-self.paddle.speed)
			if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				self.paddle.move(self.paddle.speed)

			self.update()
			self.draw()

		pygame.quit()


def main():
	game = Game()
	game.run()


if __name__ == '__main__':
	main()

