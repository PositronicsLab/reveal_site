from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from django.template import RequestContext, loader
from django.template.context_processors import csrf
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from matplotlib import colors
import mpld3
from mpld3 import plugins
import json
from .revealdb import revealdb
from .forms import ScenarioMultiForm, ExperimentForm
from django.forms.formsets import formset_factory

def index(request):
  return view( request )

def view(request):
  c = {}
  c.update(csrf(request))
  db = revealdb()

  if request.method == 'POST':

    ExperimentFormset = formset_factory(ExperimentForm, extra=2, max_num=4)
    formset = ExperimentFormset( request.POST )
    f = ScenarioMultiForm( request.POST )

    if not f.is_valid():
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
#      ex_recs = db.find_experiments({'experiment_id': exp_id, 't':{'$gt':xaxis_lower, '$lt':xaxis_upper} })
#      an_recs = db.find_analyses({'experiment_id': exp_id, 't':{'$gt':xaxis_lower, '$lt':xaxis_upper} })
      an_recs = db.find_analyses({'experiment_id': exp_id, 'values.t':{'$gte':xaxis_lower, '$lte':xaxis_upper} })
      x = []
      y = []

#      print( values )
#      for i in range(0, values):
#        a = an_recs[i]
#        d = dict(a.values[0])
#        x.append(d[analyzer.keys[x_idx]])
#        y.append(d[analyzer.keys[y_idx]])

      for a in an_recs:
        d = dict(a.values[0])
        x.append(d[analyzer.keys[x_idx]])
        y.append(d[analyzer.keys[y_idx]])

      lines = ax.plot( x, y, color )

    plt.xlabel( analyzer.labels[x_idx] )
    plt.ylabel( analyzer.labels[y_idx] )

    plugins.clear(fig)  # clear all plugins from the figure
    #plugins.connect(fig, plugins.Reset(), plugins.BoxZoom(), plugins.Zoom())

    fig_json = json.dumps(mpld3.fig_to_dict( fig ))
    template = loader.get_template('review/plot.html')
    context = RequestContext(request, {
        'figure': fig_json,
    })
    return HttpResponse(template.render(context))
  else:  # GET
    f = ScenarioMultiForm()

    ExperimentFormset = formset_factory(ExperimentForm, extra=2, max_num=4)
    formset = ExperimentFormset()
    i = 0
    for fs in formset:
      fs.load_experiments(f.scenario_id)
      fs.index = i
      i = i + 1
 
    return render(request, "review/index.html", {'form':f, 'formset':formset })

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
  scenario = request.POST['scenario']
  db = revealdb()
  experimentset = db.find_experiments({'scenario_id':scenario})
  experiment_ids = [(e.experiment_id) for e in experimentset]
  colors=[]
  colors.append( 'blue' )
  colors.append( 'green' )
  colors.append( 'red' )
  colors.append( 'cyan' )
  colors.append( 'magenta' )
  colors.append( 'yellow' )
  js = {'scenario':scenario, 'experiment_ids':json.dumps(experiment_ids), 'colors':json.dumps(colors) }
  return JsonResponse( js )

def service_ajax_post_request_experiments( request ):
  scenario = request.POST['scenario']
  experiments = request.POST['experiments']
  db = revealdb()
  experimentset = db.find_experiments({'scenario_id':scenario})
  experiment_ids = [(e.experiment_id) for e in experimentset]
  colors=[]
  colors.append( 'blue' )
  colors.append( 'green' )
  colors.append( 'red' )
  colors.append( 'cyan' )
  colors.append( 'magenta' )
  colors.append( 'yellow' )
  axes = []
  for i in range( 0, len(analyzer.keys) ):
    axes.append( (analyzer.keys[i], analyzer.labels[i]) )
#  samples = []
#  samples.append( 15000 )
#  samples.append( 10000 )
#  samples.append( 5000 )
#  samples.append( 2000 )
#  samples.append( 1000 )
#  samples.append( 500 )
#  samples.append( 100 )
#  samples.append( 50 )
#  samples.append( 10 )
#  js = {'scenario':scenario, 'experiment_ids':json.dumps(experiment_ids), 'colors':json.dumps(colors), 'axes':json.dumps(axes), 'samples':json.dumps(samples) }
  js = {'scenario':scenario, 'experiment_ids':json.dumps(experiment_ids), 'colors':json.dumps(colors), 'axes':json.dumps(axes), }
  return JsonResponse( js )

def service_ajax_post_request_experiment_stats( request ):
  scenario_id = request.POST['scenario']
  experiment_id = request.POST['experiment_id']
  db = revealdb()
  query = {'scenario_id':scenario_id,'experiment_id':experiment_id}
  resultset = db.find_experiments( query )
  if( not len(resultset) ):
    return JsonResponse( {'failed'} )
  e = resultset[0]
  js = { 'min_time':e.min_time, 'max_time':e.max_time, 'samples':e.samples, 'time_step':e.time_step }
  return JsonResponse( js )
