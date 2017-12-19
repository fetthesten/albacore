import numpy as np
import math
import pygame
from pygame import Color

class NoiseMap:
    def __init__(self, noise_size = 32, loc = 1.0, scale = 2.0):
        self.noise = np.random.normal(loc, scale, (noise_size, noise_size))
        self.maxnoise = -10000000.0
        self.minnoise = 10000000.0
        self.color_schemes = {}
        self.init_colors()
            
        for y in range(noise_size):
            for x in range(noise_size):
                sample = self.noise[y][x]
                if sample > self.maxnoise:
                    self.maxnoise = sample
                elif sample < self.minnoise:
                    self.minnoise = sample
        self.noise_span = self.maxnoise - self.minnoise

    def init_colors(self):
        self.color_schemes['land'] = self.make_gradient([Color(0, 0, 64, 255),
                                          Color(0, 0, 96, 255),
                                          Color(0, 0, 128, 255),
                                          Color(0, 0, 255, 255),
                                          Color(255, 255, 0, 255),
                                          Color(0, 255, 0, 255),
                                          Color(192, 192, 192, 255)])
        self.color_schemes['neon'] = self.make_gradient([Color(255, 0, 255, 255),
                                          Color(255, 255, 0, 255),
                                          Color(0, 255, 255, 255)],
                                          8)
        self.color_schemes['grayscale'] = self.make_gradient([Color(0, 0, 0, 255),
                                          Color(255, 255, 255, 255)],
                                          255)
    def combine_maps(self, map1, map2, cell_size = 1, tm1 = 1.0, tm2 = 1.0, offset = 0.0, uniform = 1.0):
        size = min(len(map1[0]), len(map2[0]))
        result = []
        for y in range(0, size, cell_size):
            for app in range(cell_size):
                result.append([])
            for x in range(0, size, cell_size):
                samples = []
                for sy in range(cell_size):
                    for sx in range(cell_size):
                        samples.append((map1[y + sy][x + sx] * tm1) * (map2[y + sy][x + sx] * tm2))
                avg = sum(samples) / len(samples)
                s = 0
                for ry in range(cell_size):
                    for rx in range(cell_size):
                        #result[y + ry].append(self.lerp(samples[s], avg, uniform) + offset)
                        result[y + ry].append(avg + offset)
                        s+=1
        return result
        
    def get_smooth_map(self, noise_size = None):
        if not noise_size:
            noise_size = len(self.noise[0])
        half = noise_size / 2
        smooth_map = []
        step = 1 / half
        for y in range(noise_size):
            smooth_map.append([])
            iy = 0
            if y < half:
                iy = step * y
            else:
                iy = step * (half - (y % half))
            for x in range(noise_size):
                ix = 0
                if x < half:
                    ix = step * x
                else:
                    ix = step * (half - (x % half))
                smooth_map[y].append(ix * iy)
        return smooth_map
        
    def get_map(self, selected_map = None, colors = None, scaled = False):
        if not selected_map:
            selected_map = self.noise
            scaled = True
        if not colors:
            # default to first color scheme
            colors = next(iter(self.color_schemes.values()))
        elif isinstance(colors, str):
            # do a lookup 
            colors = self.color_schemes[colors]
            # otherwise assume color scheme has been sent
        map_size = len(selected_map[0])
        surf = pygame.Surface((map_size,map_size))
        for y in range(map_size):
            for x in range(map_size):
                sample = selected_map[y][x]
                color_index = self.get_color_index(sample, colors, scaled)
                color_index = max(0, min(color_index, len(colors)-1))
                surf.set_at((x,y), colors[color_index])
        return surf
    
    def get_color_index(self, sample, colors, scale = True):
        scaled = sample
        if scale:
            scaled = float(sample - self.minnoise) / float(self.noise_span)
        return int(math.floor(scaled * len(colors)))

    def make_gradient(self, colors, stops = 4, opacity = 255):
        # stops is per-color
        i = 1 / stops
        result = []

        for l in range(len(colors) - 1):
            c1 = colors[l]
            n = l if l is (len(colors) - 1) else l + 1
            c2 = colors[n]
            for s in range(stops):
                p = s * i
                new_color = Color(self.lerp(c1.r, c2.r, p),
                                  self.lerp(c1.g, c2.g, p),
                                  self.lerp(c1.b, c2.b, p),
                                  opacity)
                result.append(new_color)
        return result

    def lerp(self, a, b, c):
        return int(math.floor((c * b) + ((1 - c) * a)))

if __name__ == '__main__':
    
    import os.path
    
    pygame.init()
    nm = NoiseMap(128)
    nm.smooth_map = nm.get_smooth_map()
    collision = True
    img_num = 0
    fname = ''
    while collision:
        fname = os.path.join('data', 'scr', 'img') + str(img_num) + '.bmp'
        img_num += 1
        if not os.path.isfile(fname):
            collision = False
    smoothed_map = nm.combine_maps(nm.noise, nm.smooth_map, 4, 0.8, 1.0, 0.2, 1.0)
    pygame.image.save(nm.get_map(smoothed_map, 'land', False), fname)
    fname2 = os.path.join('data', 'scr', 'img') + str(img_num)+'.bmp'
    pygame.image.save(nm.get_map(smoothed_map, 'grayscale'), fname2)
    print('* saved',fname,'+',fname2,'*')
