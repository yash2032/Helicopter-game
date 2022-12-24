
import glfw
import glm
import OpenGL
from OpenGL.GL import*
import ctypes
import numpy as np
from OpenGL.GL.shaders import compileProgram, compileShader
import math as m
from PIL import Image
from glfw.GLFW import *
scale = 0.5
subdiv = 5
v_shader="""
#version 330
layout(location=0)in vec3 position;
layout(location=1)in vec2 tex_coord;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 transform;
out vec2 f_tex_coord;
void main()
{
    f_tex_coord=tex_coord;
    gl_Position= transform * view * model * projection * vec4(position,1.0);
    //gl_Position= transform * vec4(position,1.0);
}
"""

f_shader="""
#version 330
in vec2 f_tex_coord;
uniform sampler2D s_texture;
out vec4 out_colour;
void main()
{
    out_colour=texture(s_texture,f_tex_coord);
}
"""
if not glfw.init():
    raise Exception("Error")

window=glfw.create_window(800,600,"Solar System",None,None)

if not window:
    glfw.terminate()
    raise Exception("Error")

glfw.make_context_current(window)
glfw.set_window_pos(window,50,50)
glClearColor(0.0,0.0,0.0,1.0)

middle_point_cache = {}
#-------------------------------------------------------------------------
def vertex(x, y, z):
    
    length = m.sqrt(x**2 + y**2 + z**2)
    
    return [(i * scale) / length for i in (x,y,z)]        
def middle_point(point_1, point_2):
   
    smaller_index = min(point_1, point_2)
    greater_index = max(point_1, point_2)
    key = '{0}-{1}'.format(smaller_index, greater_index)
    if key in middle_point_cache:
        return middle_point_cache[key]

    vert_1 = verts[point_1]
    vert_2 = verts[point_2]
    middle = [sum(i)/2 for i in zip(vert_1, vert_2)]

    verts.append(vertex(*middle))
    index = len(verts) - 1
    middle_point_cache[key] = index
    return index
#-----------------------------------------------------------------
PHI = (1 + m.sqrt(5)) / 2
verts = [ 
          vertex(-1, PHI, 0),
          vertex( 1, PHI, 0),
          vertex(-1, -PHI, 0),
          vertex( 1, -PHI, 0),
          
          vertex(0, -1, PHI),
          vertex(0, 1, PHI),
          vertex(0, -1, -PHI),
          vertex(0, 1, -PHI),

          vertex( PHI, 0, -1),
          vertex( PHI, 0, 1),
          vertex(-PHI, 0, -1),
          vertex(-PHI, 0, 1),
          ]
faces = [
         # 5 faces around point 0
          [0, 11, 5], 
          [0, 5, 1],
          [0, 1, 7],
          [0, 7, 10],  
          [0, 10, 11],
          # Adjacent faces
          [1, 5, 9],
          [5, 11, 4],   
          [11, 10, 2],  
          [10, 7, 6],
          [7, 1, 8],
          # 5 faces around 3
          [3, 9, 4],    
          [3, 4, 2],
          [3, 2, 6],    
          [3, 6, 8],    
          [3, 8, 9],
          # Adjacent faces
          [4, 9, 5],    
          [2, 4, 11],   
          [6, 2, 10],
          [8, 6, 7],
          [9, 8, 1],
        ]
#-----------------------------------------------------------------
# Subdivisions

for i in range(subdiv):
    faces_subdiv = []
    for tri in faces:
        v1 = middle_point(tri[0], tri[1])
        v2 = middle_point(tri[1], tri[2])
        v3 = middle_point(tri[2], tri[0])
        faces_subdiv.append([tri[0], v1, v3])
        faces_subdiv.append([tri[1], v2, v1])
        faces_subdiv.append([tri[2], v3, v2])
        faces_subdiv.append([v1, v2, v3])

    faces = faces_subdiv
#------------------------------------------------------------------
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

verts = np.array(verts,dtype = np.float32)
verts = verts.flatten()
faces = np.array(faces,dtype = np.uint32)
faces = faces.flatten()

#Shader Program
shaderprograms =compileProgram(compileShader(v_shader,GL_VERTEX_SHADER),
                                 compileShader(f_shader,GL_FRAGMENT_SHADER))
