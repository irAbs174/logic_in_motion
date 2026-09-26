"""
Logic in Motion — Episode 07: The Dance of Circles
BEGINNER classic spirograph (Python turtle)

How to run:
  1. Save as spirograph.py
  2. python spirograph.py
"""

import math
import turtle

screen = turtle.Screen()
screen.setup(800, 800)
screen.bgcolor("#070A0F")
screen.title("Logic in Motion — Dance of Circles")
screen.tracer(0, 0)

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.pensize(2)
pen.color("#00DCFF")


def spiro(R, r, d, n):
    for i in range(n):
        t = i * 0.05
        k = (R - r) / r
        x = (R - r) * math.cos(t) + d * math.cos(k * t)
        y = (R - r) * math.sin(t) - d * math.sin(k * t)
        if i == 0:
            pen.penup()
            pen.goto(x, y)
            pen.pendown()
        else:
            pen.goto(x, y)


# Classic gear ratios — R=120, r=45, d=90
spiro(120, 45, 90, 720)

screen.update()
turtle.done()
