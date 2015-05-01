from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.formsets import formset_factory
from .revealdb import revealdb

class ExperimentForm(forms.Form):
  index = 0
  experiment = forms.ChoiceField( label='Experiment', required = True )
  color = forms.ChoiceField( label='Color', required = True )
  min_time = forms.CharField( label='Minimum Time (s):' )
  max_time = forms.CharField( label='Maximum Time (s):' )
  samples = forms.CharField( label='Samples:' )
  def __init__(self, *args, **kwargs):
    super(ExperimentForm,self).__init__(*args,**kwargs)
    self.fields['min_time'].widget.attrs['readonly'] = True
    self.fields['max_time'].widget.attrs['readonly'] = True
    self.fields['samples'].widget.attrs['readonly'] = True
    try:
      scenario_id = self.data['scenario']
      print(scenario_id)
      self.load_experiments(scenario_id)
    except:
      print('a')
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
    experimentset = revealdb.find_experiments({'scenario_id':scenario_id})
    experiment_ids = [(e.experiment_id,e.experiment_id) for e in experimentset]
    self.fields['experiment'].choices = experiment_ids
    self.fields['min_time'].initial = experimentset[0].min_time
    self.fields['max_time'].initial = experimentset[0].max_time
    self.fields['samples'].initial = experimentset[0].samples

class ScenarioMultiForm(forms.Form):
  scenario = forms.ChoiceField( label='Scenario', required = True )
  experiments = forms.ChoiceField( label='Experiments', initial = 2 )
  scenario_id = None
  xaxis = forms.ChoiceField( label='x-axis', required = True )
  yaxis = forms.ChoiceField( label='y-axis', required = True )
  samples = forms.ChoiceField( label='How many samples to view?', required = True )

  def __init__(self, *args, **kwargs):
    super(ScenarioMultiForm,self).__init__(*args,**kwargs)
    self.populate()
  def populate(self):
    scenario_set = revealdb.find_scenarios({})
    scenarios = [(s.scenario_id,s.description) for s in scenario_set]
    self.fields['scenario'].choices = scenarios
    self.scenario_id = scenario_set[0].scenario_id
    self.fields['experiments'].choices = [(a,a) for a in range(1,5)] 
    analyzers = revealdb.find_analyzers({'scenario_id': self.scenario_id})
    analyzer = analyzers[0]
    axes = []
    for i in range( 0, len(analyzer.keys) ):
      axes.append( (analyzer.keys[i], analyzer.labels[i]) )
    self.fields['xaxis'].choices = axes
    if( len(analyzer.keys) ):
      self.fields['xaxis'].initial = analyzer.keys[0]
    self.fields['yaxis'].choices = axes
    if( len(analyzer.keys) > 1 ):
      self.fields['yaxis'].initial = analyzer.keys[1]

    maxsamples = revealdb.count_trials({'scenario_id':self.scenario_id}) #?? filter
    samples = []
    samples.append( (15000,15000) )
    samples.append( (10000,10000) )
    samples.append( (5000,5000) )
    samples.append( (2000,2000) )
    samples.append( (1000,1000) )
    samples.append( (500,500) )
    samples.append( (100,100) )
    samples.append( (50,50) )
    samples.append( (10,10) )
    self.fields['samples'].choices = samples

