from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING
import json
#from django.core import serializers

#------------------------------------------------------------------------------
class revealdb:
  host = None
  port = None
  dbname = None
  def __init__( self ):
    self.host = 'localhost'
    self.port = 27017
    self.dbname = 'reveal_samples'
  def get_collection( self, str ):
    client = MongoClient( self.host, self.port )
    db = client[self.dbname]
    return db[str]
  def find_records( self, doc, query ):
    collection = self.get_collection( doc )
    return collection.find( query )
  def find_sorted_records( self, doc, query, sortby, sortdirection ):
    collection = self.get_collection( doc )
    return collection.find( query ).sort( sortby, sortdirection )
  def find_first_record( self, doc, query, sortby ):
    cursor = self.find_sorted_records( doc, query, sortby, ASCENDING )
    return cursor[0]
  def find_last_record( self, doc, query, sortby ):
    cursor = self.find_sorted_records( doc, query, sortby, DESCENDING )
    return cursor[0]
  def count_records( self, doc, query ):
    return self.find_records( doc, query ).count()
  def count_models( self, query ):
    return self.count_records( 'model', query )
  def count_trials( self, query ):
    return self.count_records( 'trial', query )
  def find_sessions( self, query ):
    sessions = []
    errors = []
    cursor = self.find_records( 'session', query )
    for doc in cursor:
      try:
        session = Session( **doc )
        sessions.append( session )
      except:
        errors.append('ignoring corrupted session record [session_id:' + doc['session_id']+']')
    return {'sessions':sessions, 'errors':errors}
  def find_experiments( self, query ):
    experiments = []
    errors = []
    cursor = self.find_records( 'experiment', query )
    for doc in cursor:
      try:
        experiment = Experiment( **doc )
        experiments.append( experiment )
      except:
        errors.append('ignoring corrupted experiment record [experiment_id:' + doc['experiment_id']+']')
    return {'experiments':experiments, 'errors':errors}
  def find_scenarios( self, query ):
    scenarios = []
    errors = []
    cursor = self.find_records( 'scenario', query )
    for doc in cursor:
      models = self.count_models( {'scenario_id':doc['scenario_id']} )
      trials = self.count_trials( {'scenario_id':doc['scenario_id']} )
      try:
        scenario = Scenario( models, trials, **doc )
        scenarios.append( scenario )
      except:
        errors.append('ignoring corrupted scenario record [scenario_id:' + doc['scenario_id']+']')
    return {'scenarios':scenarios, 'errors':errors}
  def find_trials( self, query ):
    cursor = self.find_records( 'trial', query )
    return [Trial( **doc ) for doc in cursor]
  def find_models( self, query ):
    cursor = self.find_records( 'model', query )
    return [Model( **doc ) for doc in cursor]
  def find_solutions( self, query ):
    cursor = self.find_records( 'solution', query )
    return [Solution( **doc ) for doc in cursor]
  def count_solutions( self, scenario_id, experiment_id ):
    query = { 'scenario_id':scenario_id, 'experiment_id':experiment_id }
    return self.count_records( 'solution', query )
  def find_solution_min_t( self, scenario_id, experiment_id ):
    query = { 'scenario_id':scenario_id, 'experiment_id':experiment_id }
    return Solution( **self.find_first_record( 'solution', query, 't' ) )
  def find_solution_max_t( self, scenario_id, experiment_id ):
    query = { 'scenario_id':scenario_id, 'experiment_id':experiment_id }
    return Solution( **self.find_last_record( 'solution', query, 't' ) )
  def find_analyzers( self, query ):
    cursor = self.find_records( 'analyzer', query )
    return [Analyzer( **doc ) for doc in cursor]
  def find_analyses( self, query ):
    cursor = self.find_records( 'analysis', query )
    return [Analysis( **doc ) for doc in cursor]
#------------------------------------------------------------------------------
class User:
  def __init__(self):
    self._id = ""
    self.user_id = ""
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.user_id = kwargs['user_id']

