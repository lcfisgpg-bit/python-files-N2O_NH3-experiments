# test_turn_off_lasers.py

import time
from gpg_devices_v04 import Thorlabs_ITC4002QCL

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
    delay_temp = 0.5        #   time between temperature sweep

    current_NH3_i = 520.0e-3    #   520.0 mA
    current_N2O_i = 293.6e-3    #   293.6 mA
    current_target = 0          #   0 mA
    step_current = 5e-3         #   5 mA
    delay_current = 0.5         #   time between current step

    print("\n Setting temperature")
    
    temp_current = temp_NH3_i
    while temp_current > temp_target:
        temp_current -= step_temp
        if temp_current <= temp_target:
            temp_current = temp_target
        laserNH3.set_temp(temp_current)
        time.sleep(delay_temp)
    print("\n NH3: 25.000 °C")  

    temp_current = temp_N2O_i
    while temp_current > temp_target:
        temp_current -= step_temp
        if temp_current <= temp_target:
            temp_current = temp_target
        laserN2O.set_temp(temp_current)
        time.sleep(delay_temp)
    print("\n N2O: 25.000 °C")  

    print("\n Temperature stabilization...")
    for i in range(10, 0, -1):
        print(f"\n    Wating {i} seconds...", end="\r")
        time.sleep(1)
    print("\n Temperatures have stabilized.")

    time.sleep(2)

    print("\n Setting current off")

    current = current_NH3_i         
    while current > current_target:
        current -= step_current
        if current <= current_target:
            current = current_target
        laserNH3.set_laser_current(current)
        time.sleep(delay_current)
    print("\n NH3: 0 mA")  

    current = current_N2O_i
    while current > current_target:
        current -= step_current
        if current <= current_target:
            current = current_target
        laserN2O.set_laser_current(current)
        time.sleep(delay_current)
    print("\n N2O: 0 mA")  

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
    
    print("Starting ramp_lasers...")
    ramp_lasers_off(laserNH3, laserN2O)
    
    
