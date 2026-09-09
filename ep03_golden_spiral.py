"""
Logic in Motion — Episode 03: The Infinite Spiral
BEGINNER golden ratio spiral (Python turtle)

How to run:
  1. Save as spiral.py
  2. python spiral.py
"""

import math
import turtle

screen = turtle.Screen()
screen.setup(800, 800)
screen.bgcolor("#070A0F")
screen.title("Logic in Motion — The Infinite Spiral")
screen.tracer(0, 0)

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.pensize(3)

PHI = 1.618
TURNS = 6


def golden_spiral(a, turns, n):
    pen.penup()
    for i in range(n):
        t = i / n * turns * 2 * math.pi
        r = a * PHI ** (t / (2 * math.pi))
        x = r * math.cos(t)
        y = r * math.sin(t)
        if i == 0:
            pen.goto(x, y)
            pen.pendown()
        else:
            pen.goto(x, y)


golden_spiral(5, TURNS, 240)

screen.update()
turtle.done()
