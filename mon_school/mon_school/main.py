import turtle
import math
import random
turtle.speed(0)
turtle.home()
def circ(cl,r): 
    turtle.begin_fill()
    turtle.fillcolor(cl)
    turtle.speed(0)
    turtle.pen(pencolor=cl,pensize="1")
    turtle.pu()
    turtle.rt(90)
    turtle.fd(r)
    turtle.left(90)
    turtle.down()
    turtle.circle(r)
    turtle.end_fill()
    turtle.pu()
    turtle.home()
    turtle.down()
def square(size):
    for i in range(4):
        turtle.fd(size)
        turtle.lt(90)
def big_flower(shade):
    for i in range(13):
        turtle.up()
        turtle.goto(0,0)
        turtle.down()
        turtle.fillcolor(shade)
        turtle.pen(pencolor=shade,pensize="1")
        turtle.begin_fill()
        turtle.circle(305,70)
        turtle.left(110)
        turtle.circle(305,70)
        turtle.end_fill()
        turtle.right(1)
def draw_square(square,lll,cll):
    for i in range(0,2):
        square.begin_fill()
        square.fillcolor(cll)
        square.forward(lll)
        square.right(30)
        square.forward(lll)
        square.right(150)
        square.end_fill()


def draw_flower(coll,sizz):
	window = turtle.Screen()
	window.bgcolor("white")

	hello = turtle.Turtle()
	hello.speed(0)
	hello.shape("triangle")
    #turtle.pen(pencolor="99FF00",pensize="1")
	hello.color(coll)

	for i in range(0,36):
		draw_square(hello,sizz,coll)
		hello.right(10)
def petal(t, r, angle):
    """Use the Turtle (t) to draw a petal using two arcs
    with the radius (r) and angle.
    """
    for i in range(2):
        t.circle(r,angle)
        t.left(180-angle)

def flower(t, n, r, angle):
    """Use the Turtle (t) to draw a flower with (n) petals,
    each with the radius (r) and angle.
    """
    for i in range(n):
        petal(t, r, angle)
        t.left(360.0/n)
turtle.pen(pencolor="#770E13",pensize="1")
circ("#770E13",400)
turtle.pen(pencolor="#E67B47",pensize="1")
circ("#E67B47",390)
turtle.pen(pencolor="#ECE19F",pensize="1")
circ("#ECE19F",380)
turtle.begin_fill()
turtle.pen(pencolor="red",pensize="1")
turtle.fillcolor("red")
turtle.speed(0)
turtle.pen(pencolor="red",pensize="1")
for k in range(40):
    square(270)
    turtle.rt(10)
turtle.end_fill()
turtle.pen(pencolor="orange",pensize="1")
circ("orange",350)
turtle.pen(pencolor="#383629",pensize="1")
big_flower("#383629")
turtle.right(60)
turtle.pen(pencolor="#EFE19A",pensize="1")
big_flower("#EFE19A")
turtle.pen(pencolor="#C8520A",pensize="1")
turtle.right(60)
big_flower("#C8520A")
turtle.pen(pencolor="red",pensize="1")
circ("red",280)


t = turtle.Turtle()
t.speed(0)
####draw_flower("#ECE19F",150)##################################
turtle.begin_fill()
turtle.pen(pencolor="#ECE19F",pensize="1")
turtle.fillcolor("#ECE19F")
turtle.speed(0)
turtle.pen(pencolor="#ECE19F",pensize="1")
for k in range(12):
    square(197)
    turtle.rt(30)  
turtle.end_fill()
turtle.pen(pencolor="#FFD504",pensize="1")
t.begin_fill()
#turtle.pen(pencolor="#FFD504",pensize="1")
t.fillcolor("#FFD504")
for k in range(12):
    for i in range(6):
        t.forward(140)
        t.right(60) 
    t.rt(30)
t.end_fill()
#draw_flower()
turtle.pen(pencolor="#F4E389",pensize="1")
circ("#F4E389",250)
draw_flower("orange",129)
turtle.pen(pencolor="#E67B47",pensize="1")
circ("#E67B47",220)
turtle.pen(pencolor="#2E7644",pensize="1")
circ("#2E7644",210)

turtle.begin_fill()
turtle.pen(pencolor="orange",pensize="1")
turtle.fillcolor("orange")
#draw_flower()
for k in range(40):
    square(148)
    turtle.rt(10)
turtle.end_fill()
turtle.speed(0)
turtle.pen(pencolor="#F4E389",pensize="1")
circ("#F4E389",160)
turtle.speed(0)
turtle.begin_fill()
turtle.pen(pencolor="red",pensize="1")
turtle.fillcolor("red")
#draw_flower()
for k in range(9):
    for i in range(6):
        turtle.forward(100) #Assuming the side of a hexagon is 100 units
        turtle.right(60) #Turning the turtle by 60 degree
    turtle.rt(40)
turtle.end_fill()
turtle.pen(pencolor="#C8520A",pensize="1")#ECE19F
circ("#C8520A",172)
turtle.pen(pencolor="#770E13",pensize="1")
circ("#770E13",162)
turtle.pen(pencolor="#E67B47",pensize="1")
circ("#E67B47",152)
turtle.pen(pencolor="orange",pensize="1")
circ("orange",142)
turtle.begin_fill()
turtle.fillcolor("#383629")
turtle.pen(pencolor="#383629",pensize="1")
flower(turtle, 9, 140.0, 60.0)
turtle.end_fill()
turtle.lt(30)
turtle.begin_fill()
turtle.fillcolor("#EFE19A")
turtle.pen(pencolor="#EFE19A",pensize="1")
flower(turtle, 9, 140.0, 60.0)
turtle.end_fill()
turtle.lt(30)
turtle.begin_fill()
turtle.fillcolor("#C8520A")
turtle.pen(pencolor="#C8520A",pensize="1")
flower(turtle, 9, 140.0, 60.0)
turtle.end_fill()
turtle.lt(30)
turtle.pen(pencolor="orange",pensize="1")
for k in range(6):
    turtle.begin_fill()
    if k%2==0:
        turtle.pen(pencolor="yellow",pensize="1")
        turtle.fillcolor("yellow")
    else:
        turtle.pen(pencolor="orange",pensize="1")
        turtle.fillcolor("orange")
    square(40)
    turtle.rt(60)
    turtle.end_fill()
turtle.exitonclick()


    

    
    
    