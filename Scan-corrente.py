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
fonte = rm.open_resource('USB0::0x1313::0x804A::M00977996::INSTR') # N2O
potencia = rm.open_resource('USB0::0x1313::0x8072::P2007842::INSTR')

# Variáveis globais
xEGG5110 = []
yEGG5110 = []
rEGG5110 = []
pEGG5110 = []
currentReal = []
currentDesired = []
tempReal = []
tempDesired = []
power = []

# Funções para gráficos
def makefig_corr():
    plt.title('Photoacoustic Signal - Current Scan')
    plt.grid(True)
    plt.subplot(3, 1, 1)
    plt.ylabel('Signal R (V)')
    plt.tick_params(labelbottom=False)
    plt.plot(currentDesired, rEGG5110, 'r-', label='Absolute')
    plt.legend(loc='upper right')

    plt.subplot(3, 1, 2)
    plt.ylabel('Signal X (V)')
    plt.tick_params(labelbottom=False)
    plt.plot(currentDesired, np.abs(xEGG5110), 'b-', label='x-axis')
    plt.legend(loc='upper right')

    plt.subplot(3, 1, 3)
    plt.xlabel('Current (mA)')
    plt.ylabel('Signal Y (V)')
    plt.plot(currentDesired, np.abs(yEGG5110), 'g-', label='y-axis')
    plt.legend(loc='upper right')

# Função de varredura de corrente com limite de 300 mA
def RampaCorrente():
    plt.cla()
    global f
    ci = float(currentin.get())  # Corrente inicial
    cf = float(currentfim.get())  # Corrente final
    cstep = float(currentstep.get())  # Passo da variação de corrente

    # Limite de corrente máxima
    #if currentReal > 300:
       # cf = 300
      #  currentfim.delete(0, END)
       # currentfim.insert(0, str(cf))
       # print("A corrente final foi limitada a 300 mA.")

    f = filedialog.asksaveasfile(mode='w', defaultextension=".dat")

    plt.ion()
    tini = time.time()
    print("Iniciando varredura de corrente")

    for i in np.arange(ci, cf + cstep, cstep):
        fonte.write(f'SOUR:CURR {i / 1000}')  # Ajuste para A
        time.sleep(1.1)
        t = time.time()- tini

        dadosx, dadosy, dadosr, dadosp = map(np.float64, lockin.query('SNAP?1,2,3,4').split(','))
        dadost = float(fonte.query('MEAS:CURR?')) * 1000  # Corrente medida (mA)
        pot = float(potencia.query('MEAS:POW?'))


        xEGG5110.append(dadosx)
        yEGG5110.append(dadosy)
        rEGG5110.append(dadosr)
        pEGG5110.append(dadosp)
        power.append(pot)
        currentReal.append(dadost)
        currentDesired.append(i)

        drawnow(makefig_corr)

        f.writelines('%e, %e, %e, %f, %.3f,%.3f,%.2f\n' % (dadosx, dadosy, dadosr, dadosp, i,t,pot))

    f.close()
    os.system('say "medida concluída"')

# Função para iniciar a varredura de temperatura
def RampaTemperatura():
    plt.cla()
    global f
    ti = float(tempin.get())  # Temperatura inicial
    tf = float(tempfim.get())  # Temperatura final
    tstep = float(tdelta.get())  # Passo da variação de temperatura

    f = filedialog.asksaveasfile(mode='w', defaultextension=".dat")

    plt.ion()
    print("Iniciando varredura de temperatura")

    for i in np.arange(ti, tf + tstep, tstep):
        fonte.write(f'TEMP {i}')  # Ajuste de temperatura
        time.sleep(2)

        dadosx, dadosy, dadosr, dadosp = map(np.float64, lockin.query('SNAP?1,2,3,4').split(','))
        dadost = float(fonte.query('MEAS:TEMP?'))  # Temperatura medida (°C)
        pot = float(potencia.query('MEAS:POW?'))

        
        xEGG5110.append(dadosx)
        yEGG5110.append(dadosy)
        rEGG5110.append(dadosr)
        pEGG5110.append(dadosp)
        power.append(pot)
        tempReal.append(dadost)
        tempDesired.append(i)

        drawnow(makefig_temp)

        f.writelines('%e, %e, %e, %f, %.3f %f\n' % (dadosx, dadosy, dadosr, dadosp, dadost,pot))

    f.close()
    os.system('say "medida concluída"')

# Função para gráfico de temperatura
def makefig_temp():
    plt.title('Photoacoustic Signal - Temperature Scan')
    plt.grid(True)
    plt.subplot(3, 1, 1)
    plt.ylabel('Signal R (V)')
    plt.tick_params(labelbottom=False)
    plt.plot(tempDesired, rEGG5110, 'r-', label='Absolute')
    plt.legend(loc='upper right')

    plt.subplot(3, 1, 2)
    plt.ylabel('Signal X (V)')
    plt.tick_params(labelbottom=False)
    plt.plot(tempDesired, np.abs(xEGG5110), 'b-', label='x-axis')
    plt.legend(loc='upper right')

    plt.subplot(3, 1, 3)
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Signal Y (V)')
    plt.plot(tempDesired, np.abs(yEGG5110), 'g-', label='y-axis')
    plt.legend(loc='upper right')

# Interface de parâmetros
def parametros_entrada(root):
    global tempin, tempfim, tdelta, freqin, freqfim, freqprec
    global currentin, currentfim, currentstep

    # Seção para varredura de corrente
    Label(root, width=20, font=("Helvica", 16), text="Scan of Current").place(x=100, y=10)

    currentin = Entry(root, width=5)
    currentin.place(x=150, y=40)
    Label(root, width=10, text="I Start (mA)").place(x=58, y=40)

    currentfim = Entry(root, width=5)
    currentfim.place(x=150, y=70)
    Label(root, width=10, text="I Final (mA)").place(x=58, y=70)

    currentstep = Entry(root, width=5)
    currentstep.place(x=150, y=100)
    Label(root, width=10, text="Step (mA)").place(x=58, y=100)

    Button(root, width=20, text="Start Current Scan", command=RampaCorrente).place(x=100, y=130)

    # Seção para varredura de temperatura
    Label(root, width=20, font=("Helvica", 16), text="Scan of Temperature").place(x=100, y=170)

    tempin = Entry(root, width=5)
    tempin.place(x=150, y=200)
    Label(root, width=10, text="T Start (°C)").place(x=58, y=200)

    tempfim = Entry(root, width=5)
    tempfim.place(x=150, y=230)
    Label(root, width=10, text="T Final (°C)").place(x=58, y=230)

    tdelta = Entry(root, width=5)
    tdelta.place(x=150, y=260)
    Label(root, width=10, text="Step (°C)").place(x=58, y=260)

    Button(root, width=20, text="Start Temperature Scan", command=RampaTemperatura).place(x=100, y=290)

    # Botão para parar qualquer operação
    Button(root, width=20, text="Stop any function", command=stop).place(x=130, y=330)

# Função para interromper qualquer operação
def stop():
    print("Operação interrompida.")

# Configuração principal da janela
root = Tk()
root.geometry("500x400")
root.title("Photoacoustic Spectroscopy with Current and Temperature Control")

parametros_entrada(root)
root.mainloop()
