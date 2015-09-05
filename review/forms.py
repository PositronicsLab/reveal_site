from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.formsets import formset_factory
from .revealdb import revealdb

class FormException(Exception):
  pass

class ErrorReportForm(forms.Form):
  has_messages = False
  messages = forms.CharField( widget=forms.Textarea )
  def __init__(self, *args, **kwargs):
    super(ErrorReportForm,self).__init__(*args,**kwargs)
    self.fields['messages'].widget.attrs['readonly'] = True
    self.fields['messages'].widget.attrs['rows'] = 10
    self.fields['messages'].widget.attrs['cols'] = 100
#    self.fields['messages'].initial = 'Reported errors:'
  def add(self, msg ):
    txt = ''
    if not self.has_messages:
      self.has_messages = True
      txt = msg
    else:
      txt = self.fields['messages'].initial + '\n' + msg
    self.fields['messages'].initial = txt

class ExperimentForm(forms.Form):
  #valid = True
  index = 0
  experiment = forms.ChoiceField( label='Experiment', required = True )
  color = forms.ChoiceField( label='Color', required = True )
  min_time = forms.CharField( label='Minimum Time (s):' )
  max_time = forms.CharField( label='Maximum Time (s):' )
  samples = forms.CharField( label='Samples:' )
  time_step = forms.CharField( label='Time Step (s):' )
  intermediate_trials = forms.CharField( label='Intermediate Trials Ignored:' )
  def __init__(self, *args, **kwargs):
    super(ExperimentForm,self).__init__(*args,**kwargs)
    self.fields['min_time'].widget.attrs['readonly'] = True
    self.fields['max_time'].widget.attrs['readonly'] = True
    self.fields['samples'].widget.attrs['readonly'] = True
    self.fields['time_step'].widget.attrs['readonly'] = True
    self.fields['intermediate_trials'].widget.attrs['readonly'] = True
    try:
      scenario_id = self.data['scenario']
      #print(scenario_id)
      self.load_experiments(scenario_id)
    except:
      #raise FormException('failed to load experiment for requested scenario')
      errstr = 'failed to load experiment for requested scenario'
      #print(errstr)
    #  valid = False
    self.load_colors()
  def load_colors(self):
    colors = []
    colors.append( ('blue','blue') )
    colors.append( ('green','green') )
    colors.append( ('red','red') )
    colors.append( ('cyan','cyan') )
    colors.append( ('magenta','magenta') )
    colors.append( ('yellow','yellow') )
    self.fields['color'].choices = colors
  def load_experiments(self, scenario_id):
    db = revealdb()
    results = db.find_experiments({'scenario_id':scenario_id})
    experiment_set = results['experiments']
    errors = results['errors']
    experiment_ids = [(e.experiment_id,e.experiment_id) for e in experiment_set]
    self.fields['experiment'].choices = experiment_ids
    if( len(experiment_ids) ):
      self.fields['min_time'].initial = experiment_set[0].min_time
      self.fields['max_time'].initial = experiment_set[0].max_time
      self.fields['samples'].initial = experiment_set[0].samples
      self.fields['time_step'].initial = experiment_set[0].time_step
      self.fields['intermediate_trials'].initial = experiment_set[0].intermediate_trials
    else:
      errors.append('no experiments for found for the requested scenario')
    return errors

class ScenarioMultiForm(forms.Form):
  scenario = forms.ChoiceField( label='Scenario', required = True )
  experiments = forms.ChoiceField( label='Experiments', initial = 2 )
  samples = forms.CharField( label='Samples:' )
  sample_rate = forms.CharField( label='Sample Rate (s):' )
  sample_start_time = forms.CharField( label='Sample Start Time (s):' )
  sample_end_time = forms.CharField( label='Sample End Time (s):' )
  scenario_id = None
  xaxis = forms.ChoiceField( label='x-axis', required = True )
  xaxis_lower = forms.CharField( label='Lower Bound:', required = True )
  xaxis_upper = forms.CharField( label='Upper Bound:', required = True )
  yaxis = forms.ChoiceField( label='y-axis', required = True )

  def __init__(self, scenario_id, *args, **kwargs):
    super(ScenarioMultiForm,self).__init__(*args,**kwargs)
    if( scenario_id != None ):
      self.scenario_id = scenario_id
    self.populate()
    
  def populate(self):
    db = revealdb()
    results = db.find_scenarios({})
    scenario_set = results['scenarios']
    errors = results['errors']
#    if not scenario_set:
#      return
    scenarios = [(s.scenario_id,s.description) for s in scenario_set]
#    if not scenarios:
#      return
    self.fields['scenario'].choices = scenarios
    idx = 0;

    if( self.scenario_id != None ):
      for i in range( 0, len(scenario_set) ):
        if( self.scenario_id == scenario_set[i].scenario_id ):
          idx = i
          break
    #print( "idx: " + str(idx) )
    self.scenario_id = scenario_set[idx].scenario_id
    self.fields['samples'].initial = scenario_set[idx].samples
    self.fields['sample_rate'].initial = scenario_set[idx].sample_rate
    self.fields['sample_start_time'].initial = scenario_set[idx].sample_start_time
    self.fields['sample_end_time'].initial = scenario_set[idx].sample_end_time

    self.fields['experiments'].choices = [(a,a) for a in range(1,5)] 
    analyzers = db.find_analyzers({'scenario_id': self.scenario_id})
    analyzer = analyzers[0]
    axes = []
    for i in range( 0, len(analyzer.keys) ):
      axes.append( (analyzer.keys[i], analyzer.labels[i]) )
    self.fields['xaxis'].choices = axes
    if( len(analyzer.keys) ):
      self.fields['xaxis'].initial = analyzer.keys[0]
      self.fields['xaxis_lower'].initial = scenario_set[idx].sample_start_time
      self.fields['xaxis_upper'].initial = scenario_set[idx].sample_end_time
    self.fields['yaxis'].choices = axes
    if( len(analyzer.keys) > 1 ):
      self.fields['yaxis'].initial = analyzer.keys[1]

