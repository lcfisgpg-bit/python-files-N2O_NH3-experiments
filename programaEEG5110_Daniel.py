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
import pandas as pd

rm = visa.ResourceManager()

lockin = rm.open_resource('GPIB0::8::INSTR')
#fonte = rm.open_resource('USB0::0x1313::0x804A::M00977996::INSTR') #N2O
fonte = rm.open_resource('USB0::0x1313::0x804A::M00884527::INSTR') #NH3 




xEGG5110 = [] 
yEGG5110 = []
rEGG5110 = []
pEGG5110 = []

temperatureReal = []
temperatureDesired = []
fEGG5110 = []
Rcalculado = []
power = []



def makefig_calib():
    
    plt.title('Photoacoustic Signal')
    plt.grid(True)
    plt.xlabel('Número de pontos (unidade)')
    plt.ylabel('Amplitude (V)')
    plt.plot(rEGG5110, 'r-', label='Módulo')
    plt.legend(loc='upper right')


def makefig_temp():

    plt.title('Photoacoustic Signal')
    plt.grid(True)
    plt.subplot(3,1,1)
    plt.ylabel('Signal R (V)')
    plt.tick_params(labelbottom=False)
    plt.plot(temperatureDesired, rEGG5110, 'r-', label='Absolute')
    plt.legend(loc='upper right')

    plt.subplot(3,1,2)
    plt.ylabel('Signal X (V)')
    plt.tick_params(labelbottom=False)
    plt.plot(temperatureDesired, np.abs(xEGG5110), 'r-', label='x-axis')
    plt.legend(loc='upper right')

    
    plt.subplot(3,1,3)
    plt.xlabel('Temperature (C)')
    plt.ylabel('Signal Y (V)')
    plt.plot(temperatureDesired, np.abs(yEGG5110), 'r-', label='y-axis')
    plt.legend(loc='upper right')
    

    '''
    plt.title('Sinal Fotoacústico')
    plt.grid(True)
    plt.xlabel('Temperatura (C)')
    plt.ylabel('Amplitude (V)')
    plt.plot(temperatureDesired, rEGG5110, 'r-', label='Módulo')
    plt.legend(loc='upper right')
    '''
def makefig_freq():
    
    plt.title('Photoacoustic Signal')
    plt.grid(True)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude (V)')
    plt.plot(fEGG5110, Rcalculado, 'r-', label='Módulo')
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
        dadost = float(fonte.query('MEAS:TEMP?'))

        xEGG5110.append(float(dadosx))
        yEGG5110.append(float(dadosy))
        rEGG5110.append(float(dadosr))
        fEGG5110.append(float(dadosf))
        temperatureReal.append(dadost)

        drawnow(makefig_calib)
        time.sleep(1)
        f.writelines('%e, %e, %e, %f, %.3f\n' % (dadosx, dadosy, dadosr, dadosf, dadost))
        #df = pd.DataFrame({})
        #df['X'] = xEGG5110
        #df['Y'] = yEGG5110
        #df['R'] = rEGG5110
        #df['Phase'] = fEGG5110
        #df['Temperature'] = temperatureReal

        #df.to_csv(f,index=False)


def RampaTemperatura():
    plt.cla()
    global f

    ti = float(tempin.get())
    tf = float(tempfim.get())
    tdel = float(tdelta.get())

    f = filedialog.asksaveasfile(mode='w', defaultextension=".dat") 

    plt.ion()
    fonte.write('SOUR2:TEMP ' + str(ti))
    
    time.sleep(3)
    print(float(fonte.query('MEAS:TEMP?')))
    
    for i in np.arange(ti,tf+tdel,tdel): 
        fonte.write('SOUR2:TEMP ' + str(i))
        time.sleep(2)
    
        dadosx, dadosy, dadosr, dadosp = map(np.float64, lockin.query('SNAP?1,2,3,4').split(','))
        dadost = float(fonte.query('MEAS:TEMP?'))
        dadostDesired = float(i)

        xEGG5110.append(float(dadosx))
        yEGG5110.append(float(dadosy))
        rEGG5110.append(float(dadosr))
        pEGG5110.append(float(dadosp))
        temperatureReal.append(dadost)
        temperatureDesired.append(dadostDesired)

        drawnow(makefig_temp)
           
        f.writelines('%e, %e, %e, %f, %.3f\n' % (dadosx, dadosy, dadosr, dadosp, dadost))
        #df = pd.DataFrame({})
        #df['X'] = xEGG5110
        #df['Y'] = yEGG5110
        #df['R'] = rEGG5110
        #df['Phase'] = pEGG5110
        #df['Temperature'] = temperatureReal

        #df.to_csv(f,index=False)
        
            
    f.close() #depois que terminar de escrever, o arquivo é fechado
    os.system('say "medida conclúida"')        

