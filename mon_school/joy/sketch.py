from joy import Circle, Point, Group, Translate, Scale

_shapes = []

def circle(cx, cy, d):
    c = Circle(center=Point(cx, cy), radius=d/2)
    _shapes.append(c)

def get_shape():
    return Group(_shapes) | Translate(-150, -150) | Scale(sx=1, sy=-1)
