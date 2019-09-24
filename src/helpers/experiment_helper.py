import pymongo
import datetime
import socket
import copy
import collections
from bson.objectid import ObjectId

import gridfs


class Singleton:
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@Singleton
class ParallelHelper:
    experimentParams = {}

    def __init__(self):
        print ("init")

    def init_connection(self,experimentParams):
        self.mongoConnection = experimentParams["connection"]
        self.client = pymongo.MongoClient(self.mongoConnection)
        self.db = self.client.jobs
        self.gridfs_db = self.client.bigfiles
        collectionName = experimentParams["projectName"]
        self.collectionObj = self.db[collectionName]

    def put_content_gridfs(self,content):
        fs = gridfs.GridFS(self.gridfs_db )
        a = fs.put(content,encoding='utf-8')
        return a

    def get_content_gridfs(self, id):
        fs = gridfs.GridFS(self.gridfs_db )
        if fs.exists(id):
            content = fs.get(id).read()
        else:
            raise FileNotFoundError("GridFs key not existing")
        return content

    def free_query(self, query_d, exclude = None, sort = None, limit = None):
        if exclude:
            res = self.collectionObj.find(query_d, exclude)
        else:
            res = self.collectionObj.find(query_d)

        if sort:
            res.sort(sort)

        if limit:
            res.limit(limit)
        return res

    def getNewParameters(self, expName = "", sort_t = []):
        dictSearch = {'status': "new"}
        if len(expName) > 0:
            dictSearch["experimentName"] = expName
        one = self.collectionObj.find(dictSearch)
        data = False
        params = False
        if one.count():
            sorts = [("priority",pymongo.DESCENDING)]+sort_t
            data = one.sort(sorts).limit(1)[0]
            params = data["paramsFull"]
        return data, params

    def set_running(self, job):
        id = job["_id"]
        self.collectionObj.update({'_id': id}, {"$set": {'status': 'running', 'host': socket.gethostname()}},
                                  upsert=False)
        return True

    def getJobByState(self, expName = None, only_fields = None):
        if expName:
            exp = {'experimentName': expName}
        else:
            exp = {}
        if only_fields:
            objs = self.collectionObj.find(exp, only_fields)
        else:
            objs = self.collectionObj.find(exp)

        jobs = {}
        jobs["new"] = []
        jobs["running"] = []
        jobs["finished"] = []
        jobs["failed"] = []
        for obj in objs:
            jobs[obj["status"]].append(obj)

        return jobs

    def writeNewParameters(self, params, fullP, experimentName, commentText="", priority = 1):
        now = datetime.datetime.now()
        parameter = {
            "experimentName": experimentName,
            "paramsDiff": params,
            "paramsFull": fullP,
            "status": "new",
            "date": now,
            "dateFeedback": "",
            "results": "",
            "resultsTemp": "",
            "comment":commentText,
            "priority": priority,
            "host": "",
            "errors": ""
        }
        id = self.collectionObj.insert_one(parameter).inserted_id
        return id

    def writeNewJob(self, param):
        now = datetime.datetime.now()
        param["date"] = now
        id = self.collectionObj.insert_one(param).inserted_id
        return id

    def registerSlave(self, slaveIp, awsId):
        collection = experimentParams["projectName"]+"_slaves"
        now = datetime.datetime.now()
        parameter = {
            "slaveIP": slaveIp,
            "awsId": awsId,
            "lastChecked":now,
            "birthTime":now,
            "status": "created",
            "date_finished": "",
            "finished_jobs": 0
        }
        id = self.db[collection].insert_one(parameter).inserted_id
        return id

    def updateSlave(self, id, jobC, lastParam="", comment=""):
        collection = experimentParams["projectName"] + "_slaves"
        now = datetime.datetime.now()
        parameter = {
            "lastChecked": now,
            "status": "pending",
            "finished_jobs":jobC,
            "last_param": lastParam,
            "comment": comment
        }
        self.db[collection].update({'_id': id}, {"$set": parameter}, upsert=False)

    def unregisterSlave(self, id, lastParam ="", error = ""):
        collection = experimentParams["projectName"] + "_slaves"
        now = datetime.datetime.now()
        parameter = {
            "lastChecked": now,
            "status": "finished",
            "date_finished": now,
            "last_param": lastParam,
            "comment": error,
            "error": error
        }
        self.db[collection].update({'_id':id},{"$set":parameter}, upsert=False)

    def clearSlaves(self):
        collection = experimentParams["projectName"] + "_slaves"
        self.db[collection].drop()

    def clear_experiment(self, exp_name, cond = None):
        q = {"experimentName": exp_name}
        if cond:
            q.update(cond)
        x = self.collectionObj.delete_many(q)
        return x.deleted_count

    def del_job(self, id):
        res = self.collectionObj.delete_one({"_id": ObjectId(id)})
        success = False

        if res.acknowledged:
            return True

    def get_job(self, id):
        res = self.collectionObj.find_one({"_id": ObjectId(id)})
        return res

    def checkSlaves(self):
        collection = experimentParams["projectName"] + "_slaves"
        one = collection.find({'status': "new"})
        return one

    def writeError(self, parameterJob, msg, elapsed = 0):
        id = parameterJob["_id"]
        now = datetime.datetime.now()
        self.collectionObj.update({'_id':id},{"$set":{"status": "failed", "elapsed": elapsed,  "errors": msg, "dateFeedback": now}}, upsert=False)

    def writeResult(self, parameterJob, results, elapsed = 0):
        id = parameterJob["_id"]
        now = datetime.datetime.now()
        self.collectionObj.update({'_id':id},{"$set":{'results':results, "elapsed": elapsed, "status": "finished",  "dateFeedback": now}},upsert=False)

    def update_query(self, parameterJob, query_d, query_d_unset = {}):
        id = parameterJob["_id"]
        now = datetime.datetime.now()
        query_d_fin = query_d
        query_d_fin["dateFeedback"] = now

        update_q = {"$set": query_d_fin}
        if query_d_unset:
            update_q["$unset"] = query_d_unset
        res = self.collectionObj.update({'_id':id},update_q,upsert=False)
        return res["ok"]


    def writeTempResult(self, parameterJob, results, estTimeRemain):
        id = parameterJob["_id"]
        now = datetime.datetime.now()
        self.collectionObj.update({'_id': id}, {
            "$set": {'resultsTemp': results, 'estTimeRemain': estTimeRemain, "status": "updated",
                     "dateFeedback": now}}, upsert=False)

    def get_diff_exp_config(self, base_conf, var_conf, repeats = 1, name_pref = ""):
        var_nodes =  self.flatten_dict(var_conf)
        exps = []
        exps_changed = []
        for key, var_list in var_nodes.items():
            for el in var_list:
                paths = key.split(".")
                name = name_pref+paths[-1].replace(".","_")+"_"+str(el)
                data = copy.deepcopy(base_conf)
                for path in paths:
                    if path != paths[-1]:
                        data = data[path]

                paths = key.split(".")
                paths_r = paths[::-1]
                new_data = {}
                new_data[paths_r[0]] = el
                for path_r in paths_r:
                    if path_r != paths_r[0]:
                        new_data_parent = {}
                        new_data_parent[path_r] = new_data
                        new_data = new_data_parent

                if data[paths[-1]] != el:
                    for r in range(1,repeats+1):
                        data[paths[-1]] = el
                        name_r = name
                        if repeats > 1:
                            name_r = "_"+name+"_r"+str(r)
                            new_data["repeat"] = r
                        final_conf = self.update(copy.deepcopy(base_conf), new_data)
                        final_conf["name"] = final_conf["name"] +"_"+ name_r
                        exps.append(final_conf)
                        exps_changed.append(new_data)

        return exps, exps_changed

    def flatten_dict(self,d):
        def items():
            for key, value in d.items():
                if isinstance(value, dict):
                    for subkey, subvalue in self.flatten_dict(value).items():
                        yield key + "." + subkey, subvalue
                else:
                    yield key, value

        return dict(items())

    def update(self, orig_dict, new_dict):
        for key, val in new_dict.items():
            if isinstance(val, collections.Mapping):
                tmp = self.update(orig_dict.get(key, {}), val)
                orig_dict[key] = tmp
            elif isinstance(val, list):
                orig_dict[key] =  val
            else:
                orig_dict[key] = new_dict[key]
        return orig_dict

