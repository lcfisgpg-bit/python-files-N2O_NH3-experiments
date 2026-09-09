# test_lasers_operation.py

import time
from gpg_devices_v04 import Thorlabs_ITC4002QCL
from gpg_devices_v04 import Rigol_DG832

def ramp_lasers(laserNH3, laserN2O):
    """
    Turn on the lasers gradually:
    1. TEC on manually (temperature control)
    2. Set temperature: temp_i = 25 to tempNH3_f = 46.450 and tempN2O_f = 41.560 in celcius (step 0.1)
    3. LD on
    4. Set current 
    """
    
    temp_NH3_target = 46.450  # °C
    temp_N2O_target = 41.560  # °C
    temp_i = 25.000           # °C
    step_temp = 0.1           # °C
    delay_temp = 1            # time between the temperature step

    current_NH3_target = 520.0e-3 # 520.0 mA
    current_N2O_target = 293.6e-3 # 293.6 mA
    step_current = 5e-3           # 5 mA
    delay_current = 1           # time between the current step

    print("\n Turn on the LD")
    laserNH3.ld_on()
    laserN2O.ld_on()
    print("LD on")

    for i in range(5, 0, -1):
        print(f" \n    Wating {i} seconds setting current", end="\r")
        time.sleep(1)

    print("\n Setting current")

    current_NH3 = 0
    current_N2O = 0
    
    while current_NH3 < current_NH3_target or current_N2O < current_N2O_target:
        if current_NH3 < current_NH3_target:
            current_NH3 += step_current
            if current_NH3 > current_NH3_target:
                current_NH3 = current_NH3_target
        laserNH3.set_laser_current(current_NH3)

        if current_N2O < current_N2O_target:
            current_N2O += step_current
            if current_N2O > current_N2O_target:
                current_N2O = current_N2O_target
        laserN2O.set_laser_current(current_N2O)
        time.sleep(delay_current)

    print("\n Setting temperature")

    time.sleep(1)

    temp_NH3 = temp_i
    temp_N2O = temp_i
    
    while temp_NH3 < temp_NH3_target or temp_N2O < temp_N2O_target:
        if temp_NH3 < temp_NH3_target:
            temp_NH3 += step_temp
            if temp_NH3 > temp_NH3_target:
                temp_NH3 = temp_NH3_target
        laserNH3.set_temp(temp_NH3)


        if temp_N2O < temp_N2O_target:
            temp_N2O += step_temp
            if temp_N2O > temp_N2O_target:
                temp_N2O = temp_N2O_target
        laserN2O.set_temp(temp_N2O)
        time.sleep(delay_temp)

    print("\n Temperature stabilization...")
    for i in range(10, 0, -1):
        print(f"\n    Wating {i} seconds...", end="\r")
        time.sleep(1)
    print("\n Temperatures have stabilized.")

    laserNH3.modulation_on()
    laserN2O.modulation_on()
    print("\n External modulation ON")

def FG832_on(FG832):
    """
    1. FG832 = Function Generator RigolDG 832
    2. ON (output channel 1 and 2)
    3. Sync channels 
    """

    phase_FG = 120      #   degree
    
    FG832.on(channel=1)
    FG832.on(channel=2)

    time.sleep(2)
    FG832.phase_sync()

    print(f"\n The channels are sync")
    time.sleep(2)

    FG832.set_phase(phase_FG, channel=2)
    print(f"\n  Phase shift was defined in Rigol DG 832")

def ramp_lasers_off(laserNH3, laserN2O):
    """
    Turn off the lasers gradually:
    1. Setting current zero
    2. LD off
    3. Setting temperature in both lasers 25 °C
    """

    temp_target = 25.000    #   °C
    temp_NH3_i = 46.450     #   °C
    temp_N2O_i = 41.560     #   °C
    step_temp = 0.1         #   °C
    delay_temp = 1        #   time between temperature sweep

    current_NH3_i = 520.0e-3    #   520.0 mA
    current_N2O_i = 293.6e-3    #   293.6 mA
    current_target = 0          #   0 mA
    step_current = 5e-3         #   5 mA
    delay_current = 1         #   time between current step


    laserNH3.modulation_off()
    laserN2O.modulation_off()
    print("\n External modulation OFF")

    time.sleep(1)

    print("\n Setting temperature")
    

    temp_NH3 = temp_NH3_i
    temp_N2O = temp_N2O_i

    while temp_NH3 > temp_target or temp_N2O > temp_target:
        if temp_NH3 > temp_target:
            temp_NH3 -= step_temp
            if temp_NH3 < temp_target:
                temp_NH3 = temp_target
        laserNH3.set_temp(temp_NH3)
    
        if temp_N2O > temp_target:
            temp_N2O -= step_temp
            if temp_N2O < temp_target:
                temp_N2O = temp_target
        laserN2O.set_temp(temp_N2O)
        time.sleep(delay_temp)

    print("\n Temperature seeting 25.000 °C")

    time.sleep(1)

    print("\n Temperature stabilization...")
    for i in range(10, 0, -1):
        print(f"\n    Wating {i} seconds...", end="\r")
        time.sleep(1)
    print("\n Temperatures have stabilized.")

    time.sleep(1)

    print("\n Setting current off")

    current_NH3 = current_NH3_i
    current_N2O = current_N2O_i
    
    while current_NH3 > current_target or current_N2O > current_target:
        if current_NH3 > current_target:
            current_NH3 -= step_current
        if current_NH3 <= current_target:
            current_NH3 = current_target
        laserNH3.set_laser_current(current_NH3)

    
        if current_N2O > current_target:
            current_N2O -= step_current
            if current_N2O <= current_target:
                current_N2O = current_target
        laserN2O.set_laser_current(current_N2O)
        time.sleep(delay_current)

    print("\n lasers 0 mA") 

    time.sleep(2)

    print("\n Turn off LD")
    time.sleep(1)
    laserNH3.ld_off()
    laserN2O.ld_off()
    print("\n LD off")

if __name__ == "__main__":
    print("Connecting the lasers source...")
    laserNH3 = Thorlabs_ITC4002QCL("USB0::0x1313::0x804A::M00884527::INSTR")
    laserN2O = Thorlabs_ITC4002QCL("USB0::0x1313::0x804A::M00977996::INSTR")
    FG832 = Rigol_DG832("USB0::0x1AB1::0x643::DG8A244803802::INSTR")

    time.sleep(2)

    laserNH3.modulation_off()
    laserN2O.modulation_off()

    print("\n External modulation OFF")

    time.sleep(2)    

    print("Starting RIGOL 832...")
    FG832_on(FG832)
    print(f"\n  RIGOL DG832 ON")

    time.sleep(2)

    ciclo = 1

    while True:
        print(f"CICLO {ciclo} - Lasers ON")
            
        print("Starting ramp_lasers...")
        ramp_lasers(laserNH3, laserN2O)

        time.sleep(1)

        print("Lasers on for h...")
        for i in range(300, 0, -1):
            if i % 60 == 0:
                print(f"   less {i//60} minutes...")
            time.sleep(1)
        print("1h completed")

        time.sleep(1)
        
        print(f"CICLO {ciclo} - Lasers OFF")
        
        print("\n Lasers off for h")
        ramp_lasers_off(laserNH3, laserN2O)

        
        for i in range(300, 0, -1):
            if i % 60 == 0:
                print(f"   less {i//60} minutes...")
            time.sleep(1)
        print("h completed")

        ciclo += 1
