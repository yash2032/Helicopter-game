a = 4
def f():
    global a
    a = 5

f()
print(a)