#!/usr/bin/python3.7

from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV
        
def nonlinear_hyperparameters_tuning(X_daily, Y_pm25, Y_pm10):
    hyperparameters_decision_tree = {
        'max_features': ['sqrt', 'log2', None],
        'max_depth': [2, 4, 6, 8]
    }
    
    hyperparameters_random_forest = {
        'max_features': ['sqrt', 'log2', None],
        'n_estimators': [50, 100, 150, 200, 250],
        'max_depth': [2, 4, 6, 8]
    }

    print('\nDecision tree hyperparameters tuning results for PM25:')
    execute_hypertuning(DecisionTreeRegressor(), hyperparameters_decision_tree, X_daily, Y_pm25)
    
    print('\nDecision tree hyperparameters tuning results for PM10:')
    execute_hypertuning(DecisionTreeRegressor(), hyperparameters_decision_tree, X_daily, Y_pm10)
    
    print('\n\nRandom forest hyperparameters tuning results for PM25:')
    execute_hypertuning(RandomForestRegressor(), hyperparameters_random_forest, X_daily, Y_pm25)
    
    print('\nRandom forest hyperparameters tuning results for PM10:')
    execute_hypertuning(RandomForestRegressor(), hyperparameters_random_forest, X_daily, Y_pm10)
    
def xgboost_hyperparameters_tuning(X_daily, Y_pm25, Y_pm10):
    hyperparameters_xgboost = {
        'learning_rate': [0.0001, 0.001, 0.01, 0.1],
        'n_estimators': [50, 100, 200, 500, 1000],
        'max_depth': [2, 4, 6, 8]
    }

    print('\n\nXGBoost hyperparameters tuning results for PM25:')
    execute_hypertuning(XGBRegressor(), hyperparameters_xgboost, X_daily, Y_pm25)
    
    print('\nXGBoost hyperparameters tuning results for PM10:')
    execute_hypertuning(XGBRegressor(), hyperparameters_xgboost, X_daily, Y_pm10)
    
def execute_hypertuning(model, hyperparameters, X_daily, Y_daily):
    # grid search
    grid_search = GridSearchCV(model, hyperparameters, scoring="neg_mean_squared_error", n_jobs=-1, cv=5)
    grid_result = grid_search.fit(X_daily, Y_daily)

    # summarize results
    print(f'Best hyperparameters: {grid_result.best_score_} using {grid_result.best_params_}')
    
    means = grid_result.cv_results_['mean_test_score']
    stds = grid_result.cv_results_['std_test_score']
    params = grid_result.cv_results_['params']
    for mean, stdev, param in zip(means, stds, params):
        print(f'{mean} ({stdev}) with: {param}')