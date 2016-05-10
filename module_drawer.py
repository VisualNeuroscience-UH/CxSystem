__author__ = 'V_AD'
import turtle

def module_drawer():
    def __init__(self):
        frame_drawer()

def frame_drawer():
    x_size = 1000
    y_size = 500
    x_home = -x_size/2
    y_home = -y_size/2
    turtle.pu()
    layer_names = ['VI', 'V', 'IV', 'III/II', 'I']
    headers = ['Layers', 'N', 'SS', 'PC' ,'BC','MC' , 'L1I']
    turtle.pu()
    turtle.goto(x_home + 40,y_home+50)
    turtle.pd()
    turtle.write(layer_names[0], font=("Arial", 15, "normal"))
    for i in range(1,6):
        if i < 5:
            turtle.pu()
            turtle.goto(x_home + 40,y_home+100*i + 50)
            turtle.pd()
            turtle.write(layer_names[i], font=("Arial", 15, "normal"))
            turtle.pu()
        turtle.goto(x_home,y_home+100*i)
        current = 0
        while current <x_size :
            turtle.pd()
            turtle.fd(30)
            turtle.pu()
            turtle.fd(30)
            current += 60
    for i in range(0,5):
        turtle.pu()
        turtle.goto(x_home + 30 + 150*i,y_home+ y_size + 50)
        turtle.pd()
        turtle.write(headers[i], font=("Arial", 12, "normal"))
    current = 0
    turtle.pu()
    turtle.goto(x_home+100,y_home+y_size + 60)
    turtle.right(90)
    turtle.pd()
    while current <y_size :
        turtle.pd()
        turtle.fd(30)
        turtle.pu()
        turtle.fd(30)
        current += 60

frame_drawer()