glUseProgram(shaderprograms)
vbo=glGenBuffers(1) 
ibo=glGenBuffers(1)
vao=glGenVertexArrays(1)
########################## vao 
glBindVertexArray(vao)
glBindBuffer(GL_ARRAY_BUFFER,vbo)
glBufferData(GL_ARRAY_BUFFER,verts.nbytes,verts,GL_STATIC_DRAW)
glEnableVertexAttribArray(0)
glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,0,ctypes.c_void_p(0))
glEnableVertexAttribArray(1)
glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,0,ctypes.c_void_p(0))
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,ibo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER,faces.nbytes,faces,GL_STATIC_DRAW)

# --------------  Texture 0 -------------------
mytexture0=glGenTextures(1)
glBindTexture(GL_TEXTURE_2D,mytexture0)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
img=Image.open("sun.jpg",'r')#Read from folder
img=img.transpose(Image.FLIP_TOP_BOTTOM)#Flip image
img_data=img.convert("RGBA").tobytes()
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,img.width,img.height,0,GL_RGBA,
             GL_UNSIGNED_BYTE,img_data)
glBindTexture(GL_TEXTURE_2D,0)

# --------------  Texture 1 -------------------
mytexture1=glGenTextures(1)
glBindTexture(GL_TEXTURE_2D,mytexture1)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
img=Image.open("Mercury.jpg",'r')#Read from folder
img=img.transpose(Image.FLIP_TOP_BOTTOM)#Flip image
img_data=img.convert("RGBA").tobytes()
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,img.width,img.height,0,GL_RGBA,
             GL_UNSIGNED_BYTE,img_data)
glBindTexture(GL_TEXTURE_2D,0)

# --------------  Texture 2 -------------------
mytexture2=glGenTextures(1)
glBindTexture(GL_TEXTURE_2D,mytexture2)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
img=Image.open("Venus.jpg",'r')#Read from folder
img=img.transpose(Image.FLIP_TOP_BOTTOM)#Flip image
img_data=img.convert("RGBA").tobytes()
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,img.width,img.height,0,GL_RGBA,
             GL_UNSIGNED_BYTE,img_data)
glBindTexture(GL_TEXTURE_2D,0)

# --------------  Texture 3 -------------------
mytexture3=glGenTextures(1)
glBindTexture(GL_TEXTURE_2D,mytexture3)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
img=Image.open("Earth.jpg",'r')#Read from folder
img=img.transpose(Image.FLIP_TOP_BOTTOM)#Flip image
img_data=img.convert("RGBA").tobytes()
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,img.width,img.height,0,GL_RGBA,
             GL_UNSIGNED_BYTE,img_data)
glBindTexture(GL_TEXTURE_2D,0)

# --------------  Texture 4 -------------------
mytexture4=glGenTextures(1)
glBindTexture(GL_TEXTURE_2D,mytexture4)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
img=Image.open("Mars.jpg",'r')#Read from folder
img=img.transpose(Image.FLIP_TOP_BOTTOM)#Flip image
img_data=img.convert("RGBA").tobytes()
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,img.width,img.height,0,GL_RGBA,
             GL_UNSIGNED_BYTE,img_data)
glBindTexture(GL_TEXTURE_2D,0)

# --------------  Texture 5 -------------------
mytexture5=glGenTextures(1)
glBindTexture(GL_TEXTURE_2D,mytexture5)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
img=Image.open("Jupiter.jpg",'r')#Read from folder
img=img.transpose(Image.FLIP_TOP_BOTTOM)#Flip image
img_data=img.convert("RGBA").tobytes()
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,img.width,img.height,0,GL_RGBA,
             GL_UNSIGNED_BYTE,img_data)
glBindTexture(GL_TEXTURE_2D,0)

# --------------  Texture 6 -------------------
mytexture6=glGenTextures(1)
glBindTexture(GL_TEXTURE_2D,mytexture6)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
img=Image.open("Saturn.jpg",'r')#Read from folder
img=img.transpose(Image.FLIP_TOP_BOTTOM)#Flip image
img_data=img.convert("RGBA").tobytes()
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,img.width,img.height,0,GL_RGBA,
             GL_UNSIGNED_BYTE,img_data)
glBindTexture(GL_TEXTURE_2D,0)

# --------------  Texture 7 -------------------
mytexture7=glGenTextures(1)
glBindTexture(GL_TEXTURE_2D,mytexture7)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
img=Image.open("Uranus.jpg",'r')#Read from folder
img=img.transpose(Image.FLIP_TOP_BOTTOM)#Flip image
img_data=img.convert("RGBA").tobytes()
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,img.width,img.height,0,GL_RGBA,
             GL_UNSIGNED_BYTE,img_data)
glBindTexture(GL_TEXTURE_2D,0)

