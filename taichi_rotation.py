# reference ==>

from operator import truediv
import taichi as ti

ti.init(arch = ti.gpu)

res_x = 512
res_y = 512
r_big = 200.0
r_part =  100.0 
r_small = 40.0
r_out = 205.0

pixels = ti.Vector.field(3, ti.f32, shape=(res_x, res_y))




@ ti.func
def circle(pos, center, radius):
    r = (pos - center).norm()
    t = 0
    if r <= radius:
        t = 1
    return t


@ti.kernel
def render(t:ti.f32, scale:float):
    r_big = r_big / scale
    r_part = r_part / scale
    r_small = r_small / scale
    r_out = r_out / scale
    center = ti.Vector([res_x//2, res_y//2]) / scale


    center_up = ti.Vector([center[0], (center[1] - r_big + center[1]) / 2])
    center_down = ti.Vector([center[0], (center[1] + r_big + center[1]) / 2])
    
    for i,j in pixels:
        color = ti.Vector([0.0, 0.0, 0.0]) # init your canvas to white
        posScale = ti.Vector([i, j]) / scale
        sumColor = ti.math.vec3(0.0, 0.0, 0.0)
        for m in range(0, ti.cast(1 / scale, ti.int32)):
            for n in range(0, ti.cast(1 / scale, ti.int32)):
                pos = ti.math.vec2([posScale[0] + m], posScale[1] + n)

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
                sumColor += color
        pixels[i, j] = sumColor / (ti.cast(1 / scale, ti.int32) ** 2)
        center_raw = center * scale
        r_out_raw = r_out * scale
        # rotation 
        # if circle(ti.math.vec2(i, j), center_raw, r_out_raw) != 0:
        #     i_ = ti.cast((i - center_raw[0]) * ti.math.cos(t) - (j - center_raw[1]) * ti.math.sin(t) + center_raw[0], ti.int32)
        #     j_ = ti.cast((i - center_raw[0]) * ti.math.sin(t) + (j - center_raw[1]) * ti.math.cos(t) + center_raw[1], ti.int32)
        #     pixels[i_, j_] = sumColor / (ti.cast(1 / scale, ti.int32) ** 2)
        # else:
        #     pixels[i, j] = ti.math.vec3(1.0, 1.0, 1.0)



gui = ti.GUI("taichi logo", res=(res_x, res_y))
run = False
for i in range(10000000000000):
    t = i * 0.01
    if not run:
        run = True
        render(t, 1.0/1024)
        gui.set_image(pixels)
        gui.show()
