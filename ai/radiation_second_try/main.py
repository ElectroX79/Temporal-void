import lightgbm as lgb
import pandas as pd
import numpy as np

df=pd.read_csv('POWER_Point_Hourly_20210101_20251231_041d39N_002d17E_LST.csv')

#df = df[df['ALLSKY_SFC_SW_DWN'] > 0]

# date stuff
df['day_of_year'] = pd.to_datetime(df[['YEAR', 'MO', 'DY']].rename(columns={
    'YEAR' : 'year',
    'MO' : 'month',
    'DY' : 'day'
})).dt.dayofyear

#cyclial
def encode_cyclical(df, col, max_val):
    df[f'{col}_sin'] = np.sin(2 * np.pi * df[col] / max_val)
    df[f'{col}_cos'] = np.cos(2 * np.pi * df[col] / max_val)
    return df

# Apply encoding
df = encode_cyclical(df, 'MO', 12)
df = encode_cyclical(df, 'HR', 24)
df = encode_cyclical(df, 'day_of_year', 365)

df=df.drop("MO", axis=1)
#df=df.drop("HR", axis=1)
df=df.drop("day_of_year", axis=1)

#cositas
b = 17.625
c = 243.04

gamma = np.log(df['RH2M'] / 100) + (b * df['T2M']) / (c + df['T2M'])

df['dew_point'] = (c * gamma) / (b - gamma)

df['temp_lag1'] = df['T2M'].shift(1)
df['temp_lag2'] = df['T2M'].shift(2)

df['temp_diff_1h'] = df['T2M'] - df['temp_lag1']

df['hum_lag1'] = df['RH2M'].shift(1)
df['hum_lag2'] = df['RH2M'].shift(2)

df['hum_diff_1h'] = df['RH2M'] - df['hum_lag1']

df = df.dropna().reset_index(drop=True)

print(df.info())
print(df.head())

df.to_csv("radiationPrediction.csv", index = False)