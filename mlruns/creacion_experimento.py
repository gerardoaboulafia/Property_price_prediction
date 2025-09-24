import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.create_experiment("xgboost_models")
