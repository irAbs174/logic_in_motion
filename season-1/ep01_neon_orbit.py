"""
Logic in Motion — Episode 01: Neon Orbit Bloom
BEGINNER spirograph (Python turtle)

How to run:
  1. Save as orbit.py
  2. python orbit.py
"""

import math
import turtle

screen = turtle.Screen()
screen.setup(800, 800)
screen.bgcolor("#070A0F")
screen.title("Logic in Motion — Neon Orbit")
screen.tracer(0, 0)

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.pensize(2)


def spiro(R, r, d, n):
    for i in range(n):
        t = i * 0.07
        x = (R - r) * math.cos(t) + d * math.cos(((R - r) / r) * t)
        y = (R - r) * math.sin(t) - d * math.sin(((R - r) / r) * t)
        pen.goto(x, y)


pen.penup()
pen.goto(0, 0)
pen.pendown()
spiro(195, 59, 92, 360)

screen.update()
turtle.done()
