# %%

import time
import yaml

if __name__ == "__main__":
    parameters = {
        "a": 1,
        "b": 2,
    }
    settings = {
        "name": "frequency_sweep_SV_v02",
        "f_start": 1000,
        "f_end": 15000,
        "f_step": 10.0,
        "amplitude": 80e-3,
        "waveform": "SINusoid",
    }

    locals().update(parameters)

    print(f"a = {a}, b = {b}")
    print(f"locals() = {locals()}")

    date_time = time.strftime("%Y-%m-%d_%H-%M")

    with open(
        f"./measurements/{date_time}_{settings['name']}_settings.yml", "w"
    ) as outfile:
        yaml.dump(settings, outfile)


# %%
