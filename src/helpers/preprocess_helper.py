from pandas.api.types import is_string_dtype

def get_column_type_info(df_features, cols):
    handling = {}
    for col in cols:
        handling[col] = {}
        if is_string_dtype(df_features[col]) or df_features[col].dtype == "O":
            handling[col]["count"] = len(df_features[col].value_counts(dropna = False))
            handling[col]["type"] = "string"
        else:
            handling[col]["count"] = len(df_features[col].value_counts(dropna = False))
            handling[col]["type"] = "numeric"
            if handling[col]["count"] == 2:
                handling[col]["type"] = "binary"
    return handling