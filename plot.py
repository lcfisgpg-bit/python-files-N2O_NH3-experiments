import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("measurements/calibration_NH3_147mvpp_140flow.dat",)
print(df.head())

plt.plot(df.index, df.R)
plt.show()
