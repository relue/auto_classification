import pandas as pd
import auto_classification.src.helpers.preprocess_helper as preprocess_helper

def prepare_dataset(params, df_features):
    df_features_trans = df_features
    feature_cols = params["feature_cols"]
    id_cols = params["id_cols"]
    max_bins = params["max_bins"]
    dummy_na = params["dummy_na"]

    handling = preprocess_helper.get_column_type_info(df_features_trans, feature_cols)
    dummy_cols = [col for col, hand in handling.items() if
                  handling[col]["type"] == "string" and (handling[col]["count"] < 50)]
    num_cols = [col for col, hand in handling.items() if
                handling[col]["count"] > 2 and handling[col]["type"] == "numeric"]

    for col in num_cols:
        df_features_trans[col] = pd.cut(df_features_trans[col], max_bins, labels=[str(x) for x in range(max_bins)])
    bin_cols = [col for col, hand in handling.items() if handling[col]["type"] == "binary"]
    dummy_cols = bin_cols + dummy_cols + num_cols

    select_cols = id_cols + dummy_cols
    df_features_trans_dum = pd.get_dummies(df_features_trans[select_cols], prefix=dummy_cols, columns=dummy_cols,
                                           dummy_na=dummy_na)
    # selection methods
    final_cols = df_features_trans_dum.columns.sort_values().tolist()
    feature_cols_new = list(set(final_cols) - set(id_cols))
    df_final = df_features_trans_dum[id_cols + feature_cols_new]

    renamed_cols = {}
    for col in df_final.columns:
        renamed_cols[col] = col.replace(".", "p")
    df_final = df_final.rename(columns=renamed_cols)
    df_final[params["label_col"]] =  df_features[params["label_col"]]
    df_final = pd.get_dummies(df_final, prefix=["lbl"],columns=[params["label_col"]])
    ren_d = {}
    for fcol in feature_cols_new:
        ren_d[fcol] = "f_"+fcol
    df_final = df_final.rename(columns=ren_d)
    label_cols = [col for col in df_final.columns.tolist() if "lbl" in col]
    feature_cols_new = [col for col in df_final.columns.tolist() if "f_" in col]
    return df_final, feature_cols_new, label_cols