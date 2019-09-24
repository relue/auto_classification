import pandas as pd
import collections

def create_result_table(exp_name):
    pho = ph.ParallelHelper()
    jobs = pho.getJobByState(exp_name)
    rows =[]
    for res in jobs["finished"]:
        new_d = collections.OrderedDict()
        new_d["expname"] = res["experimentName"]
        new_d["date"] = res["date"]
        new_d["class"] = res["paramsFull"].get("class")
        new_d["parent_class"] = res["paramsFull"]["parent_class"]
        new_d["model_type"] = res["paramsFull"]["model_type"]
        new_d["params"] = res["paramsFull"]

        if res["paramsDiff"]["class"] != "combined":
            new_d["f1"] = res["results"]["f1"]
            new_d["precision"] = res["results"]["precision"]
            new_d["recall"] = res["results"]["recall"]
            new_d["fpr"] = res["results"].get("fpr")
            new_d["accuracy"] = res["results"]["accuracy"]
            new_d["occurence"] = res["results"].get("occurence")
            new_d["feat_scores"] = res["results"].get("feat_scores")
            if res["results"].get("confusion_matrix"):
                new_d["cm_tp"] = res["results"]["confusion_matrix"].get("tp")
                new_d["cm_tn"] = res["results"]["confusion_matrix"].get("tn")
                new_d["cm_fn"] = res["results"]["confusion_matrix"].get("fn")
                new_d["cm_fp"] = res["results"]["confusion_matrix"].get("fp")
        else:
            new_d["f1"] = res["results"]["avg"]["average_f1"]
            new_d["precision"] = res["results"]["avg"]["average_precision"]
            new_d["recall"] =res["results"]["avg"]["average_recall"]
        rows.append(new_d)
    # pass
    df = pd.DataFrame(data=rows)
    return df