# --------------  Texture 8 -------------------
mytexture8=glGenTextures(1)
glBindTexture(GL_TEXTURE_2D,mytexture8)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
img=Image.open("Neptune.jpg",'r')#Read from folder
img=img.transpose(Image.FLIP_TOP_BOTTOM)#Flip image
img_data=img.convert("RGBA").tobytes()
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,img.width,img.height,0,GL_RGBA,
             GL_UNSIGNED_BYTE,img_data)
glBindTexture(GL_TEXTURE_2D,0)

# --------------  Texture 9 -------------------
mytexture9=glGenTextures(1)
glBindTexture(GL_TEXTURE_2D,mytexture9)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
img=Image.open("Pluto.jpg",'r')#Read from folder
img=img.transpose(Image.FLIP_TOP_BOTTOM)#Flip image
img_data=img.convert("RGBA").tobytes()
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,img.width,img.height,0,GL_RGBA,
             GL_UNSIGNED_BYTE,img_data)
glBindTexture(GL_TEXTURE_2D,0)

transform = glGetUniformLocation(shaderprograms,"transform")
modelLoc = glGetUniformLocation(shaderprograms, "model")
viewLoc = glGetUniformLocation(shaderprograms, "view")
projectionLoc = glGetUniformLocation(shaderprograms, "projection")

