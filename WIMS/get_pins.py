import numpy as np
import scipy

def get_pins_1_8(p0,p2,f,npins):
##Get pins in the same order as Ben 
    pins =[]

    for x in [1,2,4,5]:
        pins.append((x*p0,0,f))


    for y in range(8): 
        pins.append((8*p2,y*p2,f))
        pins.append((9*p2,y*p2,f))

    pins.append((8*p2,8*p2,f))
    pins.append((9*p2,8*p2,f))
    pins.append((9*p2,9*p2,f))

    pins.append((1*p2,1*p2,f))
    pins.append((2*p2,1*p2,f))

    for y in [3,4,5,6,7]:
        pins.append((y*p2,p2,f))
    pins.append((2*p2,2*p2,f))
    for y in [3,4,5,6,7]:
        pins.append((y*p2,2*p2,f))


    pins.append((7.2*p2,4.5*p2,f))
    pins.append((6.05*p2,3.68*p0,f))

    pins.append((7*p2,7*p2,f))
    pins.append((7.2*p2,5.5*p2,f))
    pins.append((6.32*p2,6.32*p2,f))
    pins.append((6.4*p2,5*p2,f))

    for x in [4.5,5.5]:
        pins.append((x*p2,2.8*p2,f))

    pins.append((5*p2,3.6*p2,f))
    pins.append((4.1*p2,4.1*p2,f))
    pins.append((5.2*p2,4.53*p2,f))
    return pins


def get_w(p0):
    #returns positions of control rods in terms of pitch p0
    wx=[0,3*p0,5*p0,3*p0,6*p0,6*p0]
    wy=[0,3*p0,5*p0,   0,   0,3*p0]
    return wx,wy


def get_sc(pins,gt_x,gt_y,f,p2):
    D_coords=[]
    count=0
    for p in pins:
        x=p[0]
        y=p[1]
        D_coords.append((x,y))
        count+=1
    for i in range(len(gt_x)):
        D_coords.append((gt_x[i],gt_y[i]))

    D_coords=np.array(D_coords)
    #print("D_coords ", D_coords)

    triangles=scipy.spatial.Delaunay(D_coords)
    sc=triangles.simplices

    for t in sc:
        for i in range(len(t)):
            if t[i]>count-1 : #the index of the pin is longer than the number of fuel pins, this is a guide tube
                t[i]=-(t[i]-count+1)
    sc=list(sc)
    sc.append(22)
    sc.append([22,21])
    sc.append([21,19])
    sc.append([19,17])
    sc.append([17,15])
    sc.append([13,15])
    sc.append([11,13])
    sc.append([9,11])
    sc.append([7,9])
    sc.append([5,7])
    return sc

