import lightgbm as lgb
import pandas as pd 
from sklearn import multiclass
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import numpy as np
import matplotlib.pyplot as plt



#ttps://re.jrc.ec.europa.eu/pvg_tools/es/#api_5.3
def main():
    # Load the dataset
    data = pd.read_csv('Solar_radiation_2018_2023.csv')
    data = data.drop(['Int','WS10m','H_sun','Gd(i)', 'Gr(i)' ] , axis=1)  # Eliminar la columna 'Int' si no es relevante para el modelo

    # Parse and separate the Time column
    data['year']   = pd.to_numeric(data['time'].str[0:4], errors='coerce')
    data['month']  = pd.to_numeric(data['time'].str[4:6], errors='coerce')
    data['day']    = pd.to_numeric(data['time'].str[6:8], errors='coerce')
    data['hour']   = pd.to_numeric(data['time'].str[9:11], errors='coerce')
    data['minute'] = pd.to_numeric(data['time'].str[11:13], errors='coerce')

    # --- CRITICAL STEP: Drop the rows that failed to parse (NaNs) ---
    data = data.dropna(subset=['year', 'month', 'day', 'hour'])

    # Now this will work
    data['year']   = data['year'].astype(int)
    data['month']  = data['month'].astype(int)
    data['day']    = data['day'].astype(int)
    data['hour']   = data['hour'].astype(int)
    data['minute'] = data['minute'].astype(int)
    
    # Convert time into cyclic features using sine/cosine
    def encode_cyclical(df, col, max_val):
        data[f'{col}_sin'] = np.sin(2 * np.pi * df[col] / max_val)
        data[f'{col}_cos'] = np.cos(2 * np.pi * df[col] / max_val)
        return df

    data = encode_cyclical(data, 'month', 12)
    data = encode_cyclical(data, 'day', 31)
    data = encode_cyclical(data, 'hour', 24)

    data = data.drop("month", axis=1)
    data = data.drop("day", axis=1)
    data = data.drop("hour", axis=1)
    data = data.drop("time", axis=1)
    data = data.drop("minute", axis=1)

    #data = data.drop("time", axis=1)
    # 1. Creamos la columna con el valor de la hora anterior
    data['T2m_last_hour'] = data['T2m'].shift(1)

    # 2. Calculamos la diferencia
    data['T_diff'] = data['T2m'] - data['T2m_last_hour']

    data['Gb(i)']   = data['Gb(i)'].astype(float)

    print(data.head(100))
    data.info()
    #data = data.drop(['Data', 'Time', 'Hour', 'Minute', 'Year', 'Month', 'Day'], axis=1)  # Eliminar las columnas originales de fecha y hora

    # Define features and target variable
    X = data.drop('Gb(i)', axis=1)
    #X = X.drop(['Data', 'Time'], axis=1)  # Eliminar las columnas 'data' y 'Time' si no son relevantes para el modelo
    y = data['Gb(i)']
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create LightGBM dataset
    train_data = lgb.Dataset(X_train, label=y_train)
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

    
    # Set parameters for LightGBM
    params = {
        'objective': 'regression',
        'metric': 'mae',
        'boosting_type': 'gbdt',
        'learning_rate': 0.03,          # Un poco más bajo para mayor precisión
        'num_leaves': 63,               # Aumentamos complejidad (solar es no-lineal)
        'max_depth': 8,                 # Profundidad moderada
        'min_data_in_leaf': 30,         # Evita hojas con muy pocos datos
        
        # Regularización para evitar Overfitting
        'feature_fraction': 0.7,        # Ayuda si tienes muchas variables climáticas
        'bagging_fraction': 0.7,        # Subsampling de filas
        'bagging_freq': 5,
        'lambda_l1': 0.5,               # Regularización más fuerte
        'lambda_l2': 0.5,
        
        # Optimización para radiación
        'extra_trees': True,            # Ayuda a generalizar mejor con datos ruidosos
        'path_smooth': 0.1,             # Suaviza las predicciones
        
        'seed': 42,
        'num_threads': -1,
        'verbose': -1
    }

    print("Entrenando al chikitin...")
    # Train the model
    model = lgb.train(
        params, 
        train_data, 
        valid_sets=[test_data], 
        num_boost_round=1000, 
        callbacks=[lgb.early_stopping(100, verbose=False)]
    )
    
    # Predict on the test set
    predictions = model.predict(X_test, num_iteration=model.best_iteration)


    # Evaluate the model (e.g., calculate RMSE)
    rmse = ((predictions - y_test) ** 2).mean() ** 0.5
    print(f'RMSE: {rmse}')

    mae = mean_absolute_error(y_test, predictions)
    print(f'MAE:  {mae:.4f}')

    lgb.plot_importance(model)
    plt.show()

if __name__ == "__main__":
    main()