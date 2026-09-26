"""
Logic in Motion — Episode 05: Ice Crystals
BEGINNER Koch snowflake (Python turtle)

How to run:
  1. Save as snowflake.py
  2. python snowflake.py
"""

import turtle

screen = turtle.Screen()
screen.setup(800, 800)
screen.bgcolor("#070A0F")
screen.title("Logic in Motion — Ice Crystals")
screen.tracer(0, 0)

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.pensize(2)
pen.color("#7EE8FF")

pen.penup()
pen.goto(-150, -90)
pen.setheading(0)
pen.pendown()


def koch(length, n):
    if n == 0:
        pen.forward(length)
        return
    koch(length / 3, n - 1)
    pen.left(60)
    koch(length / 3, n - 1)
    pen.right(120)
    koch(length / 3, n - 1)
    pen.left(60)
    koch(length / 3, n - 1)


for _ in range(3):
    koch(300, 4)
    pen.right(120)

screen.update()
turtle.done()
