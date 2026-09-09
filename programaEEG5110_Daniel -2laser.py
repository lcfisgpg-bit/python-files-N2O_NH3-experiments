from tkinter import *
from tkinter import filedialog
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt 
import pyvisa as visa
import numpy as np
import time
from drawnow import drawnow 
import os

rm = visa.ResourceManager()

lockin = rm.open_resource('GPIB0::8::INSTR')
fonteNH3 = rm.open_resource('USB0::0x1313::0x804A::M00884527::INSTR') #Usando a fonte da Thorlabs
fonteN2O = rm.open_resource('USB0::0x1313::0x804A::M00977996::INSTR')


xEGG5110 = [] 
yEGG5110 = []
rEGG5110 = []
pEGG5110 = []
temperatureReal1 = []
temperatureDesired1 = []
temperatureReal2 = []
temperatureDesired2 = []

fEGG5110 = []
Rcalculado = []



def makefig_calib():
    
    plt.title('Photoacoustic Signal')
    plt.grid(True)
    plt.xlabel('Point of numbers')
    plt.ylabel('Amplitude (V)')
    plt.plot(rEGG5110, 'r-', label='Absolute')
    plt.legend(loc='upper right')


def makefig_temp():

    plt.title('Photoacoustic Signal')
    plt.grid(True)
    plt.subplot(3,1,1)
    plt.ylabel('Signal R (V)')
    plt.tick_params(labelbottom=False)
    plt.plot(temperatureReal1, rEGG5110, 'r-', label='Absolute')
    plt.legend(loc='upper right')

    plt.subplot(3,1,2)
    plt.ylabel('Signal X (V)')
    plt.tick_params(labelbottom=False)
    plt.plot(temperatureReal1, np.abs(xEGG5110), 'r-', label='Phase')
    #plt.plot(temperatureDesired2, np.abs(xEGG5110), 'r-', label='Fase2')
    plt.legend(loc='upper right')

    
    plt.subplot(3,1,3)
    plt.xlabel('Temperature (C)')
    plt.ylabel('Signal Y (V)')
    plt.plot(temperatureReal1, np.abs(yEGG5110), 'r-', label='Quadrature')
    #plt.plot(temperatureDesired2, np.abs(yEGG5110), 'r-', label='Quadratura2')
    plt.legend(loc='upper right')
    
def makefig_freq():
    
    plt.title('Photoacoustic Signal')
    plt.grid(True)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (V)')
    plt.plot(fEGG5110, Rcalculado, 'r-', label='Absolute')
    plt.legend(loc='upper right')
        
def Calibracao():
    plt.cla()
    global running
    running = True
    global f 
    f = filedialog.asksaveasfile(mode='w', defaultextension=".dat")
    print (running)
    while running:
        
        dadosx, dadosy, dadosr, dadosf = map(np.float64, lockin.query('SNAP?1,2,3,4').split(','))
        dadost1 = float(fonteNH3.query('MEAS:TEMP?'))
        dadost2 = float(fonteN2O.query('MEAS:TEMP?'))

        xEGG5110.append(float(dadosx))
        yEGG5110.append(float(dadosy))
        rEGG5110.append(float(dadosr))
        fEGG5110.append(float(dadosf))
        temperatureReal1.append(dadost1)
        temperatureReal2.append(dadost2)


        drawnow(makefig_calib)
        time.sleep(1)
        f.writelines('%e, %e, %e, %f, %.3f, %.3f\n' % (dadosx, dadosy, dadosr, dadosf, dadost1, dadost2))

    f.close() #depois que terminar de escrever, o arquivo é fechado
    os.system('say "medida conclúida"')  

