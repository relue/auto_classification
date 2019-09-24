import auto_classification.src.helpers.models_helper as models_helper
import pandas as pd

def run_model(full_conf):
    #get model from database
    #load dataset train/test from preprocessed
    if full_conf["model_conf"]["cv"] == True:
        pass
    else:
        df_full = pd.read_csv(full_conf["feature_conf"]["df_preprocessed_fp"])
        df_full = df_full.set_index(full_conf["feature_conf"]["id_cols"][0])

        df_train = df_full.loc[full_conf["internal_conf"]["train_def"]]
        test_d_real = {}
        for name, test_index in full_conf["internal_conf"]["test_def"].items():
            test_d_real = {name: df_full.loc[test_index]}
        res = models_helper.get_model_validated(full_conf["model_conf"],
                                                df_train,
                                                test_d_real,
                                                full_conf["feature_conf"]["label_col"],
                                                full_conf["feature_conf"]["feature_cols"])
    return res

