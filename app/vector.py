from math import sqrt, acos

def sqre(x):
    return x * x

class Vector(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def increase(self, s):
        self.x = self.x + s
        self.y = self.y + s
    def decrease(self, s):
        self.x = self.x - s
        self.y = self.y - s
    def scalar(self, s):
        self.x = self.x * s
        self.y = self.y * s
    def shrink(self, s):
        self.x = self.x / s
        self.y = self.y / s
    def add(self, v):
        self.x = self.x + v.x
        self.y = self.y + v.y
    def add2(self, x, y):
        self.x = self.x + x
        self.y = self.y + y
    def subtract(self, v):
        self.x = self.x - v.x
        self.y = self.y - v.y
    def subtract2(self, x, y):
        self.x = self.x - x
        self.y = self.y - y
    def normalize(self):
        return Vector(self.x / self.magnitude(), self.y / self.magnitude())
    def magnitude(self):
        return sqrt(sqre(self.x) + sqre(self.y))
    def magnitude2(self):
        return self.x * self.x + self.y * self.y
    def dot(self, v):
        return self.x * v.x + self.y * v.y
    def theta(self, v):
        return acos(self.normalize().dot(v.normalize()))
    def __str__(self):
        return "<Vector %s:%s>" % (self.x, self.y)
    def __repr__(self):
        return "<Vector %s:%s>" % (self.x, self.y)