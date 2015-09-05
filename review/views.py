from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse, QueryDict
from django.template import RequestContext, loader
from django.template.context_processors import csrf
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from matplotlib import colors
import mpld3
from mpld3 import plugins
import json
from .revealdb import revealdb
from .forms import ScenarioMultiForm, ExperimentForm, ErrorReportForm
from django.forms.formsets import formset_factory

errors = ErrorReportForm()

def get_colors():
  colors=[]
  colors.append( 'blue' )
  colors.append( 'green' )
  colors.append( 'red' )
  colors.append( 'cyan' )
  colors.append( 'magenta' )
  colors.append( 'yellow' )
  return colors

def index(request):
  return view( request )

def view(request):
  c = {}
  c.update(csrf(request))
  db = revealdb()

  if request.method == 'POST':

    scenario_id = request.POST.get( "scenario" )

    #ExperimentFormset = formset_factory(ExperimentForm, extra=2, max_num=4)
    ExperimentFormset = formset_factory(ExperimentForm, max_num=4)
    formset = ExperimentFormset( request.POST )
    f = ScenarioMultiForm( scenario_id, request.POST )

    if not f.is_valid():
      #print( f.errors )
      raise Http404("form not valid")

    if not formset.is_valid():
      raise Http404("formset not valid")

    scenario_id = f.cleaned_data['scenario']
    experiments = f.cleaned_data['experiments']
    xaxis = f.cleaned_data['xaxis']
    yaxis = f.cleaned_data['yaxis']
    xaxis_lower = float( f.cleaned_data['xaxis_lower'] )
    xaxis_upper = float( f.cleaned_data['xaxis_upper'] )
    analyzers = db.find_analyzers({'scenario_id': scenario_id})
    analyzer = analyzers[0]
    i = 0
    x_idx = 0
    y_idx = 0
    for k in analyzer.keys:
      if k == xaxis:
        x_idx = i
      if k == yaxis:
        y_idx = i
      i  = i + 1

    fig, ax = plt.subplots()

    for xf in formset:
      exp_id = xf.cleaned_data['experiment']
      color = xf.cleaned_data['color']
      an_recs = db.find_analyses({'experiment_id': exp_id, 'values.t':{'$gte':xaxis_lower, '$lte':xaxis_upper} })
      x = []
      y = []

      for a in an_recs:
        d = dict(a.values[0])
        x.append(d[analyzer.keys[x_idx]])
        y.append(d[analyzer.keys[y_idx]])

      lines = ax.plot( x, y, color )

    plt.xlabel( analyzer.labels[x_idx] )
    plt.ylabel( analyzer.labels[y_idx] )

    #plugins.clear(fig)  # clear all plugins from the figure
    #plugins.connect(fig, plugins.Reset(), plugins.Zoom(), plugins.BoxZoom())

    fig_json = json.dumps(mpld3.fig_to_dict( fig ))
    template = loader.get_template('review/plot.html')
    context = RequestContext(request, {
        'figure': fig_json,
    })
    return HttpResponse(template.render(context))
  else:  # GET
    f = ScenarioMultiForm( None )
    ExperimentFormset = formset_factory(ExperimentForm, max_num=4)
    formset = ExperimentFormset()

    if f.scenario_id == None:
      errors.add('no scenarios exist in database')
    else:
      i = 0
      for ef in formset:
        errs = ef.load_experiments(f.scenario_id)
        ef.index = i
        i = i + 1
        for err in errs:
          errors.add( err )

    return render(request, "review/index.html", {'form':f, 'formset':formset, 'errors':errors} )

def query(request):
  c = {}
  c.update(csrf(request))
  if request.method == 'POST':
    fun = request.POST['fun']
    if( fun == 'request_scenario' ):
      return service_ajax_post_request_scenario( request )
    if( fun == 'request_experiments' ):
      return service_ajax_post_request_experiments( request )
    elif( fun == 'request_experiment_stats' ):
      return service_ajax_post_request_experiment_stats( request )

def service_ajax_post_request_scenario( request ):
  scenario_id = request.POST['scenario']
  db = revealdb()
  results = db.find_scenarios( {'scenario_id':scenario_id} )
  scenario_set = results['scenarios']
  query_errors = results['errors']
  if scenario_set:
    scenario = scenario_set[0]
    print( scenario )
    results = db.find_experiments( {'scenario_id':scenario.scenario_id} )
    experiment_set = results['experiments']
    experiment_ids = [(e.experiment_id) for e in experiment_set]
    #TODO: need to update axes information also
    # Note: the following is recreated here from forms along with other cases.
    # Target a refactor for these duplicate logic to roll into specialized class
    analyzers = db.find_analyzers({'scenario_id': scenario.scenario_id})
    analyzer = analyzers[0]
    axes = []
    for i in range( 0, len(analyzer.keys) ):
      axes.append( (analyzer.keys[i], analyzer.labels[i]) )
    min_time = scenario.sample_start_time
    max_time = scenario.sample_end_time

    axes_filters = { 'axes':axes, 'min_time':min_time, 'max_time':max_time }

#    self.fields['xaxis'].choices = axes
#    if( len(analyzer.keys) ):
#      self.fields['xaxis'].initial = analyzer.keys[0]
#      self.fields['xaxis_lower'].initial = scenario_set[0].sample_start_time
#      self.fields['xaxis_upper'].initial = scenario_set[0].sample_end_time
#    self.fields['yaxis'].choices = axes
#    if( len(analyzer.keys) > 1 ):
#      self.fields['yaxis'].initial = analyzer.keys[1]

    #lowerbound, upperbound, axes

    js = {'scenario':scenario.to_JSON(), 'experiment_ids':json.dumps(experiment_ids), 'colors':json.dumps(get_colors()), 'axes_filters':json.dumps(axes_filters )}
    return JsonResponse( js )
  else:
    return JsonResponse()

def service_ajax_post_request_experiments( request ):
  scenario = request.POST['scenario']
  experiments = request.POST['experiments']
  db = revealdb()
  results = db.find_experiments({'scenario_id':scenario})
  experiment_set = results['experiments']
  query_errors = results['errors']
  experiment_ids = [(e.experiment_id) for e in experiment_set]
  axes = []
  for i in range( 0, len(analyzer.keys) ):
    axes.append( (analyzer.keys[i], analyzer.labels[i]) )
  js = {'scenario':scenario, 'experiment_ids':json.dumps(experiment_ids), 'colors':json.dumps(get_colors()), 'axes':json.dumps(axes), }
  return JsonResponse( js )

def service_ajax_post_request_experiment_stats( request ):
  scenario_id = request.POST['scenario']
  experiment_id = request.POST['experiment_id']
  db = revealdb()
  query = {'scenario_id':scenario_id,'experiment_id':experiment_id}
  results = db.find_experiments( query )
  experiment_set = results['experiments']
  query_errors = results['errors']
  if( not len(experiment_set) ):
    return JsonResponse( {'failed'} )
  e = experiment_set[0]
  js = { 'min_time':e.min_time, 'max_time':e.max_time, 'samples':e.samples, 'time_step':e.time_step, 'intermediate_trials':e.intermediate_trials }
  return JsonResponse( js )