#------------------------------------------------------------------------------
class Session:
  def __init__(self):
    self._id = ""
    self.session_id = ""
    self.user_type = 0
    self.user_id = ""
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.session_id = kwargs['session_id']
    self.user_type = kwargs['user_type']
    self.user_id = kwargs['user_id']

#------------------------------------------------------------------------------
class Scenario:
  _id = ""
  scenario_id = ""
  description = ""
  samples = 0
  sample_rate = 0.0
  sample_start_time = 0.0
  sample_end_time = 0.0
  uris = []
  def __init__(self):
    self._id = ""
    self.scenario_id = ""
    self.description = ""
    self.samples = 0
    self.sample_rate = 0.0
    self.sample_start_time = 0.0
    self.sample_end_time = 0.0
    self.uris = []
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.scenario_id = kwargs['scenario_id']
    self.description = kwargs['description']
    self.samples = kwargs['samples']
    self.sample_rate = kwargs['sample_rate']
    self.sample_start_time = kwargs['sample_start_time']
    self.sample_end_time = kwargs['sample_end_time']
    self.uris = []
  def __init__(self, models, trials, **kwargs):
    self._id = kwargs['_id']
    self.scenario_id = kwargs['scenario_id']
    self.description = kwargs['description']
    self.samples = models
    self.sample_rate = kwargs['sample_rate']
    self.sample_start_time = kwargs['sample_start_time']
    self.sample_end_time = kwargs['sample_end_time']
    self.uris = []
    self.trials = trials
#    self.steps_per_trial = kwargs['steps_per_trial']
  def to_JSON(self):
    return json.dumps( { 'sample_start_time': self.sample_start_time, 'description': self.description, 'sample_end_time': self.sample_end_time, 'sample_rate': self.sample_rate, 'samples': self.samples, 'scenario_id': self.scenario_id } )
    

#------------------------------------------------------------------------------
class Experiment:
  def __init__(self):
    self._id = ""
    self.experiment_id = ""
    self.session_id = ""
    self.scenario_id = ""
    self.start_time = 0.0
    self.end_time = 0.0
    self.time_step = 0.0
    self.epsilon = 0.0
    self.min_time = 0.0
    self.max_time = 0.0
    self.samples = 0
    self.intermediate_trials = 0
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.experiment_id = str(kwargs['experiment_id'])
    self.session_id = kwargs['session_id']
    self.scenario_id = kwargs['scenario_id']
    self.start_time = kwargs['start_time']
    self.end_time = kwargs['end_time']
    self.time_step = kwargs['time_step']
    self.epsilon = kwargs['epsilon']
    self.intermediate_trials = kwargs['intermediate_trials']
    self.get_stats()
  def get_stats(self):
    db = revealdb()
    rec_min_t = db.find_solution_min_t( self.scenario_id, self.experiment_id )
    rec_max_t = db.find_solution_max_t( self.scenario_id, self.experiment_id )
    self.min_time = rec_min_t.time
    self.max_time = rec_max_t.time
    self.samples = db.count_solutions( self.scenario_id, self.experiment_id )

#------------------------------------------------------------------------------
class Trial:
  def __init__(self):
    self._id = ""
    self.scenario_id = ""
    self.time = 0
    self.models = []
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.scenario_id = kwargs['scenario_id']
    self.time = kwargs['t']
    self.models = []

#------------------------------------------------------------------------------
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

#------------------------------------------------------------------------------
class Solution:
  def __init__(self):
    self._id = ""
    self.scenario_id = ""
    self.time = 0
    self.models = []
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.scenario_id = kwargs['scenario_id']
    self.time = kwargs['t']
    self.models = []

#------------------------------------------------------------------------------
class Analyzer:
  def __init__(self):
    self._id = ""
    self.scenario_id = ""
    self.type = 0
    self.keys = []
    self.labels = []
  def __init__(self, **kwargs):
    self._id = kwargs['_id']
    self.scenario_id = kwargs['scenario_id']
    self.type = kwargs['type']
    self.keys = kwargs['keys']
    self.labels = kwargs['labels']

#------------------------------------------------------------------------------
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

#------------------------------------------------------------------------------
