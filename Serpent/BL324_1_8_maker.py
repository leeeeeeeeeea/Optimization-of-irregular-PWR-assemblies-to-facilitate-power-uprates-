import numpy as np
import matplotlib.pyplot as plt
import serpentTools 
import csv 


def serp_input(p0,p2,f,npins,pins,x_g,y_g,asm_pitch,P_tot,n_pop,n_cycles) :
    ##x and y positions just like in the output
    x=[]
    y=[]
    for p in pins:
        x.append(p[0])
        y.append(p[1])

    #Now we want to add them to the BL324_1_8 input file

    f = open('BL324_1_8', mode ='w')
    f.writelines(['set title "BL324 asembly" \n','set gcu -1 \n', 'set cmm 0 \n', 'set opti 4 \n','\n','% --- Define materials --- %\n','mat fuel	-10.295 rgb 255 215 0 \n','92235.09c	0.0495 \n','92238.09c 	0.9505 \n','8016.09c 	2 \n'])
    f.writelines(['mat clad 	4.2982E-02 rgb 150 150 150 \n','40000.06c	4.2982E-02 \n'])
    f.writelines(['mat coolant	7.2216E-02 moder lwtr 1001 rgb 173 216 230\n',' 1001.06c  5.061215E-02\n',' 8016.06c  2.530608E-02 \n'])
    f.writelines(['% thermal scattering library for H20 \n','therm lwtr lwj3.11t \n'])
    f.write("%Lattice \n")

    for i in range(len(x)):
        line1="surf Sf_" + str(i)+" cyl "+ str(x[i]) +" " + str(y[i]) + " 0.3696 \n"
        line2="surf Sv_" + str(i)+" cyl "+ str(x[i]) +" " + str(y[i]) + " 0.3773 \n"
        line3="surf Sc_" + str(i)+" cyl "+ str(x[i]) +" " + str(y[i]) + " 0.4287 \n"
        line4="cell Cf_" +str(i)+" U0 fuel -SA -Sf_"+str(i)+" \n"
        line5="cell Cv_" +str(i)+" U0 void -SA Sf_"+str(i)+" -Sv_"+str(i)+" \n"
        line6="cell Cc_" +str(i)+" U0 clad -SA Sv_"+str(i)+" -Sc_"+str(i)+"\n"
        f.writelines([line1, line2,line3,line4,line5,line6])

    for i in range(len(x_g)):
        line1="surf SGi_" + str(i)+" cyl "+ str(x_g[i]) +" " + str(y_g[i]) + " 0.56 \n"
        line2="surf SGc_" + str(i)+" cyl "+ str(x_g[i]) +" " + str(y_g[i]) + " 0.61 \n"
        line3="cell CGi_" +str(i)+" U0 coolant -SA -SGi_"+str(i)+" \n"
        line4="cell CGc_" +str(i)+" U0 clad -SA SGi_"+str(i)+" -SGc_"+str(i)+"\n"
        f.writelines([line1, line2,line3,line4])

    f.writelines(['% Assembly \n',"surf SA sqc 5.375 5.375 5.375 \n"])


    s=""
    for i in range(len(x)):
        s+=" Sc_" + str(i)
    for i in range(len(x_g)):
        s+=" SGc_" + str(i)
    line = 'cell coolA U0 coolant -SA ' + s+ '\n'
    line2="cell insideA 0 fill U0 -SA \n"
    f.writelines([line,line2,"cell outsideA 0 outside SA \n"])
    f.write("set usym U0 3 2 0.0 0.0 0 45 \n")

    f.writelines(['% --- Neutron population and criticality cycles : \n','set pop '+str(n_pop)+' '+str(n_cycles)+' 5  \n'])
    f.writelines(['% --- Boundary conditions: \n','set bc 2 %reflective \n'])  
    f.writelines(['% --- Normalisation: \n','set power '+str(P_tot/8)+ ' \n'])
    f.writelines(['% --- Geometry and mesh plots:  \n','plot 30 100 100  \n']) 
    f.writelines(['% --- Cross section library file path: \n','set acelib "/usr/software/mcnplib/SERPENT/XSdata_endfb7/sss_endfb7u.xsdata" \n']) 

    f.write('% --- Detectors for power of each pin \n') 
    for i in range(len(x)):
        line="det D" +str(i) +" dr -8 void dc Cf_" +str(i) + " \n"
        f.write(line)
    f.close()
    return "Serpent input generated"

