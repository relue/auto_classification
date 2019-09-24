import numpy as np
import json
param_ranges = {}
param_ranges["xgboost"] = {'max_depth': range(5, 22),
                        "learning_rate": [0.1,0.05],
                        "gamma": [0, 0.1, 1, 5],
                        "etc": [0.1, 0.2, 0.3],
                        "subsample":[1,0.5,0.8],
                        "trial_iterations": [40],
                        "scale_pos_weight":[1,2,3,5,10,50],
                        "tree_method":["gpu_hist"]
                        }

param_ranges["mlp"] = {'hidden_neurons': range(100, 5100,1000)+[20,6000],
                    "activation_function": ["relu","sigmoid","tanh"],
                   "dropout_prop": [0,0.05,0.1,0.2,0.3],
                   "l1": [0,0.001],
                   "l2": [0,0.001],
                   "trial_iterations": [30],
                   "batch_size": [100],
                   "class_weight":[1,2,3,5,10,50],
                   }

param_ranges["svm"] = {'gamma': [0,1],
                    "kernel": ["linear","rbf","poly"],
                    "class_weight":[1,2,3,5,10,50],
                    "cache_size":[8000],
                    'C': np.logspace(-3, 2, 6).tolist(),
                    'gamma': np.logspace(-3, 2, 6).tolist()
                   }

param_ranges["rf"] = {'gamma': [0,1],
                    "kernel": ["linear","rbf","poly"],
                    "class_weight":[1,2,3,5,10,50],
                    "cache_size":[8000],
                    'C': np.logspace(-3, 2, 6).tolist(),
                    'gamma': np.logspace(-3, 2, 6).tolist()
                   }
