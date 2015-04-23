from pymongo import MongoClient

class revealdb:
  def get_collection(str):
    client = MongoClient('localhost',27017)
    db = client['revealdb']
    return db[str]
  def find_sessions(query):
    collection = revealdb.get_collection('session')
    cursor = collection.find(query)
    return [Session(**doc) for doc in cursor]
  def find_experiments(query):
    collection = revealdb.get_collection('experiment')
    cursor = collection.find(query)
    return [Experiment(**doc) for doc in cursor]
  def find_scenarios(query):
    collection = revealdb.get_collection('scenario')
    cursor = collection.find(query)
    return [Scenario(**doc) for doc in cursor]
  def find_trials(query):
    collection = revealdb.get_collection('trial')
    cursor = collection.find(query)
    return [Trial(**doc) for doc in cursor]
  def find_models(query):
    collection = revealdb.get_collection('model')
    cursor = collection.find(query)
    return [Model(**doc) for doc in cursor]
  def find_solutions(query):
    collection = revealdb.get_collection('solution')
    cursor = collection.find(query)
    return [Solution(**doc) for doc in cursor]
  def find_analyzers(query):
    collection = revealdb.get_collection('analyzer')
    cursor = collection.find(query)
    return [Analyzer(**doc) for doc in cursor]
  def find_analyses(query):
    collection = revealdb.get_collection('analysis')
    cursor = collection.find(query)
    return [Analysis(**doc) for doc in cursor]

class User:
  def __init__(self):
    self._id = ""
    self.user_name = ""
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.user_name = kwargs['user_name']

class Session:
  def __init__(self):
    self._id = ""
    self.session_id = ""
    self.user_type = 0
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.session_id = kwargs['session_id']
    self.user_type = kwargs['user_type']

class Scenario:
  def __init__(self):
    self._id = ""
    self.scenario_id = ""
    self.description = ""
    self.trials = 0
    self.steps_per_trial = 0
    self.uris = []
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.scenario_id = kwargs['scenario_id']
    self.description = kwargs['description']
    self.trials = kwargs['trials']
    self.steps_per_trial = kwargs['steps_per_trial']
    self.uris = []

class Experiment:
  def __init__(self):
    self._id = ""
    self.experiment_id = ""
    self.session_id = ""
    self.scenario_id = ""
    self.trials = 0
    self.steps_per_trial = 0
    self.trial_index = 0
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.experiment_id = str(kwargs['experiment_id'])
    self.session_id = kwargs['session_id']
    self.scenario_id = kwargs['scenario_id']
    self.trials = kwargs['trials']
    self.steps_per_trial = kwargs['steps_per_trial']
    self.trial_index = kwargs['current_trial_index']

class Trial:
  def __init__(self):
    self._id = ""
    self.scenario_id = ""
    self.trial_id = 0
    self.time = 0
    self.time_step = 0
    self.models = []
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.scenario_id = kwargs['scenario_id']
    self.trial_id = kwargs['trial_id']
    self.time = kwargs['t']
    self.time_step = kwargs['dt']
    self.models = []

class Model:
  def __init__(self):
    self._id = ""
    self.scenario_id = ""
    self.trial_id = 0
    self.time = 0
    self.time_step = 0
    self.models = []
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.scenario_id = kwargs['scenario_id']
    self.trial_id = kwargs['trial_id']
    self.time = kwargs['t']
    self.time_step = kwargs['dt']
    self.models = []

class Solution:
  def __init__(self):
    self._id = ""
    self.scenario_id = ""
    self.trial_id = 0
    self.time = 0
    self.time_step = 0
    self.models = []
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.scenario_id = kwargs['scenario_id']
    self.trial_id = kwargs['trial_id']
    self.time = kwargs['t']
    self.time_step = kwargs['dt']
    self.models = []

class Analyzer:
  def __init__(self):
    self._id = ""
    self.scenario_id = ""
    self.type = 0
    self.file = 0
    self.keys = []
    self.labels = []
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.scenario_id = kwargs['scenario_id']
    self.type = kwargs['type']
    self.file = kwargs['filename']
    self.keys = kwargs['keys']
    self.labels = kwargs['labels']

class Analysis:
  def __init__(self):
    self._id = ""
    self.session_id = ""
    self.experiment_id = ""
    self.scenario_id = ""
    self.values = []
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.session_id = kwargs['session_id']
    self.experiment_id = kwargs['experiment_id']
    self.scenario_id = kwargs['scenario_id']
    self.values = kwargs['values']

