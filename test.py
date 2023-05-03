
import torch
from typing import Optional

from abc import abstractmethod
import os
from PIL import Image


import numpy as np

mesh_path = "/home/hcygh1/python projects/textured-3d-gan/mesh_templates/classes/batch1seed_train1.obj"
vertices = []
faces = []
face_textures = []
uvs = []
with open(mesh_path, 'r') as mesh:
    for line in mesh:
        data = line.split()
        if len(data) == 0:
            continue
        if data[0] == 'v':
            vertices.append(data[1:])
        elif data[0] == 'vt':
            uvs.append(data[1:3])
        elif data[0] == 'f':
            if '//' in data[1]:
                data = [da.split('//') for da in data]
                faces.append([int(d[0]) for d in data[1:]])
                face_textures.append([int(d[1]) for d in data[1:]])
            elif '/' in data[1]:
                data = [da.split('/') for da in data]
                faces.append([int(d[0]) for d in data[1:]])
                face_textures.append([int(d[1]) for d in data[1:]])
            else:
                faces.append([int(d) for d in data[1:]])
                continue
vertices = torch.FloatTensor([float(el) for sublist in vertices for el in sublist]).view(-1, 3)
three=0
four=0
more=0
for i in faces:
    if len(i)==3:
        three+=1
    elif len(i)==4:
        four+=1
    else:
        more+=1
        
print(three)
print(four)
print(more)

faces = torch.LongTensor(faces) - 1
