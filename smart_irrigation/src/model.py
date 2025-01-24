from sklearn.model_selection import GridSearchCV
from xgboost import XGBRegressor
import numpy as np


def optimize_xgboost(X_train, X_test, y_train, y_test):
    # Define parameter grid
    param_grid = {
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.3],
        'n_estimators': [100, 200],
        'min_child_weight': [1, 3],
        'subsample': [0.8, 0.9, 1.0],
        'colsample_bytree': [0.8, 0.9, 1.0]
    }

    # Create base model
    xgb = XGBRegressor(random_state=42)

    # Initialize GridSearchCV
    grid_search = GridSearchCV(
        estimator=xgb,
        param_grid=param_grid,
        cv=5,
        scoring='r2',
        n_jobs=-1,
        verbose=2
    )

    # Fit Grid Search
    grid_search.fit(X_train, y_train)

    # Print best parameters and score
    print("\nBest parameters found:")
    print(grid_search.best_params_)
    print(f"\nBest R² score: {grid_search.best_score_:.4f}")

    return grid_search.best_estimator_