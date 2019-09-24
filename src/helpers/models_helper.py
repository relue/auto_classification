import pandas as pd
from sklearn.feature_selection import SelectKBest, chi2, f_regression
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import svm
from sklearn.linear_model import LogisticRegression
import pandas as pd
from sklearn.model_selection import KFold
import numpy as np
import collections
from sklearn.ensemble import RandomForestClassifier
import auto_classification.src.helpers.experiment_helper as eh
import auto_classification.src.helpers.validation_helper as validation_helper

def decide_class_val(df, def_d):
    max_proba = 0
    val = "0"
    for key, d in def_d.items():
        if df[key+"_pred"] == 1:
            if  df[key+"_proba"] > max_proba:
                max_proba = df[key+"_proba"]
                val = key.split("_")[-1]
    return val

def combine_models(bin_pred_d, test_df):
    test_df = test_df.copy(deep=True)
    for key, d in bin_pred_d.items():
        test_df[key+"_pred"] = d["preds"]
        test_df[key+"_proba"] = d["pred_probas"]
    test_df["pred_class_combined"] = test_df.apply(decide_class_val,def_d = bin_pred_d,axis=1)
    return test_df

def execute_model(param, train_df, test_df_d, label_col, feature_cols):
    X_train = train_df[feature_cols].values
    y_train = train_df[label_col]
    x_test_d = {}
    for name,test_df in test_df_d.items():
        x_test_d[name] = test_df[feature_cols].values
    info_d = {}
    y_preds_d = {}
    y_pred_probas_d = {}

    if param["model_type"] == "svm":
        model = svm.SVC(kernel='linear',probability=True) #,kernel="linear"
        model.fit(X_train, y_train)

    elif param["model_type"] == "regression":
        model = LogisticRegression(random_state=0, solver='liblinear',multi_class = 'ovr')
        model.fit(X_train, y_train)

        cols = train_df[feature_cols].drop(columns=[label_col], axis=1).columns
        info_d["coefs"] = pd.concat([pd.DataFrame(cols),pd.DataFrame(np.transpose(model.coef_))], axis=1)
        print (info_d["coefs"])

    elif param["model_type"] == "xgboost":
        model = XGBClassifier(max_depth=3,n_estimators=2)
        model.fit(X_train, y_train,verbose=True)

    elif param["model_type"] == "randomforest":
        model  = RandomForestClassifier(n_estimators=100, max_depth=3)
        model.fit(X_train, y_train)
    else:
        raise ValueError("modeltype not exists: "+param["model_type"])

    for name, test_df in x_test_d.items():
        y_preds_d[name] = model.predict(x_test_d[name])
        y_pred_probas_d[name] = model.predict_proba(x_test_d[name])

    return y_preds_d, y_pred_probas_d, info_d

def split_df(frac, df):
    t,v = train_test_split(df, test_size=frac,random_state=2)
    return t,v

def create_multiclass_exp(params_diff, fullP, exp_name, label_cols):
    db = eh.ParallelHelper.instance()
    fullP["type"] = "combined"
    job_id_parent = db.writeNewParameters(params_diff, fullP, exp_name)

    for label_col in label_cols:
        fullP["type"] = "single"
        fullP["parent_id"] = job_id_parent
        fullP["feature_conf"]["label_col"] = label_col
        db.writeNewParameters(params_diff, fullP, exp_name)

def get_model_validated(model_conf, df_train, test_d, label_col, feature_cols):
    preds, probas, info_d = execute_model(model_conf, df_train, test_d, label_col,
                                                        feature_cols)
    scores_d = {}
    results_d = {}
    for test_name, pred in preds.items():
        scores_d[test_name] = validation_helper.get_validation_score(preds[test_name], list(df_test[label_col]))
    print(scores_d)
    results_d["scores"] = scores_d
    results_d["info"] = info_d
    results_d["preds"] = preds
    results_d["probas"] = probas