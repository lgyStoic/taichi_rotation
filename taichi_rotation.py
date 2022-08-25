# reference ==>

import taichi as ti

ti.init(arch = ti.cuda)

res_x = 512
res_y = 512
r_big = 200.0
pixels = ti.Vector.field(3, ti.f32, shape=(res_x, res_y))

@ ti.func
def circle(pos, center, radius):
    r = (pos - center).norm()
    t = 0
    if r < radius:
        t = 1
    return t
@ti.func
def smoothstep(edge0, edge1, x):
    t = (x - edge0) / (edge1 - edge0)
    t = ti.max(0, ti.min(1, t))
    return (3 - 2 * t) * t * t



@ti.kernel
def render(t:ti.f32):
    center = ti.Vector([res_x//2, res_y//2])


    center_up = ti.Vector([center[0], (center[1] - r_big + center[1]) / 2])
    center_down = ti.Vector([center[0], (center[1] + r_big + center[1]) / 2])
    r_part =  100.0 
    r_small = 40.0
    r_out = 205.0
    for i,j in pixels:
        color = ti.Vector([0.0, 0.0, 0.0]) # init your canvas to white
        pos = ti.Vector([i, j])
        
        c = circle(pos, center, r_big)
        c_up_small = circle(pos, center_up, r_small)
        c_down_small =  circle(pos, center_down, r_small)
        c_up_big = circle(pos, center_up, r_part)
        c_down_big = circle(pos, center_down, r_part)
        c_out = circle(pos, center, r_out)
        if c_up_small:
            color = ti.Vector([1.0, 1.0, 1.0])
        elif c_down_small:
            color = ti.Vector([0.0, 0.0, 0.0])
        elif c_up_big:
            color = ti.Vector([0.0, 0.0, 0.0])
        elif c_down_big:
            color = ti.Vector([1.0, 1.0, 1.0])
        elif c:
            if pos[0] < center[0]:
                color = ti.Vector([0.0, 0.0, 0.0])
            else:
                color = ti.Vector([1.0, 1.0, 1.0])
        elif c_out:
            color = ti.Vector([0.0, 0.0, 0.0])
        else:
            color = ti.Vector([1.0, 1.0, 1.0])

        # rotation 
        if not c: 
            pixels[i,j] = color
        else:
            i_ = ti.cast((i - center[0]) * ti.math.cos(t) - (j - center[1]) * ti.math.sin(t) + center[0], ti.int32)
            j_ = ti.cast((i - center[0]) * ti.math.sin(t) + (j - center[1]) * ti.math.cos(t) + center[1], ti.int32)
            pixels[i_, j_] = color
@ti.kernel
def smooth():
    center = ti.math.vec2(res_x // 2, res_y // 2)
    for i,j in pixels:
        r = (ti.math.vec2(i, j) - center).norm()
        d = r / r_big
        pixels[i, j] = smoothstep(0.9, 1, d) * pixels[i, j]



gui = ti.GUI("taichi logo", res=(res_x, res_y))

for i in range(59900):
    t = i * 0.01
    render(t)
    smooth()
    gui.set_image(pixels)
    gui.show()
