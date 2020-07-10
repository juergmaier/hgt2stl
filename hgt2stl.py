

"""
juerg maier 10.7.2020

convert a hgt-file to stl
a hgt file is a sequence of height values
it is a square section with a lon/lat start position given in the file name

For this conversion it is assumed that we have equidistances between points

with 1" resolution the resulting file will be 1.2 GB and I was not able
to find a program that can reasonably handle it.
this is why I chose to split it into 9 subsections
"""
import os
import math
from array import array
import numpy as np

hgtlat=47
hgtlon=9

filePath = 'd:/projekte/3ddruck/HGT-Dateien_Schweiz/'
fileName = 'N47E009'
inFile = filePath + fileName + '.hgt'

hgt = None
triangles = []
dimension = None
baseHeight = None
counter = 0

def locationToIndex(lat, lon, dimension):
    row = dimension - int((lat-hgtlat)*dimension)
    col = int((lon-hgtlon)*dimension)
    return row, col

    print('Generating surface...')



def createSurface(fp):
    # Surface
    for row in range(dimension - 1):
        for col in range(dimension - 1):
            triangle = [
                [col, row, hgt[col,row]],
                [col+1,row+1,hgt[col+1,row+1]],
                [col,row+1,hgt[col,row+1]]]
            addTriangle(fp,triangle)
            triangle = [
                [col, row, hgt[col,row]],
                [col+1,row,hgt[col+1, row]],
                [col+1,row+1,hgt[col+1, row+1]]]
            addTriangle(fp,triangle)


def createBase(fp):
    #Base
    for row in range(dimension - 1):
        for col in range(dimension - 1):
            triangle = [
                [col,row,baseHeight],
                [col,row+1,baseHeight],
                [col+1,row+1,baseHeight]]
            addTriangle(fp,triangle)
            triangle = [
                [col,row,baseHeight],
                [col+1,row+1,baseHeight],
                [col+1,row,baseHeight]]
            addTriangle(fp,triangle)


def createWalls(fp):
    #Walls, front
    row=0
    for col in range(dimension - 1):
        triangle = [
            [col,row,baseHeight],
            [col+1,row, hgt[col+1,row]],
            [col,row, hgt[col,row]]]
        addTriangle(fp,triangle)
        triangle = [[col,row,baseHeight],
                    [col+1,row, baseHeight],
                    [col+1,row, hgt[col+1,row]]]
        addTriangle(fp,triangle)

# back
    row = dimension-1
    for col in range(dimension - 1):
        triangle = [
            [col,row,baseHeight],
            [col,row, hgt[col,row]],
            [col+1,row, hgt[col+1,row]]]
        addTriangle(fp,triangle)

        triangle = [[col,row,baseHeight],
                    [col+1,row, hgt[col+1,row]],
                    [col+1,row, baseHeight]]
        addTriangle(fp,triangle)



    #left
    for row in range(dimension - 1):
        col=0
        triangle = [
            [col, row, baseHeight],
            [col, row, hgt[col,row]],
            [col, row+1, hgt[col,row+1]]]
        addTriangle(fp,triangle)

        triangle = [
            [col, row, baseHeight],
            [col, row+1, hgt[col,row+1]],
            [col, row+1, baseHeight]]
        addTriangle(fp,triangle)


    # right
    for row in range(dimension - 1):
        col=dimension-1 #right
        triangle = [
            [col, row, baseHeight],
            [col, row+1, hgt[col,row+1]],
            [col, row, hgt[col,row]]]
        addTriangle(fp,triangle)

        triangle = [
            [col, row, baseHeight],
            [col, row+1, baseHeight],
            [col, row+1, hgt[col,row+1]]]
        addTriangle(fp,triangle)



def createStlFile(outFile):
    print('Create STL file...')


    fp = open(outFile,'wb')
    # Binary STL header must be 80 characters wide
    header = b'Generated with hgt2stl                                                          '
    fp.write(header)
    fp.write(np.uint32(5759996))
    return fp

def addTriangle(fp, triangle):
    global counter
    counter+=1
    if counter % 100000 == 0:
         print(counter)
    fp.write(np.float32(0.0))
    fp.write(np.float32(0.0))
    fp.write(np.float32(0.0))
    fp.write(np.float32(triangle[0][0]))
    fp.write(np.float32(triangle[0][1]))
    fp.write(np.float32(triangle[0][2]))
    fp.write(np.float32(triangle[1][0]))
    fp.write(np.float32(triangle[1][1]))
    fp.write(np.float32(triangle[1][2]))
    fp.write(np.float32(triangle[2][0]))
    fp.write(np.float32(triangle[2][1]))
    fp.write(np.float32(triangle[2][2]))
    fp.write(np.uint16(0)) # <- data from shades[l] would go here


size = os.path.getsize(inFile)
#dimension = int(math.sqrt(size/2))
hgtAll = np.fromfile(inFile, dtype='>i2')
dimension = 1200

# mörikon, 47.484290,9.006909
#row, col = locationToIndex(47.484290,9.006909, dimension)
#height = hgt[row, col]
#print(height)

for i in range(3):
    for j in range(3):
        hgt = hgtAll[(i+j)*dimension*dimension:(i+j+1)*dimension*dimension]

        outFile = f'{filePath}{fileName}_{i}_{j}.stl'
        print(outFile)

        # Find the minimum height, ignoring invalid data points (-32768)
        hgt_min = 32767.
        for l in range(len(hgt)):
            if (hgt[l] < hgt_min) and (hgt[l] > -32768.): hgt_min = hgt[l]

        baseHeight = hgt_min-50
        hgt_max = hgt.max() # Find the maximum height

        hgt = hgt.reshape(dimension,dimension)

        # size reduction for testing only
        #dimension=10
        #hgt = hgt[0:10,0:10]

        print('Points:',len(hgt))
        print('Maximum height:',hgt_max)
        print('Minimum height:',hgt_min)

        fp = createStlFile(outFile)
        createSurface(fp)
        createBase(fp)
        createWalls(fp)
        print(counter)
        fp.close()

print('Complete!')





