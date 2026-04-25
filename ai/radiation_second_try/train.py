import lightgbm as lgb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from sklearn.metrics import mean_squared_error
#from main import preprocess_weather_data

df = pd.read_csv('radiationPrediction.csv')
#df['Summary'] = df['Summary'].astype('category')

x = df.drop("ALLSKY_SFC_SW_DWN", axis=1)
y = df["ALLSKY_SFC_SW_DWN"]
       
x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.15, random_state = 67) 

lgb_train = lgb.Dataset(x_train, y_train)
lgb_eval = lgb.Dataset(x_test, y_test, reference=lgb_train)

params = {
    'objective': 'regression',
    'metric': 'rmse',         # Usamos MAE ya que es lo que estás midiendo
    'boosting_type': 'gbdt',
    'verbosity': -1,
    'seed': 67,

    # --- Parámetros de Complejidad ---
    'num_leaves': 63,         # Tamaño máximo del árbol. 31 es estándar y robusto.
    'learning_rate': 0.05,    # Un paso más pequeño ayuda a converger mejor (0.01 a 0.1).

}

print("entrenando al chikitin...")


gbm = lgb.train(
    params,
    lgb_train,
    valid_sets=[lgb_eval],
    num_boost_round=1000,
    callbacks=[lgb.early_stopping(500, verbose=False)]
)

y_pred = gbm.predict(x_test, num_iteration=gbm.best_iteration)
gbm.save_model('radiation_prediction.txt')

mae = mean_absolute_error(y_test, y_pred)
print(mae)

print((mae/y.mean()) * 100)

mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
print(rmse)
lgb.plot_importance(gbm)
plt.show()
