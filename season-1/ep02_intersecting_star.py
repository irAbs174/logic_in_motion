"""
Logic in Motion — Episode 02: The Birth of a Star
BEGINNER intersecting polygons (Python turtle)

How to run:
  1. Save as star.py
  2. python star.py
"""

import math
import turtle

screen = turtle.Screen()
screen.setup(800, 800)
screen.bgcolor("#070A0F")
screen.title("Logic in Motion — Birth of a Star")
screen.tracer(0, 0)

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.pensize(2)


def polygon(n, r, rot):
    pts = []
    for i in range(n):
        a = math.radians(rot + i * 360 / n)
        pts.append((r * math.cos(a), r * math.sin(a)))
    for i in range(n):
        pen.penup()
        pen.goto(pts[i])
        pen.pendown()
        pen.goto(pts[(i + 1) % n])


for layer in range(8):
    polygon(12, 195 - layer * 7, layer * 7.5)

screen.update()
turtle.done()
