import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("measurements/background_test_lockin03_cabooscilo_nobreak_caixaDANIEL.dat",)
print(df.head())

plt.plot(df.index, df.R)
plt.show()
