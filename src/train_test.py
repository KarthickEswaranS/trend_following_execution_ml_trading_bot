from src.execution import Execution
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import  accuracy_score


class TrainTest(Execution):

    def __init__(self):
        super().__init__()
        self.train_test()

    def modify_df(self):
        df = self.buy_sell().copy()

        df.loc[df['enter_long'] == True, 'target'] = 1
        df.loc[df['enter_short'] == True, 'target'] = 0

        df = df.dropna(subset=['target'])

        return df
    
    def train_test(self):
        df = self.modify_df() 
        features = ['open', 'high', 'low', 'close', 'lip', 'teeth', 'jaw' ]
        X = df[features].values
        y = df['target'].values

        t = TimeSeriesSplit(n_splits=5)

        for train_idx, test_idx in t.split(X):
          X_train, X_test = X[train_idx], X[test_idx]
          y_train, y_test = y[train_idx], y[test_idx]   

          print("TRAIN SHAPE:", X_train.shape, "TEST SHAPE:", X_test.shape)

        model = RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        print("Accuracy:", accuracy_score(y_test, preds))
    
     
t = TrainTest()