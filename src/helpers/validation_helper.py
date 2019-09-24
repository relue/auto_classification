from sklearn.metrics import accuracy_score,f1_score,precision_score,\
    recall_score, confusion_matrix,average_precision_score,balanced_accuracy_score
import numpy as np

def get_validation_score(y, y_pred):
    validation_summary = {}
    validation_summary["accuracy"] = float(accuracy_score(y, y_pred))
    validation_summary["f1"] = float(f1_score(y, y_pred))
    validation_summary["precision"] = float(precision_score(y, y_pred))
    validation_summary["recall"] = float(recall_score(y, y_pred))
    validation_summary["occurence"] = float(sum(y)/len(y))

    validation_summary["confusion_matrix"] = {}
    validation_summary["confusion_matrix"]["tn"], \
    validation_summary["confusion_matrix"]["fp"], \
    validation_summary["confusion_matrix"]["fn"], \
    validation_summary["confusion_matrix"]["tp"] = confusion_matrix(y, y_pred, labels=[0, 1]).ravel()
    tab = ["tn","fp","fn","tp"]
    for v in tab:
        validation_summary["confusion_matrix"][v] = int(validation_summary["confusion_matrix"][v])
    validation_summary["fpr"] = float(validation_summary["confusion_matrix"]["fp"] / (
                validation_summary["confusion_matrix"]["fp"] + validation_summary["confusion_matrix"]["tn"]))
    return validation_summary

def get_validation_scores_multi(y, y_pred):
    scores = {}
    class_vals = list(set(y))
    class_rows = []
    class_rows_pred = []
    for class_val in class_vals:
        bin_y = [1 if ye == class_val else 0 for ye in y]
        bin_y_pred = [1 if ye == class_val else 0 for ye in y_pred]
        scores[str(class_val)] = get_validation_score(bin_y, bin_y_pred)
        class_rows.append(bin_y)
        class_rows_pred.append(bin_y_pred)
    scores["avg"] = {"average_precision":average_precision_score(np.array(class_rows).T, np.array(class_rows_pred).T,average="micro"),
                     "average_f1":f1_score(y, y_pred,average="micro"),
                     "average_recall":balanced_accuracy_score(y, y_pred)
                     }
    scores["accuracy"] = accuracy_score(y, y_pred)
    return scores