def RampaFrequencia():

    plt.cla()

    global f
    t = float(temp.get())
    fi = float(freqin.get()) #frequência inicial
    ff = float(freqfim.get()) #frquência final
    pc = float(freqprec.get()) #passo de variação da frequência

    f = filedialog.asksaveasfile(mode='w', defaultextension=".dat") 

    #print(round(float(lockin.query('FRQ')),3)*1e-3) #pega o valor atual frequência
    
    
    plt.ion()
    print("ok")
    
    fonte.write('SOUR2:TEMP ' + str(t))
    treal = float(fonte.query('MEAS:TEMP?'))
    time.sleep(9)
    lockin.write("FMOD1")
    for i in np.arange(fi, ff + pc, pc):
        np.float64(lockin.write("FREQ%d" % i))
        time.sleep(1)
            
        dadosx, dadosy, dadosr, dadosp = map(np.float64, lockin.query('SNAP?1,2,3,4').split(','))
        
        dadost = float(fonte.query('MEAS:TEMP?'))
        dadosf = float(lockin.query('SNAP?9'))
        dadosR = np.sqrt(dadosx**2+dadosy**2)
        
        xEGG5110.append(float(dadosx))
        yEGG5110.append(float(dadosy))
        rEGG5110.append(float(dadosr))
        pEGG5110.append(float(dadosp))
        temperatureReal.append(dadost)
        fEGG5110.append(dadosf)
        Rcalculado.append(dadosR)
        
        drawnow(makefig_freq)
            
        f.writelines('%e, %e, %e, %f, %.3f, %.3f\n' % (dadosx, dadosy, dadosr, dadosp, dadost, dadosf))
        #df = pd.DataFrame({})
        #df['X'] = xEGG5110
        #df['Y'] = yEGG5110
        #df['R'] = rEGG5110
        #df['Phase'] = fEGG5110
        #df['Temperature'] = temperatureReal

        #df.to_csv(f,index=False)
            
    f.close() #depois que terminar de escrever, o arquivo é fechado
    os.system('say "medida conclúida"')
        



def stop():
    """Stop scanning by setting the running flag to False."""
    global running
    running = False
    f.close()


 
def parametros_entrada(root):


#Calibração
    
    global tempCalib,tempin,tempfim, temp, tdelta, prec, num, frec, freqin, freqfim, freqprec

    Label(root, width = 20, font=("Helvica", 16), text = "Measure").place(x = 100, y = 10)

    freq = Entry(root, width = 5)
    freq.insert(END, '3860')
    freq.place(x = 150, y =50)
    Label(root, width = 10, text = 'freq').place(x = 58, y =50)


    tempCalib = Entry(root, width = 5)
    tempCalib.place(x = 150, y = 80)
    Label(root, width = 10, text = "Temp").place(x = 58, y = 80)


    Button(root, width = 12, text = "Start", command = Calibracao).place(x = 230, y = 65)


    Label(root, width = 20, font=("Helvica", 16), text = "Scan of temperature").place(x = 100, y = 120)


#Rampa de temperatura


    freq = Entry(root, width = 5)
    freq.insert(END, '3860')
    freq.place(x = 150, y = 170)
    Label(root, width = 10, text = 'freq').place(x = 58, y = 170)


    tempin = Entry(root, width = 5)
    tempin.place(x = 150, y = 200)
    Label(root, width = 10, text = "T Start").place(x = 58, y = 200)

    tempfim = Entry(root, width = 5)
    tempfim.place(x = 150, y = 230)
    Label(root, width = 10, text = "T final").place(x = 58, y = 230)

    tdelta = Entry(root, width = 5)
    tdelta.place(x = 150, y = 260)
    Label(root, width = 10, text = "Step").place(x = 58, y = 260)
    

    Button(root, width = 12, text = "Start Scan", command = RampaTemperatura).place(x = 230, y = 210)



    Label(root, width = 20, font=("Helvica", 16), text = "Scan of frequency").place(x = 100, y = 300)


#Rampa de frequência


    temp = Entry(root, width = 5)
    temp.place(x = 150, y = 340)
    Label(root, width = 10, text = 'Temp').place(x = 58, y = 340)


    freqin = Entry(root, width = 5)
    freqin.place(x = 150, y = 370)
    Label(root, width = 10, text = "freq Start").place(x = 58, y = 370)

    freqfim = Entry(root, width = 5)
    freqfim.place(x = 150, y = 400)
    Label(root, width = 10, text = "freq final").place(x = 58, y = 400)

    freqprec = Entry(root, width = 5)
    freqprec.place(x = 150, y = 430)
    Label(root, width = 10, text = "Step").place(x = 58, y = 430)
    

    Button(root, width = 12, text = "Start Scan", command = RampaFrequencia).place(x = 230, y = 380)



    
    Button(root, width = 20, text = "Stop any function", command = stop ).place(x = 130 , y = 470)
    

root = Tk()
root.geometry("500x550")
root.title("Photoacoustic Spectroscopy for one Controller")

parametros_entrada(root)
root.mainloop()




        

