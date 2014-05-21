#!/usr/bin/env python
import sys, os, glob, shutil, numpy

## Need to edit this to include the path to the netcdf4 site packages for
## your python version
sys.path.append('PATH_TO_NETCDF4')

from netCDF4 import *
from netCDF4 import Dataset as NetCDFFile
from pylab import *

from optparse import OptionParser

import time
import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

## Get command line parameters
parser = OptionParser()
parser.add_option("-f", "--file", dest="filename", help="file to visualize", metavar="FILE")
parser.add_option("-v", "--var", dest="variable", help="variable to visualize", metavar="VAR")
parser.add_option("--max", dest="maximum", help="maximum for color bar", metavar="MAX")
parser.add_option("--min", dest="minimum", help="minimum for color bar", metavar="MIN")

options, args = parser.parse_args()

if not options.filename:
	parser.error("Filename is a required input.")

if not options.variable:
	parser.error("Variable is a required input.")

if not options.maximum:
	color_max = 0.0
else:
	color_max = float(options.maximum)

if not options.minimum:
	color_min = 0.0
else:
	color_min = float(options.minimum)

## Read fields from netcdf file
f = NetCDFFile(options.filename,'r')

times = f.variables['xtime']
field = f.variables[options.variable]

dim = field.dimensions[1]
if dim == "nCells":
	x = f.variables['xCell'][:]
	y = f.variables['yCell'][:]
elif dim == "nEdges":
	x = f.variables['xEdge'][:]
	y = f.variables['yEdge'][:]
elif dim == "nVertices":
	x = f.variables['xVertex'][:]
	y = f.variables['yVertex'][:]

dcedge = f.variables['dcEdge']
vert_levs = len(f.dimensions['nVertLevels'])

junk = dcedge[:]
resolution = junk.max()

del dcedge
del junk

## Compute nx and ny from netcdf file
nx = int((x.max() - x.min())/resolution - 1)
ny = int((y.max() - y.min())/resolution)

time_length = times.shape[0]

del times

print "nx = ", nx, " ny = ", ny
print "vert_levs = ", vert_levs, " time_length = ", time_length

print "Computing global max and min"
junk = field[:,:,0]
maxval = junk.max()
minval = junk.min()

del junk

junk = field[:,:,:]
global_max = junk.max()
global_min = junk.min()

del junk

print "Global max = ", global_max, " Global min = ", global_min
print "Surface max = ", maxval, " Surface min = ", minval

if color_max == color_min:
	color_max = global_max
	color_min = global_min

## Build color bar
steps = 30
step = (color_max - color_min) / steps
color_bar_levels = arange(color_min-step, color_max+step, step)

## Create regular grid
xi = linspace(x.min(), x.max(), nx*2)
yi = linspace(y.min(), y.max(), ny*2)

## Interpolate field onto regular grid
zi = griddata((x, y), field[0,:,0], (xi[None,:], yi[:,None]), method='linear')

## Plot interpolated data
plt.ion()
fig = plt.figure(1)
ax = fig.add_subplot(111)

plt.contourf(xi, yi, zi, levels=color_bar_levels)
plt.colorbar()
plt.draw()

for t in range(1, time_length):
 	ax.cla()
	zi = griddata((x, y), field[t,:,0], (xi[None,:], yi[:,None]), method='linear')
 
	plt.contourf(xi, yi, zi, levels=color_bar_levels)
	plt.draw()
 	time.sleep(0.05)

plt.ioff()

plt.show()
f.close()
