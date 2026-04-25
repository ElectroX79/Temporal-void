import lightgbm as lgb
import pandas as pd 
from sklearn.model_selection import train_test_split

def main():
    # Load the dataset
    data = pd.read_csv('SolarPrediction.csv')
    
    # Preprocess the data (handle missing values, encode categorical variables, etc.)
    data.fillna(data.mean(), inplace=True)
    
    # Define features and target variable
    X = data.drop('radiation_level', axis=1)
    y = data['radiation_level']
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create LightGBM dataset
    train_data = lgb.Dataset(X_train, label=y_train)
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
    
    # Set parameters for LightGBM
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.9
    }
    
    # Train the model
    model = lgb.train(params, train_data, valid_sets=[test_data], num_boost_round=1000, early_stopping_rounds=50)
    
    # Predict on the test set
    predictions = model.predict(X_test, num_iteration=model.best_iteration)
    
    # Evaluate the model (e.g., calculate RMSE)
    rmse = ((predictions - y_test) ** 2).mean() ** 0.5
    print(f'RMSE: {rmse}')

if __name__ == "__main__":
    main()