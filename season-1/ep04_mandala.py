"""
Logic in Motion — Episode 04: Digital Mandala
BEGINNER radial mandala (Python turtle)

How to run:
  1. Save as mandala.py
  2. python mandala.py
"""

import math
import turtle

screen = turtle.Screen()
screen.setup(800, 800)
screen.bgcolor("#070A0F")
screen.title("Logic in Motion — Digital Mandala")
screen.tracer(0, 0)

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.pensize(2)

PETALS = 12
LAYERS = 6


def petal(inner, outer, angle, span):
    pen.penup()
    xi = inner * math.cos(math.radians(angle))
    yi = inner * math.sin(math.radians(angle))
    pen.goto(xi, yi)
    pen.pendown()

    for i in range(11):
        t = angle - span / 2 + i * span / 10
        rad = math.radians(t)
        x = outer * math.cos(rad)
        y = outer * math.sin(rad)
        pen.goto(x, y)


for layer in range(LAYERS):
    off = layer * (360 / PETALS / 2)
    outer = 200 - layer * 28
    inner = max(22, outer - 28 + 12)
    for p in range(PETALS):
        petal(inner, outer, p * (360 / PETALS) + off, 14)

screen.update()
turtle.done()