def RampaTemperatura():
    plt.cla()
    global f
    ti1 = float(tempin1.get())
    tf1 = float(tempfim1.get())
    tdel1 = float(tdelta1.get())

    ti2 = float(tempin2.get())
    tf2 = float(tempfim2.get())
    
    #tdel2 = float(tdelta2.get())

    f = filedialog.asksaveasfile(mode='w', defaultextension=".dat") 

    plt.ion()
    fonteNH3.write('SOUR2:TEMP ' + str(ti1))
    fonteN2O.write('SOUR2:TEMP ' + str(ti2))
    
    b = ti1 - ti2
    

    time.sleep(3)
 
    for i in np.arange(ti1,tf1+tdel1,tdel1): #rampa de temperyEGG5110atura
        fonteNH3.write('SOUR2:TEMP ' + str(i))
        if float(fonteN2O.query('MEAS:TEMP?')) <= tf2:
            fonteN2O.write('SOUR2:TEMP ' + str(i-b)) #setar o valor que a cada 0.1v é equivalente a 1ºC
        else:
            fonteN2O.write('SOUR2:TEMP ' + str(tf2)) 
        time.sleep(2)
            
        dadosx, dadosy, dadosr, dadosp = map(np.float64, lockin.query('SNAP?1,2,3,4').split(','))
        dadost1 = float(fonteNH3.query('MEAS:TEMP?'))
        dadost2 = float(fonteN2O.query('MEAS:TEMP?'))
        dadostDesired1 = float(i)
        dadostDesired2 = float(i)

        xEGG5110.append(float(dadosx))
        yEGG5110.append(float(dadosy))
        rEGG5110.append(float(dadosr))
        pEGG5110.append(float(dadosp))
        temperatureReal1.append(dadost1)
        temperatureDesired1.append(dadostDesired1)
        temperatureReal2.append(dadost2)
        temperatureDesired2.append(dadostDesired2)

        drawnow(makefig_temp)
           
        f.writelines('%e, %e, %e, %f, %.3f, %.3f\n' % (dadosx, dadosy, dadosr, dadosp, dadost1, dadost2))
        #time.sleep(5) #dorme 30s para tentar estabilizar a temperatura
            
    f.close() #depois que terminar de escrever, o arquivo é fechado
    os.system('say "medida conclúida"')        

def RampaFrequencia():

    plt.cla()

    global f
    t1 = float(temp1.get())
    fi1 = float(freqin1.get()) #frequência inicial 1
    ff1 = float(freqfim1.get()) #frquência final 1
    pc1 = float(freqprec1.get()) #passo de variação da frequência
    t2 = float(temp2.get())
    #pc2 = float(freqprec2.get()) #passo de variação da frequência

    f = filedialog.asksaveasfile(mode='w', defaultextension=".dat")     
    
    plt.ion()
    
    
    fonteNH3.write('SOUR2:TEMP ' + str(t1))
    fonteN2O.write('SOUR2:TEMP ' + str(t2))
    #treal1 = float(fonteNH3.query('MEAS:TEMP?'))
    #treal2 = float(fonteN2O.query('MEAS:TEMP?'))
    time.sleep(9)
    
    for i in np.arange(fi1, ff1 + pc1, pc1):
        #lockin.write('OF %f 4' % i) #it's wrong
        time.sleep(1)
      
        dadosx, dadosy, dadosr, dadosp = map(np.float64, lockin.query('SNAP?1,2,3,4').split(','))
        dadost1 = float(fonteNH3.query('MEAS:TEMP?'))
        dadost2 = float(fonteN2O.query('MEAS:TEMP?'))
        dadosf = float(lockin.query('SNAP?9'))
        dadosR = np.sqrt(dadosx**2+dadosy**2)
        
        xEGG5110.append(float(dadosx))
        yEGG5110.append(float(dadosy))
        rEGG5110.append(float(dadosr))
        pEGG5110.append(float(dadosp))
        temperatureReal1.append(dadost1)
        temperatureReal2.append(dadost2)
        fEGG5110.append(dadosf)
        Rcalculado.append(dadosR)
        
        drawnow(makefig_freq)
            
        f.writelines('%e, %e, %e, %f, %.3f, %.3f, %.3f\n' % (dadosx, dadosy, dadosr, dadosp, dadost1, dadost2, dadosf))
        #time.sleep(5) #dorme 30s para tentar estabilizar a temperatura
            
    f.close() #depois que terminar de escrever, o arquivo é fechado
    os.system('say "medida conclúida"')
        



def stop():
    """Stop scanning by setting the running flag to False."""
    global running
    running = False
    f.close()
    plt.ioff()


 