while not glfw.window_should_close(window):
    glEnable(GL_DEPTH_TEST) 
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glfw.poll_events()
    t = glfw.get_time()
    #------------------------Camera View------------------------
    model = glm.mat4()
    model = glm.rotate(model, 30.0, glm.vec3(1.0, 0.0, 0.0)) 
    view = glm.mat4()
    projection = glm.mat4()
    Projection = glm.ortho(-4.0/3.0, 4.0/3.0, -1.0, 1.0, -1.0, 1.0)
    view = glm.lookAt(glm.vec3(0.5, 0.0, 0.0),
                       glm.vec3(0.0, 0.0, 0.0),
                       glm.vec3(0.0, -1.0, 0.0))
    
    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm.value_ptr(model))
    glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm.value_ptr(view))
    glUniformMatrix4fv(projectionLoc, 1, GL_FALSE, glm.value_ptr(projection))
    #without camera view Sun will only rotate on the orgin.
    #-----------------------------------------------------------
    glBindVertexArray(vao)           #Sun
    trans = glm.mat4()
    trans = glm.rotate(trans, t*0.5, glm.vec3(1.0, 0.0, 1.0))
    trans = glm.scale(trans, glm.vec3(0.5, 0.5, 0.5));
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D,mytexture0)
    glUniformMatrix4fv(transform, 1, GL_FALSE, glm.value_ptr(trans))
    glDrawElements(GL_TRIANGLES,len(faces),GL_UNSIGNED_INT,None)
    
    glBindVertexArray(vao)       #Merkury
    trans = glm.mat4()
    trans = glm.translate(trans, glm.vec3(0.4*m.sin(t), -0.4*m.cos(t), 0.0))
    trans = glm.rotate(trans, t*0.5, glm.vec3(1.0, 0.0, 1.0))
    trans = glm.scale(trans, glm.vec3(0.1, 0.1, 0.1))
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D,mytexture1)
    glUniformMatrix4fv(transform, 1, GL_FALSE, glm.value_ptr(trans))
    glDrawElements(GL_TRIANGLES,len(faces),GL_UNSIGNED_INT,None)
    
    glBindVertexArray(vao)      #Venus
    trans = glm.mat4()
    trans = glm.translate(trans, glm.vec3(0.6*m.sin(-0.5+t), 0.6*m.cos(-0.5+t), 0.0))
    trans = glm.rotate(trans, t*0.5, glm.vec3(1.0, 0.0, 1.0))
    trans = glm.scale(trans, glm.vec3(0.2, 0.2, 0.2))
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D,mytexture2)
    glUniformMatrix4fv(transform, 1, GL_FALSE, glm.value_ptr(trans))
    glDrawElements(GL_TRIANGLES,len(faces),GL_UNSIGNED_INT,None)

    glBindVertexArray(vao)      #Earth
    
    trans = glm.mat4()
    trans = glm.translate(trans, glm.vec3(0.7*m.sin(0.5+t), -0.7*m.cos(0.5+t), 0.0))
    trans = glm.rotate(trans, t*0.5, glm.vec3(1.0, 0.0, 1.0))
    trans = glm.scale(trans, glm.vec3(0.2, 0.2, 0.2))
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D,mytexture3)
    glUniformMatrix4fv(transform, 1, GL_FALSE, glm.value_ptr(trans))
    glDrawElements(GL_TRIANGLES,len(faces),GL_UNSIGNED_INT,None)

    glBindVertexArray(vao)      #Mars
    
    trans = glm.mat4()
    trans = glm.translate(trans, glm.vec3(0.8*m.sin(0.3+t), 0.0, -0.8*m.cos(0.3+t)))
    trans = glm.rotate(trans, t*0.5, glm.vec3(1.0, 0.0, 1.0))
    trans = glm.scale(trans, glm.vec3(0.15, 0.15, 0.15))
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D,mytexture4)
    glUniformMatrix4fv(transform, 1, GL_FALSE, glm.value_ptr(trans))
    glDrawElements(GL_TRIANGLES,len(faces),GL_UNSIGNED_INT,None)

    glBindVertexArray(vao)      #Jupiter
    
    trans = glm.mat4()
    trans = glm.translate(trans, glm.vec3(0.0, 0.8*m.sin(0.3+t), -0.8*m.cos(0.3+t)))
    trans = glm.rotate(trans, t*0.5, glm.vec3(1.0, 0.0, 1.0))
    trans = glm.scale(trans, glm.vec3(0.3, 0.3, 0.3))
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D,mytexture5)
    glUniformMatrix4fv(transform, 1, GL_FALSE, glm.value_ptr(trans))
    glDrawElements(GL_TRIANGLES,len(faces),GL_UNSIGNED_INT,None)
    
    glBindVertexArray(vao)      #Saturn

    trans = glm.mat4()
    trans = glm.translate(trans, glm.vec3(0.8*m.sin(-0.3+t), 0.0, -0.8*m.cos(-0.3+t)))
    trans = glm.rotate(trans, t*0.5, glm.vec3(1.0, 0.0, 1.0))
    trans = glm.scale(trans, glm.vec3(0.35, 0.35, 0.35))
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D,mytexture6)
    glUniformMatrix4fv(transform, 1, GL_FALSE, glm.value_ptr(trans))
    glDrawElements(GL_TRIANGLES,len(faces),GL_UNSIGNED_INT,None)

    glBindVertexArray(vao)      #Uranus

    trans = glm.mat4()
    trans = glm.translate(trans, glm.vec3(0.0, 0.85*m.sin(-0.5+t), -0.85*m.cos(-0.5+t)))
    trans = glm.rotate(trans, t*0.5, glm.vec3(1.0, 0.0, 1.0))
    trans = glm.scale(trans, glm.vec3(0.2, 0.2, 0.2))
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D,mytexture7)
    glUniformMatrix4fv(transform, 1, GL_FALSE, glm.value_ptr(trans))
    glDrawElements(GL_TRIANGLES,len(faces),GL_UNSIGNED_INT,None)
    
    glBindVertexArray(vao)      #Neptune

    trans = glm.mat4()
    trans = glm.translate(trans, glm.vec3(0.95*m.sin(0.7+t), 0.0, -0.95*m.cos(0.7+t)))
    trans = glm.rotate(trans, t*0.5, glm.vec3(1.0, 0.0, 1.0))
    trans = glm.scale(trans, glm.vec3(0.17, 0.17, 0.17))
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D,mytexture8)
    glUniformMatrix4fv(transform, 1, GL_FALSE, glm.value_ptr(trans))
    glDrawElements(GL_TRIANGLES,len(faces),GL_UNSIGNED_INT,None)
    
    glBindVertexArray(vao)      #Pluto

    trans = glm.mat4()
    trans = glm.translate(trans, glm.vec3(0.9*m.sin(0.7+t), -0.9*m.cos(0.7+t), 0.0))
    trans = glm.rotate(trans, t*0.5, glm.vec3(1.0, 0.0, 1.0))
    trans = glm.scale(trans, glm.vec3(0.1, 0.1, 0.1))
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D,mytexture9)
    glUniformMatrix4fv(transform, 1, GL_FALSE, glm.value_ptr(trans))
    glDrawElements(GL_TRIANGLES,len(faces),GL_UNSIGNED_INT,None)
    
    size = np.array(glfw.get_framebuffer_size(window),dtype = np.uint32)
    glViewport(0,0,size[0],size[1])
    
    #-----------Include Escape press input for closing window
    if glfw.get_key(window,GLFW_KEY_X)==GLFW_PRESS:
        glfw.set_window_should_close(window,1)
  
    glfw.poll_events()
    glfw.swap_buffers(window)
    glfw.swap_interval(1)
    
glBindTexture(GL_TEXTURE_2D,0)           
glDeleteProgram(shaderprograms)
glfw.terminate()









    