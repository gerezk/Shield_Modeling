import sys
import os
import numpy as np
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt

#Function that goes through MCNP output file and determines lines where all detectors relating
#to dose are located
def findDetectors(filename):
    with open(filename, 'r') as mcnp_file:
        #print filename
        line_index = 1
        Index = []
        for lines in mcnp_file.readlines():
            if lines.startswith(" detector located at"):
                Index.append(line_index)
            # KG [
            #search for positive x value of the RPP for borated poly
            line = lines.strip()
            line = line.split() #split line into list of strings
            if "$borated" in line and "RPP" in line:
                point_of_interest = float(line[4])+30 #30 cm from shielding
            line_index += 1
            # ]
    mcnp_file.close()
    return Index, point_of_interest
    print Index

#Function that takes in neutron parameters for dose exposure
#   filename: Name of MCNP output file
#   dose_index: Line number provided by findDetectors() function
#   hours: Length of time of exposure (usually 1 hour)
#   neutron_rate: Rate of neutron emission from source  
def getDose(filename, dose_index, hours, neutron_rate):
    #print filename
    f = open(filename, 'r')
    lines = f.readlines()
    dose_list = []
    error_list = []
    x_location = []
    y_location = []
    z_location = []
    for i in dose_index:
        try:
            dose_list.append(float(lines[i].strip(" ").split()[0])*hours*neutron_rate*1000)#1000 is used to convert rem to mrem
            error_list.append(float(lines[i].strip(" ").split()[1]))            
            x_location.append(float(lines[i-1].strip(" ").split()[-3]))
            y_location.append(float(lines[i-1].strip(" ").split()[-2]))
            z_location.append(float(lines[i-1].strip(" ").split()[-1]))
            

        except:
            pass
    f.close()
    return dose_list, error_list, x_location, y_location, z_location
# input value then find element in an array closest to that inputted value
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx

file_name = sys.argv[1] # variable never invoked

hours = 1
n_rate = 1e8
dose_plot = []
error_plot = []
x_loc_plot = []
y_loc_plot = []
z_loc_plot = []
figure = plt.figure()
ax = figure.add_subplot(111)
line, = ax.plot([], [], '*')
ax.set_title('Poly Outside')
ax.set_ylabel('Dose Rate(mrem/hr)')
ax.set_xlabel('Distance(cm)')

#Looping through all MCNP output files listed in the command line
doses_of_interest = []
points_of_interest = []
for i in range(1,len(sys.argv)):
    #print sys.argv[i]
    dose_index, point_of_interest = findDetectors(sys.argv[i])
    #print dose_index
    dose,error, x_location, y_location, z_location = getDose(sys.argv[i], dose_index,hours, n_rate)
    #print dose
    dose_plot.append(dose)
    error_plot.append(error)
    x_loc_plot.append(x_location)
    y_loc_plot.append(y_location)
    z_loc_plot.append(z_location)
    name = sys.argv[i][:-4]  # file name without .txt
    ax.plot(x_location,dose , '-', label = name)

    # KG [
    #find x-value 30 cm from shielding and interpolate dose at that point
    #check if x value 30 cm from shielding already matches a detector location
    points_of_interest.append(point_of_interest)
    if point_of_interest in x_location:
        for i in range(len(x_location)):
            if point_of_interest == x_location[i]:
                index = i
            else:
                pass
        doses_of_interest.append(dose[index])
    else:
        #search for other bordering x value and associated dose
        x_loc_bordering_dets = []
        dose_at_dets = []
        nearest_x,idx = find_nearest(x_location,point_of_interest)
        x_loc_bordering_dets.append(nearest_x)
        dose_at_dets.append(dose[idx])
        if point_of_interest > nearest_x:
            x_loc_bordering_dets.append(x_location[idx+1])
            dose_at_dets.append(dose[idx+1])
        else:
            x_loc_bordering_dets.insert(0, x_location[idx-1])
            dose_at_dets.insert(0, dose[idx-1])
        print x_loc_bordering_dets, dose_at_dets
        #interpolate dose 30cm from shielding
        f = interpolate.interp1d(x_loc_bordering_dets, dose_at_dets)
        doses_of_interest.append(f(point_of_interest))
ax.plot(points_of_interest,doses_of_interest, 'ro')
    # ]

#print dose
ax.legend()
ax.set_ylim(min(dose_plot[-1]), max(dose_plot[0]))
print x_loc_plot[0]
ax.set_xlim(min(x_loc_plot[0]), max(x_loc_plot[0]))
ax.semilogy()
#line.set_xdata(x_loc_plot)
#line.set_ydata(dose_plot)
figure.canvas.draw()
plt.show()


if __name__ == "__main__":
    pass