def parametros_entrada(root):


#Calibração
    
    global tempCalib,tempin1,tempfim1,tempin2,tempfim2, temp1,temp2, tdelta1,tdelta2, prec, num, frec, freqin1, freqfim1, freqprec1,freqin2, freqfim2, freqprec2

    Label(root, width = 20, font=("Helvica", 16), text = "Measure").place(x = 100, y = 10)

    freq = Entry(root, width = 5)
    freq.insert(END, '3860')
    freq.place(x = 150, y =50)
    Label(root, width = 10, text = 'freq').place(x = 58, y =50)


    tempCalib = Entry(root, width = 5)
    tempCalib.place(x = 150, y = 80)
    Label(root, width = 10, text = "Temp").place(x = 58, y = 80)


    Button(root, width = 12, text = "Start Measure", command = Calibracao).place(x = 230, y = 65)


    Label(root, width = 20, font=("Helvica", 16), text = "Scan Temperature").place(x = 100, y = 120)


#Rampa de temperatura


    freq = Entry(root, width = 5)
    freq.insert(END, '3860')
    freq.place(x = 150, y = 170)
    Label(root, width = 10, text = 'freq').place(x = 58, y = 170)


    tempin1 = Entry(root, width = 5)
    tempin1.place(x = 150, y = 200)
    Label(root, width = 10, text = "T_NH3 start").place(x = 58, y = 200)

    tempfim1 = Entry(root, width = 5)
    tempfim1.place(x = 150, y = 230)
    Label(root, width = 10, text = "T_NH3 final").place(x = 58, y = 230)



    tempin2 = Entry(root, width = 5)
    tempin2.place(x = 150, y = 260)
    Label(root, width = 10, text = "T_N2O start").place(x = 58, y = 260)

    tempfim2 = Entry(root, width = 5)
    tempfim2.place(x = 150, y = 290)
    Label(root, width = 10, text = "T_N2O final").place(x = 58, y = 290)

    tdelta1 = Entry(root, width = 5)
    tdelta1.place(x = 150, y = 320)
    Label(root, width = 10, text = "Step").place(x = 58, y = 320)
    



    Button(root, width = 12, text = "Start Scan", command = RampaTemperatura).place(x = 230, y = 230)



    Label(root, width = 20, font=("Helvica", 16), text = "Scan frequency").place(x = 100, y = 350)


#Rampa de frequência


    temp = Entry(root, width = 5)
    temp.place(x = 150, y = 400)
    Label(root, width = 10, text = 'Temp_NH3').place(x = 58, y = 400)


    freqin1 = Entry(root, width = 5)
    freqin1.place(x = 150, y = 430)
    Label(root, width = 10, text = "freq_NH3 Start").place(x = 58, y = 430)

    freqfim1 = Entry(root, width = 5)
    freqfim1.place(x = 150, y = 460)
    Label(root, width = 10, text = "freq_NH3 final").place(x = 58, y = 460)

    freqprec1 = Entry(root, width = 5)
    freqprec1.place(x = 150, y = 490)
    Label(root, width = 10, text = "Step").place(x = 58, y = 490)

    temp2 = Entry(root, width = 5)
    temp2.place(x = 150, y = 520)
    Label(root, width = 10, text = 'Temp_N2O').place(x = 58, y = 520)


#    freqin2 = Entry(root, width = 5)
#    freqin2.place(x = 150, y = 390)
#    Label(root, width = 10, text = "freq_N2O Start").place(x = 58, y = 580)

#    freqfim2 = Entry(root, width = 5)
#    freqfim2.place(x = 150, y = 420)
#    Label(root, width = 10, text = "freq_N2O final").place(x = 58, y = 610)


    Button(root, width = 12, text = "Start Scan", command = RampaFrequencia).place(x = 230, y = 480)

    
    Button(root, width = 20, text = "Stop any function", command = stop ).place(x = 130 , y = 640)
    

root = Tk()
root.geometry("500x700")
root.title("Photoacoustic Spectroscopy for two Controller")
parametros_entrada(root)
root.mainloop()




        

