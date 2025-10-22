#!python3
###################
# Made by Jihadz #
###################

import re, sys, os
import subprocess
import pkg_resources

sys.dont_write_bytecode = True

from time import sleep, time
from threading import Thread, Lock
from colorama import Fore
from PIL import Image
from pathlib import Path
import datetime
import cv2 as cv
import pyautogui
import colorama
import keyboard
import random
import win32api, win32ui, win32con
import pytesseract
import numpy as np
import math

class BotState:
	INIT = 0
	FARMING = 1
	FLEEING = 2

class PGBot:

	INIT_TIME = 2

	stopped = True
	lock = None

	state = None
	timestamp = None

	appName = 'UnknownAppOrigin'
	version = '0.1'
	pytesseract.pytesseract.tesseract_cmd = ''
	minimapLoc = [0,0]
	updated = False
	paused = False

	plr_energy = 0
	plr_hp = 0
	last_hp = 100
	last_heal_time = 0
	dtime = [0,0,0,0,0] # Energy, HP, Map, Collector, NavMenu
	outliers = [0,0,0,0]
	lastChat = []

	targets = False
	lastPrint = '';
	ws = "                     "

	techTree = {"aoe": ["rocket", "orbitalstrike", "aggrobomb", "mine", "stundome", "stickybomb", "magnettrap", "aggrobeacon"], "defend": ["shield", "protector", "scramble"], "single": ["rocket", "orbitalstrike", "stun", "thermoblast", "taunt", "sniper", "attackdroid"], "buff": ["speedactuator", "aimcomp", "perforator", "dmgbuff"]}

	# Init
	def __init__(self, settings, appName, version):
		self.lock = Lock()

		self.state = BotState.INIT
		self.timestamp = time()
		self.updated = True

		self.version = version
		pytesseract.pytesseract.tesseract_cmd = settings.get('tesseract', "C:/Program Files/Tesseract-OCR/tesseract.exe")

		self.appName = appName
		self.minimapLoc = [0,0]
		presets = settings.get('presets', {"custom": ["blaster","collector","repair","afterburner","","","",""]})
		self.skills = presets[settings.get('skillset', 'custom')]

		self.plr_energy = 0
		self.plr_hp = 100
		self.last_hp = 100
		self.last_heal_time = 0
		self.outliers = [0,0,0,0]
		self.lastChat = []
		self.objectCount = 0
		self.objectPrio = settings.get('priority', ["enemy","loot","enemyIdle"])
		self.objectPixel = settings.get('search', {"enemy": [135,27,11],"enemyIdle": [162,151,15],"loot": [19,193,217]})
		
		# Sistema de curación
		self.healOnHp = settings.get('healOnHp', 25)
		self.healThresholds = settings.get('healThresholds', [80, 50, 30])
		self.healCooldown = settings.get('healCooldown', 60)
		
		self.defendOnHp = settings.get('defendOnHp', 45)
		self.runOnHp = settings.get('runOnHp', 10)
		self.lowEnergy = settings.get('lowEnergy', 1000)
		self.occasionalSkill = settings.get('occasionalSkill', 150)
		
		# Perfil de combate actual
		self.current_profile = settings.get('combat_profile', 'balanced')
		
		# Sistema de Energy Loading
		self.energy_loading_active = False
		self.energy_loading_thread = None
		self.energy_debug_window_active = False

		if not Path(pytesseract.pytesseract.tesseract_cmd).exists():
			self.terminal(f'Cant find pytesseract!', 'danger')
			exit()
		
		# Cargar región de energía desde settings
		self.energy_region = None
		try:
			screen_width, screen_height = pyautogui.size()
			resolution_key = f"{screen_width}x{screen_height}"
			
			if 'stats_config' in settings and 'energy_region' in settings['stats_config']:
				energy_regions = settings['stats_config']['energy_region']
				if resolution_key in energy_regions:
					self.energy_region = tuple(energy_regions[resolution_key])
					print(f"✓ Energy region loaded for {resolution_key}: {self.energy_region}")
				elif 'default' in energy_regions:
					self.energy_region = tuple(energy_regions['default'])
					print(f"⚠ Using default energy region: {self.energy_region}")
		except Exception as e:
			print(f"⚠ Could not load energy region: {e}")
	
	# Aplicar perfil de combate
	def apply_combat_profile(self, profile_name):
		"""Aplicar perfil de combate dinámicamente"""
		profiles = {
			'aggressive': {
				'healOnHp': 20,
				'defendOnHp': 30,
				'runOnHp': 5,
				'occasionalSkill': 20,
				'healCooldown': 45
			},
			'balanced': {
				'healOnHp': 30,
				'defendOnHp': 45,
				'runOnHp': 10,
				'occasionalSkill': 50,
				'healCooldown': 60
			},
			'defensive': {
				'healOnHp': 50,
				'defendOnHp': 65,
				'runOnHp': 20,
				'occasionalSkill': 100,
				'healCooldown': 30
			},
			'spam': {
				'healOnHp': 30,
				'defendOnHp': 45,
				'runOnHp': 10,
				'occasionalSkill': 5,
				'healCooldown': 60
			}
		}
		
		if profile_name in profiles:
			profile = profiles[profile_name]
			self.healOnHp = profile['healOnHp']
			self.defendOnHp = profile['defendOnHp']
			self.runOnHp = profile['runOnHp']
			self.occasionalSkill = profile['occasionalSkill']
			self.healCooldown = profile['healCooldown']
			self.current_profile = profile_name
			return True
		return False

	# Find targets on minimap
	def update_targets(self):
		if not self.checkTimePassed(2, 1):
			return

		targets = self.findObject(True)
		self.lock.acquire()
		self.targets = targets
		self.updated = True
		self.lock.release()

		# Check HP with updating and using resources
		if (self.plr_hp <= self.healOnHp):
			self.skill(self.checkSkill("repair"))

	# Start the bot
	def start(self):
		self.stopped = False
		t = Thread(target=self.run)
		t.start()
		print(f'{Fore.GREEN}Bot started{Fore.WHITE}')

	# Stop the bot
	def stop(self):
		self.stopped = True
		# Cerrar ventana de debug si está activa
		if self.energy_debug_window_active:
			try:
				cv.destroyAllWindows()
				self.energy_debug_window_active = False
			except:
				pass

	# Main Bot Logic
	def run(self):
		while not self.stopped:
			if self.paused: # Paused
				sleep(0.2)
				continue

			if self.state == BotState.INIT: # Initializing
				if time() > self.timestamp + self.INIT_TIME:
					self.lock.acquire()
					self.state = BotState.FARMING
					self.lock.release()

			elif self.state == BotState.FARMING: # Farming
				# Check Energy
				if self.checkTimePassed(0, 15):
					try:
						if self.checkEnergy():
							self.terminal(f'Low Energy! ({self.plr_energy})', 'danger')
					except:
						pass

				self.checkHP()

				# Check if Nav Menu is open
				if self.checkTimePassed(4, 45):
					try:
						if self.search('orbit') != False:
							navmenu = self.search('navmenu')
							if navmenu != False:
								self.click(navmenu.left + 5, navmenu.top + 5)
					except:
						pass

				# Battle and Collect
				if self.targets != False:
					# Ignore idle targets if energy is low or if below low hp threshold
					if self.targets[2] == 'enemyIdle' and (self.plr_energy <= self.lowEnergy or self.plr_hp <= self.healOnHp):
						continue

					# Use Collector to prevent softlock
					if self.checkTimePassed(3, 4):
						self.skill(self.checkSkill("collector"))

					try:
						if self.updated:
							self.moveTo(self.targets)
							self.lock.acquire()
							self.updated = False
							self.lock.release()
						self.interact(self.targets[2])
					except Exception:
						pass # Ignore

			elif self.state == BotState.FLEEING: # Fleeing
				self.checkHP()

				self.skill(self.checkSkill("afterburner"))
				self.skill(self.checkSkill("repair"))

				if self.plr_hp >= math.ceil(self.healOnHp / 2):
					self.lock.acquire()
					self.state = BotState.FARMING
					self.lock.release()

	#---# Helper Scripts #---#

	# Click Function
	def click(self, x,y):
		win32api.SetCursorPos((x,y))
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
		sleep(0.1)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

	# Double Click
	def doubleclick(self, x,y):
		self.click(x,y)
		self.click(x,y)

	# Get Text from Image
	def getText(self, image):
		return pytesseract.image_to_string(image, lang='eng', config='--psm 6')

	# Get Numbers from Image
	def getNum(self, image):
		nums = pytesseract.image_to_string(image, config='-c tessedit_char_whitelist=0123456789')
		if nums == " ":
			nums = pytesseract.image_to_string(image, config='--psm 10 --oem 3 -c tessedit_do_invert=0 -c tessedit_char_whitelist=0123456789')
		if nums == " ":
			return "0"
		return nums

	# Check a Pixel for its RGB values
	def isPixel(self, x,y,c):
		if pyautogui.pixel(x,y)[0] == c[0] and pyautogui.pixel(x,y)[1] == c[1] and pyautogui.pixel(x,y)[2] == c[2]:
			return True
		return False

	# Find Pixel in Image
	def imgFindPixel(self, img, c, findAll = False):
		width, height = img.size
		listAll = []
		for x in range(width):
			for y in range(height):
				pix = img.getpixel((x,y))
				if pix[0] == c[0] and pix[1] == c[1] and pix[2] == c[2]:
					if findAll:
						listAll.append([x,y])
					else:
						return [x,y]
		if findAll:
			if len(listAll) != 0:
				return listAll
		return False

	# Find Object on Minimap
	def minimapFind(self, find, nearest = False):
		minimap = self.search('minimap')
		if minimap != False:
			self.minimapLoc = [minimap.left + 25, minimap.top - 100]
			minimap = pyautogui.screenshot('./data/search/minimap.png', region=(int(minimap.left + 25), int(minimap.top - 100), 115, 115))
			found = self.imgFindPixel(minimap, find, nearest)
			if found != False:
				if nearest == False:
					return found
			else:
				return False
		else:
			return False

		# Return nearest
		self.objectCount = len(found)
		center = [115 / 2, 115 / 2]
		near = []
		for loc in found:
			if near == []:
				near = loc
			else:
				new_dist = abs(loc[0] - center[0]) + abs(loc[1] - center[1])
				old_dist = abs(near[0] - center[0]) + abs(near[1] - center[1])
				if new_dist < old_dist:
					near = loc
		return near

	# Image recognition
	def search(self, img, conf=0.8):
		try:
			simg = pyautogui.locateOnScreen('./data/images/' + img + '.png', confidence=conf)
			if simg != None:
				return simg
			else:
				return False
		except:
			return False

	# Check Energy - MEJORADO CON REGIÓN CONFIGURADA
	def checkEnergy(self, num=None):
		"""Sistema de detección de energía mejorado - USA LA REGIÓN CONFIGURADA"""
		if num is None:
			num = self.lowEnergy

		try:
			# Usar región configurada desde settings
			if hasattr(self, 'energy_region') and self.energy_region:
				region = self.energy_region
			else:
				# Fallback: buscar icono de energía
				find = None
				for confidence in [0.7, 0.6, 0.5]:
					find = self.search('energy', confidence)
					if find != False:
						break
				
				if find == False:
					self.lock.acquire()
					self.plr_energy = 10000
					self.lock.release()
					return False
				
				# Usar offsets si no hay región configurada
				region = (int(find.left - 60), int(find.top), 60, 20)
			
			# Capturar región
			screenshot = pyautogui.screenshot(region=region)
			
			# Preprocesamiento
			img_array = np.array(screenshot)
			gray = cv.cvtColor(img_array, cv.COLOR_RGB2GRAY)
			_, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
			
			# Invertir si el fondo es oscuro
			if np.mean(binary) < 127:
				binary = cv.bitwise_not(binary)
			
			# Intentar OCR múltiples veces
			cenergy = None
			
			# Intento 1: PSM 7 (línea de texto)
			try:
				result = pytesseract.image_to_string(
					Image.fromarray(binary),
					config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789,'
				)
				result = result.replace('\x0c', '').replace('\n', '').replace(',', '').replace('.', '').replace(' ', '').strip()
				if result and result.isdigit():
					cenergy = int(result)
			except:
				pass
			
			# Intento 2: PSM 8 (palabra)
			if cenergy is None:
				try:
					result = pytesseract.image_to_string(
						Image.fromarray(binary),
						config='--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789'
					)
					result = result.replace('\x0c', '').replace('\n', '').replace(',', '').replace('.', '').replace(' ', '').strip()
					if result and result.isdigit():
						cenergy = int(result)
				except:
					pass
			
			# Intento 3: Método original
			if cenergy is None:
				try:
					result = self.getNum(screenshot)
					result = result.replace('\x0c', '').replace('\n', '').replace(',', '').replace('.', '').replace(' ', '').strip()
					if result and result.isdigit():
						cenergy = int(result)
				except:
					pass
			
			# Si todos los intentos fallaron
			if cenergy is None or cenergy <= 0:
				self.lock.acquire()
				self.plr_energy = 10000
				self.lock.release()
				return False
			
			# Validar rango razonable
			if not (100 <= cenergy <= 50000):
				# Valor fuera de rango, probablemente incorrecto
				self.lock.acquire()
				self.plr_energy = 10000
				self.lock.release()
				return False
			
			# Filtro de outliers
			if self.outliers[2] > 0:
				diff = abs(self.outliers[2] - cenergy)
				if diff >= 5000 and self.outliers[3] <= 2:
					cenergy = self.outliers[2]
					nout = self.outliers[3] + 1
				else:
					nout = 0
			else:
				nout = 0

			self.lock.acquire()
			self.outliers[3] = nout
			self.plr_energy = cenergy
			self.outliers[2] = cenergy
			self.lock.release()

			if cenergy <= num:
				return True
			return False
				
		except Exception as e:
			self.lock.acquire()
			self.plr_energy = 10000
			self.lock.release()
			return False

	# Find Energy
	def findEnergy(self):
		return False

	# Find Objects
	def findObject(self, nearest = False):
		for obj in self.objectPrio:
			find = self.minimapFind(self.objectPixel[obj], nearest)
			if find != False:
				find.append(obj)
				return find

		self.objectCount = 0
		return False

	# Move to Position and avoid obstacles
	def moveTo(self, pos = False):
		if pos == False:
			return False

		# Obstacle evasion

		# Move
		self.click(self.minimapLoc[0] + pos[0] - 1, self.minimapLoc[1] + pos[1])

	# Check HP and heal if needed
	def checkHP(self):
		"""Sistema de curación inteligente"""
		if not self.checkTimePassed(1, 2):
			if (self.plr_hp <= self.healOnHp):
				current_time = time()
				if current_time - self.last_heal_time >= self.healCooldown:
					self.skill(self.checkSkill("repair"))
					self.last_heal_time = current_time
					return True
			return False

		find = self.search('minimap')
		if find != False:
			chp = pyautogui.screenshot('./data/search/hp.png', region=(int(find.left - 25), int(find.top + 5), 20, 15))
			newImg = Image.new('RGB', (2*chp.size[0], chp.size[1]), (250,250,250))
			newImg.paste(chp,(0,0))
			newImg.paste(chp,(chp.size[0],0))
			newImg.save("./data/search/hp.png", "PNG")

			chp = self.getNum(Image.open('./data/search/hp.png')).replace('\n', '').replace('\x0c', '').replace('|', '')
			chp = chp[0:int(len(chp)/2)]
			if chp != '' and chp != ' ':
				chp = int(chp)

				if chp == 1 or chp == 2:
					return False

				self.lock.acquire()
				old_hp = self.last_hp
				self.plr_hp = chp
				self.lock.release()

				current_time = time()
				time_since_last_heal = current_time - self.last_heal_time
				hp_is_dropping = chp < old_hp or old_hp == 100
				
				should_heal = False
				
				if chp < 80 and hp_is_dropping and time_since_last_heal >= self.healCooldown:
					should_heal = True
				elif chp <= self.healOnHp:
					should_heal = True
				
				if should_heal:
					self.skill(self.checkSkill("repair"))
					self.last_heal_time = current_time
					self.last_hp = chp
					return True
				
				self.last_hp = chp
					
			else:
				self.lock.acquire()
				self.plr_hp = 100
				self.last_hp = 100
				self.lock.release()
			return False
		else:
			return False

	# Decide action based on findings
	def interact(self, act):
		if act == "loot":
			self.skill(self.checkSkill("collector"))

		if act == "enemy" or act == "enemyIdle":
			self.interactType('aoe')
			self.interactType('defend')
			self.interactType('single')
			self.interactType('buff')

			if self.plr_hp <= self.runOnHp:
				self.lock.acquire()
				self.state = BotState.FLEEING
				self.lock.release()

			self.skill(1)

	# Interaction types
	def interactType(self, itype):
		techs = []
		for tech in self.techTree[itype]:
			if self.checkSkill(tech):
				techs.append(tech)

		cond_aoe = self.objectCount >= 3 and len(techs) > 0
		cond_defend = self.plr_hp <= self.defendOnHp and len(techs) > 0
		cond_occasion = random.randint(1, self.occasionalSkill) == 1 and len(techs) > 0

		if (itype == 'aoe' and cond_aoe) or (itype == 'defend' and cond_defend) or ((itype == 'single' or itype == 'buff') and cond_occasion):
			self.skill(self.checkSkill(techs[random.randint(0, len(techs) - 1)]))

	# Check if User has Skill
	def checkSkill(self, check):
		index = 1
		for a in self.skills:
			if check == a:
				return index
			index += 1
		return False

	# Use a Skill
	def skill(self, num):
		if num == False or num < 1 or num > 8:
			return False
		keyboard.press(str(num))
		sleep(0.1)
		keyboard.release(str(num))

	# Send Decoy Message
	def chatSend(self, msg):
		find = self.search('chatWindow')
		if find != False:
			self.click(find.left + 200, find.top + 5)
			keyboard.write(msg)
			keyboard.press('enter')
			sleep(0.1)
			keyboard.release('enter')

	# Print to local and remote Terminal
	def terminal(self, text, type='text'):
		col = Fore.WHITE
		if type == 'info':
			col = Fore.LIGHTCYAN_EX
		if type == 'warn':
			col = Fore.YELLOW
		if type == 'danger':
			col = Fore.LIGHTRED_EX

		ptext = f'{col}{text}{Fore.WHITE}{self.ws}'
		if text != self.lastPrint:
			print(ptext)

			self.lock.acquire()
			self.lastPrint = ptext
			self.lock.release()
		return True

	# ============================================
	# ENERGY LOADING SYSTEM - MEJORADO V2
	# ============================================

	def detect_energy_orbs(self):
		"""
		Detectar orbes de energía azules en pantalla - VERSIÓN MEJORADA
		Returns: (orbs_list, debug_image) si energy_loading_active, sino solo orbs_list
		"""
		try:
			# Región de búsqueda (pantalla principal)
			screen_width, screen_height = pyautogui.size()
			
			search_region = {
				'x': 50,
				'y': 50,
				'width': screen_width - 700,
				'height': screen_height - 200
			}
			
			# Capturar pantalla
			screenshot = pyautogui.screenshot(region=(
				search_region['x'],
				search_region['y'],
				search_region['width'],
				search_region['height']
			))
			
			# Convertir a numpy y HSV
			img_rgb = np.array(screenshot)
			img_bgr = cv.cvtColor(img_rgb, cv.COLOR_RGB2BGR)
			img_hsv = cv.cvtColor(img_bgr, cv.COLOR_BGR2HSV)
			
			# MEJORADO: Rango de color más amplio para azul brillante
			lower_blue = np.array([85, 120, 120])
			upper_blue = np.array([135, 255, 255])
			
			# Crear máscara
			mask = cv.inRange(img_hsv, lower_blue, upper_blue)
			
			# MEJORADO: Limpiar ruido con morfología más agresiva
			kernel = np.ones((5, 5), np.uint8)
			mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel, iterations=3)
			mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel, iterations=2)
			
			# Dilatar ligeramente para capturar bordes
			kernel_dilate = np.ones((3, 3), np.uint8)
			mask = cv.dilate(mask, kernel_dilate, iterations=1)
			
			# Encontrar contornos
			contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
			
			orbs = []
			
			# Imagen de debug si está activo
			debug_img = img_bgr.copy() if self.energy_loading_active else None
			
			for contour in contours:
				area = cv.contourArea(contour)
				
				# MEJORADO: Rango de área más flexible
				if not (30 < area < 5000):
					continue
				
				# Calcular circularidad
				perimeter = cv.arcLength(contour, True)
				if perimeter == 0:
					continue
				
				circularity = 4 * np.pi * area / (perimeter * perimeter)
				
				# MEJORADO: Circularidad más permisiva
				if circularity < 0.3:
					continue
				
				# Calcular centro y bounding box
				M = cv.moments(contour)
				if M['m00'] == 0:
					continue
				
				cx = int(M['m10'] / M['m00'])
				cy = int(M['m01'] / M['m00'])
				
				# Calcular radio aproximado
				radius = int(np.sqrt(area / np.pi))
				
				# MEJORADO: Calcular brillo promedio del orbe
				x, y, w, h = cv.boundingRect(contour)
				orb_region = img_hsv[y:y+h, x:x+w]
				avg_brightness = np.mean(orb_region[:, :, 2])
				
				# Filtrar por brillo
				if avg_brightness < 100:
					continue
				
				# Coordenadas de pantalla
				screen_x = search_region['x'] + cx
				screen_y = search_region['y'] + cy
				
				orbs.append({
					'x': screen_x,
					'y': screen_y,
					'radius': radius,
					'area': area,
					'circularity': circularity,
					'brightness': avg_brightness,
					'local_x': cx,
					'local_y': cy
				})
				
				# Dibujar en debug si está activo
				if debug_img is not None:
					# Cuadrado verde alrededor del orbe
					box_size = max(radius * 2, 30)
					top_left = (cx - box_size//2, cy - box_size//2)
					bottom_right = (cx + box_size//2, cy + box_size//2)
					cv.rectangle(debug_img, top_left, bottom_right, (0, 255, 0), 3)
					
					# Círculo rojo en el centro
					cv.circle(debug_img, (cx, cy), 5, (0, 0, 255), -1)
					
					# Texto con info
					text = f"#{len(orbs)} B:{int(avg_brightness)}"
					cv.putText(debug_img, text, (cx - 30, cy - box_size//2 - 5),
							 cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
			
			# Ordenar por distancia al centro
			center_x = screen_width // 2
			center_y = screen_height // 2
			
			orbs.sort(key=lambda o: 
				np.sqrt((o['x'] - center_x)**2 + (o['y'] - center_y)**2)
			)
			
			# Agregar indicador del más cercano en debug
			if debug_img is not None and len(orbs) > 0:
				closest = orbs[0]
				# Marcar el más cercano con borde amarillo más grueso
				box_size = max(closest['radius'] * 2, 30)
				top_left = (closest['local_x'] - box_size//2, closest['local_y'] - box_size//2)
				bottom_right = (closest['local_x'] + box_size//2, closest['local_y'] + box_size//2)
				cv.rectangle(debug_img, top_left, bottom_right, (0, 255, 255), 5)
				
				# Agregar contador total
				cv.putText(debug_img, f"Total Orbs: {len(orbs)}", (10, 30),
						 cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
			
			if debug_img is not None:
				return orbs, debug_img
			
			return orbs
			
		except Exception as e:
			self.terminal(f'Error detecting orbs: {str(e)}', 'warn')
			if self.energy_loading_active:
				return [], None
			return []

	def collect_energy_orb(self, orb):
		"""
		Recolectar un orbe de energía individual
		"""
		try:
			# Click en el orbe
			self.click(orb['x'], orb['y'])
			sleep(0.6)
			
			# Usar collector
			collector_slot = self.checkSkill("collector")
			if collector_slot:
				self.skill(collector_slot)
				sleep(0.4)
			
			return True
		except Exception as e:
			self.terminal(f'Error collecting orb: {str(e)}', 'warn')
			return False

	def toggle_energy_loading(self):
		"""
		Activar/Desactivar modo de carga infinita de energía
		"""
		self.energy_loading_active = not self.energy_loading_active
		
		if self.energy_loading_active:
			self.terminal('⚡ ENERGY LOADING: ACTIVADO (Presiona E para desactivar)', 'info')
			self.energy_debug_window_active = True
			# Iniciar thread de carga
			from threading import Thread
			self.energy_loading_thread = Thread(target=self._energy_loading_loop)
			self.energy_loading_thread.daemon = True
			self.energy_loading_thread.start()
		else:
			self.terminal('⚡ ENERGY LOADING: DESACTIVADO', 'warn')
			self.energy_debug_window_active = False
			# Cerrar ventana de debug
			try:
				cv.destroyAllWindows()
			except:
				pass
		
		return self.energy_loading_active

	def _energy_loading_loop(self):
		"""
		Loop infinito de carga de energía con overlay en tiempo real
		"""
		collected_total = 0
		cycle = 0
		
		# Importar y crear overlay
		overlay = None
		try:
			# Asegurarse de que hay una QApplication
			from PyQt5.QtWidgets import QApplication
			if QApplication.instance() is None:
				self.terminal('⚠ No hay QApplication, overlay deshabilitado', 'warn')
				overlay = None
			else:
				# Importar overlay
				import sys
				import os
				sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'enhanced'))
				
				from energy_overlay import EnergyOverlay
				
				overlay = EnergyOverlay()
				overlay.show()
				self.terminal('✓ Overlay de detección activado', 'info')
		except Exception as e:
			self.terminal(f'⚠ Error creando overlay: {str(e)}', 'warn')
			overlay = None
		
		while self.energy_loading_active and not self.stopped:
			cycle += 1
			
			# Pausar si el bot está pausado
			if self.paused:
				sleep(0.5)
				continue
			
			try:
				# Detectar orbes
				orbs = self.detect_energy_orbs()
				
				# Actualizar overlay
				if overlay is not None:
					try:
						overlay.set_orbs(orbs, collected_total, cycle)
						from PyQt5.QtWidgets import QApplication
						QApplication.processEvents()
					except Exception as e:
						self.terminal(f'Error actualizando overlay: {str(e)}', 'warn')
				
				if not orbs:
					sleep(1)
					continue
				
				# Recolectar orbe #1 (más cercano)
				orb = orbs[0]
				
				if self.collect_energy_orb(orb):
					collected_total += 1
					
					# Log cada 5 orbes
					if collected_total % 5 == 0:
						self.terminal(f'  ⚡ Orbes recolectados: {collected_total}', 'info')
				
				# Pequeña pausa entre recolecciones
				sleep(0.3)
				
			except Exception as e:
				self.terminal(f'Error en energy loop: {str(e)}', 'warn')
				sleep(1)
		
		# Cerrar overlay al terminar
		if overlay is not None:
			try:
				overlay.close_overlay()
			except:
				pass
		
		self.energy_debug_window_active = False
		self.terminal(f'✓ Energy loading finalizado: {collected_total} orbes totales', 'info')
	def auto_collect_energy(self, max_orbs=10, timeout=30):
		"""
		Recolectar orbes de energía (modo manual limitado)
		DEPRECADO: Usar toggle_energy_loading() para modo infinito
		"""
		start_time = time()
		collected = 0
		
		self.terminal('⚡ Iniciando carga de energía...', 'info')
		
		while collected < max_orbs and time() - start_time < timeout:
			# Detectar orbes
			result = self.detect_energy_orbs()
			orbs = result[0] if isinstance(result, tuple) else result
			
			if not orbs:
				self.terminal('  No se detectaron orbes', 'warn')
				break
			
			# Recolectar el más cercano
			orb = orbs[0]
			self.terminal(f'  → Recolectando orbe {collected+1}/{max_orbs}', 'info')
			
			if self.collect_energy_orb(orb):
				collected += 1
			
			sleep(0.5)
		
		elapsed = time() - start_time
		self.terminal(f'✓ Carga completada: {collected} orbes en {elapsed:.1f}s', 'info')
		return collected

	# Check time passed since last check
	def checkTimePassed(self, delta, secs):
		if self.dtime[delta] == 0:
			self.dtime[delta] = datetime.datetime.fromtimestamp(self.dtime[delta])
		if datetime.timedelta.total_seconds(datetime.datetime.now()-self.dtime[delta]) >= secs:
			self.dtime[delta] = datetime.datetime.now()
			return True
		return False