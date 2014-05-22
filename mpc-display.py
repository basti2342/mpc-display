#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame, pygame.mouse, logging, os, subprocess, sys
from pygame.locals import *
from textrect import render_textrect, TextRectException
import time

# windowed mode if True
DEBUG = True

class MpcTicker:
	def __init__(self):
		"Ininitializes a new pygame screen using the framebuffer"

		if DEBUG:
			logging.info("DEBUG MODE")
			self.screen = pygame.display.set_mode((640, 480))
		else:
			# Based on "Python GUI in Linux frame buffer"
			# http://www.karoltomala.com/blog/?p=679
			dispNo = os.getenv("DISPLAY")
			if dispNo:
				logging.info("I'm running under X display = %s" % dispNo)

			# Check which frame buffer drivers are available
			# Start with fbcon since directfb hangs with composite output
			drivers = ["fbcon", "directfb", "svgalib"]
			found = False
			for driver in drivers:
				# Make sure that SDL_VIDEODRIVER is set
				if not os.getenv("SDL_VIDEODRIVER"):
					os.putenv("SDL_VIDEODRIVER", driver)
				try:
					pygame.display.init()
				except pygame.error:
					logging.warning("Driver: %s failed." % driver)
					continue
				found = True
				break

			if not found:
				logging.critical("No suitable video driver found! Are you root?")
				raise Exception("No suitable video driver found! Are you root?")

			size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
			logging.info("Framebuffer size: %d x %d" % (size[0], size[1]))
			self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

		pygame.mouse.set_visible(False)
		pygame.font.init()

	def nowPlaying(self):
		mpcCall = ["mpc"] + sys.argv[1:]
		inp, err = subprocess.Popen(mpcCall, stdout=subprocess.PIPE).communicate()
		inp = inp.split("\n")
		if len(inp) > 2:
			inp = inp[0]
		else:
			inp = "(paused)"

		# ugly umlaut replacement ahead (font does not support them)
		inp = inp.replace("ö", "oe")
		inp = inp.replace("ä", "ae")
		inp = inp.replace("ü", "ue")
		inp = inp.replace("ß", "ss")
		return inp

	def show(self):
		headlineFont = pygame.font.Font("leddigital.ttf", 70)
		font = pygame.font.Font(None, 50)
		run = True
		while run:
			inp = self.nowPlaying()

			# quit on "window close" and Escape
			for evt in pygame.event.get():
				if evt.type == KEYDOWN:
					if evt.key == K_ESCAPE:
						run = False
				elif evt.type == QUIT:
					return
			self.screen.fill((0, 0, 0))

			headline = headlineFont.render("mpd - Now playing:", True, (255, 0, 0))
			self.screen.blit(headline, (0, 0))

			# try to render all text and cut off if it's too large
			textRendered = False

			while not textRendered:
				try:
					# draw text and handle line breaks properly
					textSurface = render_textrect(inp, headlineFont, \
						self.screen.get_rect(), (255, 255, 255), (0, 0, 0))
					textRendered = True
				except TextRectException:
					# cut char off
					inp = inp[:-1]

			self.screen.blit(textSurface, (0, 120))
			pygame.display.flip()
			time.sleep(1)

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG,
		format="%(asctime)s %(levelname)-8s %(message)s",
		datefmt="%Y.%m.%d %H:%M:%S")
	mpc = MpcTicker()
	mpc.show()
	pygame.quit()
