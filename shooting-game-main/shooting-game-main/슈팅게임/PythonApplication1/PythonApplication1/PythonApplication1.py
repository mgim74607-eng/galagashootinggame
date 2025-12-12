from tkinter import *
import time
import pygame
import random
from PIL import Image, ImageTk


class Enemy:
	def __init__(self, canvas, images, id, canAttack):
		self.__frame = 0
		self.id = 'e' + str(id)
		self.canvas = canvas
		self.images = images
		self.canAttack = canAttack
		self.stopped = False
		self.lastAttackTime = time.time()
		if self.canAttack:
			self.me = self.canvas.create_image(random.randint(100, 640), random.randint(50, 150), image=self.images[0], tags=self.id)
			self.stopY = random.randint(100, 200)
		else:
			self.me = self.canvas.create_image(random.randint(100, 640), random.randint(50, 200), image=self.images[0], tags=self.id)
			self.stopY = -1
		self.frame = 0

	def update(self):
		self.canvas.itemconfig(self.me, image=self.images[self.frame % len(self.images)])
		if self.canAttack:
			if not self.stopped:
				pos = self.canvas.coords(self.me)
				if pos[1] >= self.stopY:
					self.stopped = True
				else:
					self.canvas.move(self.me, 0, 2)
		else:
			self.canvas.move(self.me, 0, 2)
		self.frame = self.frame + 1

	def getPos(self):
		return self.canvas.coords(self.me)

	def getId(self):
		return self.me

	def getCanAttack(self):
		return self.canAttack

	def getStopped(self):
		return self.stopped

	def getLastAttackTime(self):
		return self.lastAttackTime

	def setLastAttackTime(self, t):
		self.lastAttackTime = t


class GalagaGame:
	def __init__(self):
		self.window = Tk()
		self.window.title("갤러그 게임")
		self.window.geometry("740x740")
		self.window.resizable(0, 0)
		self.lastTime = time.time()
		self.keys = set()
		self.canvas = Canvas(self.window, bg="black")
		self.canvas.pack(expand=True, fill=BOTH)
		self.window.bind("<KeyPress>", self.keyPressHandler)
		self.window.bind("<KeyRelease>", self.keyReleaseHandler)
		self.window.protocol("WM_DELETE_WINDOW", self.onClose)

		self.my_image_number = 0
		player_img = Image.open('image/player_ship.png')
		player_img = player_img.resize((player_img.width // 6, player_img.height // 6))
		self.myimages = [ImageTk.PhotoImage(player_img)]

		self.enemy_img_number = 0
		enemy_img = Image.open('image/enemy_ship.png')
		enemy_img = enemy_img.resize((enemy_img.width // 6, enemy_img.height // 6))
		self.enemyimages = [ImageTk.PhotoImage(enemy_img)]

		bg_img = Image.open("image/background.png")
		bg_img = bg_img.resize((740, 740))
		self.bgimage = ImageTk.PhotoImage(bg_img)
		self.canvas.create_image(0, 0, image=self.bgimage, anchor=NW, tags="bg")

		fire_img = Image.open("image/fire_type2.png")
		fire_img = fire_img.resize((fire_img.width // 8, fire_img.height // 8))
		self.fire = ImageTk.PhotoImage(fire_img)

		enemy_fire_img = Image.open("image/fire_type2.png")
		enemy_fire_img = enemy_fire_img.resize((enemy_fire_img.width // 10, enemy_fire_img.height // 10))
		self.enemy_fire = ImageTk.PhotoImage(enemy_fire_img)

		self.player = self.canvas.create_image(370, 650, image=self.myimages[0], tags="player")

		self.enemy_list = []
		self.enemy_id = 0

		pygame.init()
		pygame.mixer.music.load("sound/bgm.mp3")
		pygame.mixer.music.play(-1)

		self.sounds = pygame.mixer
		self.sounds.init()
		self.s_effect1 = self.sounds.Sound("sound/destruction.mp3")

		self.canvas.create_text(150, 50, fill="white", font="Times 15 italic bold", text="입력키: ←, →, space")
		self.canvas.create_text(370, 600, fill="white", font="Times 15 italic bold", text="Galaga")
		

		while True:
			try:
				self.canvas.itemconfig(self.player, image=self.myimages[self.my_image_number % len(self.myimages)])

				self.my_image_number += 1
				self.enemy_img_number += 1

				fires = self.canvas.find_withtag("fire")
				self.display()

				for fire in fires:
					self.canvas.move(fire, 0, -9)
					if self.canvas.coords(fire)[1] < 0:
						self.canvas.delete(fire)

				enemy_fires = self.canvas.find_withtag("enemy_fire")
				for enemy_fire in enemy_fires:
					self.canvas.move(enemy_fire, 0, 5)
					if self.canvas.coords(enemy_fire)[1] > 740:
						self.canvas.delete(enemy_fire)

				self.manageEnemy()

			except TclError:
				return

			self.window.after(33)
			self.window.update()

	def manageEnemy(self):
		if (random.randint(0, 70) == 0):
			canAttack = (random.randint(0, 3) == 0)
			self.enemy_list.append(Enemy(self.canvas, self.enemyimages, self.enemy_id, canAttack))
			self.enemy_id = self.enemy_id + 1

		for e in self.enemy_list:
			e.update()
			if e.getCanAttack() and e.getStopped():
				now = time.time()
				if (now - e.getLastAttackTime()) > 1.5:
					e.setLastAttackTime(now)
					pos = e.getPos()
					self.canvas.create_image(pos[0], pos[1] + 30, image=self.enemy_fire, tags="enemy_fire")

			if e.getPos()[1] > 740:
				self.canvas.delete(e.getId())
				self.enemy_list.pop(self.enemy_list.index(e))

		fires = self.canvas.find_withtag("fire")
		area = 25
		for fire in fires:
			f_pos = self.canvas.coords(fire)
			for e in self.enemy_list:
				e_pos = e.getPos()
				if e_pos[0] - area < f_pos[0] and e_pos[0] + area > f_pos[0] and e_pos[1] - area < f_pos[1] and e_pos[1] + area > f_pos[1]:
					self.s_effect1.play()
					self.canvas.delete(e.getId())
					self.enemy_list.pop(self.enemy_list.index(e))
					self.canvas.delete(fire)

		enemy_fires = self.canvas.find_withtag("enemy_fire")
		player_pos = self.canvas.coords(self.player)
		for enemy_fire in enemy_fires:
			ef_pos = self.canvas.coords(enemy_fire)
			if player_pos[0] - area < ef_pos[0] and player_pos[0] + area > ef_pos[0] and player_pos[1] - area < ef_pos[1] and player_pos[1] + area > ef_pos[1]:
				self.canvas.delete(enemy_fire)

	def keyReleaseHandler(self, event):
		if event.keycode in self.keys:
			self.keys.remove(event.keycode)

	def display(self):
		player = self.canvas.find_withtag("player")
		for key in self.keys:
			if key == 39:
				self.canvas.move(player, 5, 0)
			if key == 37:
				self.canvas.move(player, -5, 0)
			if key == 32:
				now = time.time()
				if (now - self.lastTime) > 0.3:
					self.lastTime = now
					pos = self.canvas.coords(player)
					self.canvas.create_image(pos[0], pos[1] - 30, image=self.fire, tags="fire")

	def keyPressHandler(self, event):
		if event.keycode == 27:
			self.onClose()
		else:
			self.keys.add(event.keycode)

	def onClose(self):
		self.running = False
		pygame.mixer.music.stop()
		pygame.quit()
		self.window.destroy()


GalagaGame()