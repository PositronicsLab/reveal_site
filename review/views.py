from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import mpld3
from mpld3 import plugins
import json
from .revealdb import revealdb
from .forms import Filters
from .forms import Single_Exp_Filters

def singleview(request):
  if request.method == 'POST':
    experiments = revealdb.find_experiments({})
    experiment_ids = [(e.experiment_id,e.experiment_id) for e in experiments]

    experiment_id = experiment_ids[0]
    scenario_id = experiments[0].scenario_id

    analyzers = revealdb.find_analyzers({'scenario_id': scenario_id})
    analyzer = analyzers[0]
    axes = [(a,a) for a in analyzer.keys]

    samples = []
    samples.append( (10,10) )
    samples.append( (50,50) )
    samples.append( (100,100) )
    samples.append( (500,500) )
    samples.append( (1000,1000) )
    samples.append( (2000,2000) )
    samples.append( (5000,5000) )
    samples.append( (10000,10000) )
    samples.append( (15000,15000) )

    filters = Single_Exp_Filters( request.POST )
    filters.fields['experiment1'].choices = experiment_ids
    filters.fields['xaxis'].choices = axes
    filters.fields['yaxis'].choices = axes
    filters.fields['samples'].choices = samples

    if filters.is_valid():
      experiment_id1 = filters.cleaned_data['experiment1']
      xaxis = filters.cleaned_data['xaxis']
      yaxis = filters.cleaned_data['yaxis']
      values = int( filters.cleaned_data['samples'] )

      experiment1 = revealdb.find_experiments({'experiment_id': experiment_id1})
      scenario_id = experiment1[0].scenario_id

      analyzers = revealdb.find_analyzers({'scenario_id': scenario_id})
      analysis1 = revealdb.find_analyses({'experiment_id': experiment_id1})

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

      x1 = []
      y1 = []

      for i in range(0, values-1):
        a = analysis1[i]
        d = dict(a.values[0])
        x1.append(d[analyzer.keys[x_idx]])
        y1.append(d[analyzer.keys[y_idx]])

      fig, ax = plt.subplots()

      lines = ax.plot( x1, y1, color='red' )

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
    else:
      return Http404()
  else:  # GET
    experiments = revealdb.find_experiments({})
    experiment_ids = [(e.experiment_id,e.experiment_id) for e in experiments]

    experiment_id = experiment_ids[0]
    scenario_id = experiments[0].scenario_id

    analyzers = revealdb.find_analyzers({'scenario_id': scenario_id})
    analyzer = analyzers[0]

    axes = []
    for i in range( 0, len(analyzer.keys) ):
      axes.append( (analyzer.keys[i], analyzer.labels[i]) )
    
    samples = []
    samples.append( (10,10) )
    samples.append( (50,50) )
    samples.append( (100,100) )
    samples.append( (500,500) )
    samples.append( (1000,1000) )
    samples.append( (2000,2000) )
    samples.append( (5000,5000) )
    samples.append( (10000,10000) )
    samples.append( (15000,15000) )

    filters = Single_Exp_Filters()
    filters.fields['experiment1'].choices = experiment_ids
    filters.fields['xaxis'].choices = axes
    filters.fields['yaxis'].choices = axes
    filters.fields['samples'].choices = samples

    return render(request, "review/index.html", {'form': filters })

def doubleview(request):
  if request.method == 'POST':
    experiments = revealdb.find_experiments({})
    experiment_ids = [(e.experiment_id,e.experiment_id) for e in experiments]

    experiment_id = experiment_ids[0]
    scenario_id = experiments[0].scenario_id

    analyzers = revealdb.find_analyzers({'scenario_id': scenario_id})
    analyzer = analyzers[0]
    axes = [(a,a) for a in analyzer.keys]

    samples = []
    samples.append( (10,10) )
    samples.append( (50,50) )
    samples.append( (100,100) )
    samples.append( (500,500) )
    samples.append( (1000,1000) )
    samples.append( (2000,2000) )
    samples.append( (5000,5000) )
    samples.append( (10000,10000) )
    samples.append( (15000,15000) )

    filters = Filters( request.POST )
    filters.fields['experiment1'].choices = experiment_ids
    filters.fields['experiment2'].choices = experiment_ids
    filters.fields['xaxis'].choices = axes
    filters.fields['yaxis'].choices = axes
    filters.fields['samples'].choices = samples

    if filters.is_valid():
      experiment_id1 = filters.cleaned_data['experiment1']
      experiment_id2 = filters.cleaned_data['experiment2']
      xaxis = filters.cleaned_data['xaxis']
      yaxis = filters.cleaned_data['yaxis']
      values = int( filters.cleaned_data['samples'] )

      experiment1 = revealdb.find_experiments({'experiment_id': experiment_id1})
      experiment2 = revealdb.find_experiments({'experiment_id': experiment_id2})
      scenario_id = experiment1[0].scenario_id

      analyzers = revealdb.find_analyzers({'scenario_id': scenario_id})
      analysis1 = revealdb.find_analyses({'experiment_id': experiment_id1})
      analysis2 = revealdb.find_analyses({'experiment_id': experiment_id2})

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

      x1 = []
      y1 = []
      x2 = []
      y2 = []

      for i in range(0, values-1):
        a = analysis1[i]
        d = dict(a.values[0])
        x1.append(d[analyzer.keys[x_idx]])
        y1.append(d[analyzer.keys[y_idx]])

      for i in range(0, values-1):
        a = analysis2[i]
        d = dict(a.values[0])
        x2.append(d[analyzer.keys[x_idx]])
        y2.append(d[analyzer.keys[y_idx]])

      fig, ax = plt.subplots()

      lines = ax.plot( x1, y1, color='red' )
      lines, = ax.plot( x2, y2, color='blue' )

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
    else:
      return Http404()
  else:  # GET
    experiments = revealdb.find_experiments({})
    experiment_ids = [(e.experiment_id,e.experiment_id) for e in experiments]

    experiment_id = experiment_ids[0]
    scenario_id = experiments[0].scenario_id

    analyzers = revealdb.find_analyzers({'scenario_id': scenario_id})
    analyzer = analyzers[0]

    axes = []
    for i in range( 0, len(analyzer.keys) ):
      axes.append( (analyzer.keys[i], analyzer.labels[i]) )

    samples = []
    samples.append( (10,10) )
    samples.append( (50,50) )
    samples.append( (100,100) )
    samples.append( (500,500) )
    samples.append( (1000,1000) )
    samples.append( (2000,2000) )
    samples.append( (5000,5000) )
    samples.append( (10000,10000) )
    samples.append( (15000,15000) )

    filters = Filters()
    filters.fields['experiment1'].choices = experiment_ids
    filters.fields['experiment2'].choices = experiment_ids
    filters.fields['xaxis'].choices = axes
    filters.fields['yaxis'].choices = axes
    filters.fields['samples'].choices = samples

    return render(request, "review/index.html", {'form': filters })

def index(request):
#  return singleview( request )
  return doubleview( request )
