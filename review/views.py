from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from .revealdb import revealdb
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import mpld3
from mpld3 import plugins
import json
from django import forms

class Filters(forms.Form):
  experiment1 = forms.ChoiceField( label='Experiment 1', required = True )
  experiment2 = forms.ChoiceField( label='Experiment 2', required = True )
  xaxis = forms.ChoiceField( label='x-axis', required = True )
  yaxis = forms.ChoiceField( label='y-axis', required = True )
  samples = forms.ChoiceField( label='How many samples to view?', required = True )

def index(request):
  if request.method == 'POST':
    experiments = revealdb.find_experiments({})
    experiment_ids = [(e.experiment_id,e.experiment_id) for e in experiments]

    experiment_id = experiment_ids[0]
    scenario_id = experiments[0].scenario_id

    analyzers = revealdb.find_analyzers({'scenario_id': scenario_id})
    analyzer = analyzers[0]
    axes = [(a,a) for a in analyzer.keys]

#    form = FilterForm( request.POST )
#    form.fields['experiment'].choices = experiment_ids
#    form.fields['xaxis'].choices = axes
#    form.fields['yaxis'].choices = axes

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
#      x1.clear;
#      y1.clear;
#      x2.clear;
#      y2.clear;
#      values = 200

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

      #fig = figure()
      fig, ax = plt.subplots()

      #line1 = ax.plot(x1,y1, color='red')
      #line2 = ax.plot(x2,y2, color='blue')
      #line1 = plt.plot(x1,y1, 'r-', x2, y2, 'b-')

      lines = ax.plot( x1, y1, color='red' )
      lines, = ax.plot( x2, y2, color='blue' )
      #plt.setp( lines, color='r')

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
      
#    if form.is_valid():
#      experiment_id = form.cleaned_data['experiment']
#      xaxis = form.cleaned_data['xaxis']
#      yaxis = form.cleaned_data['yaxis']
#  
#      experiment = Revealdb.find_experiments({'experiment_id': experiment_id})
#      scenario_id = experiment[0].scenario_id
#  
#      analyzers = Revealdb.find_analyzers({'scenario_id': scenario_id})
#      analysis = Revealdb.find_analyses({'experiment_id': experiment_id})
#  
#      analyzer = analyzers[0]
#      i = 0
#      x_idx = 0
#      y_idx = 0
#      for k in analyzer.keys:
#        if k == xaxis:
#          x_idx = i
#        if k == yaxis:
#          y_idx = i
#        i  = i + 1
#
#      x = []
#      y = []
#
#      for i in range(0, 49):
#          a = analysis[i]
#          d = dict(a.values[0])
#          x.append(d[analyzer.keys[x_idx]])
#          y.append(d[analyzer.keys[y_idx]])
#
##      for a in analysis:
##          d = dict(a.values[0])
##          x.append(d[analyzer.keys[x_idx]])
##          y.append(d[analyzer.keys[y_idx]])
#
#      fig = figure()
#  
#      pyplot.plot(x,y)
#      pyplot.xlabel( analyzer.labels[x_idx] )
#      pyplot.ylabel( analyzer.labels[y_idx] )
#  
#      fig_json = json.dumps(mpld3.fig_to_dict( fig ))
#      template = loader.get_template('visualization/analysis.html')
#      context = RequestContext(request, {
#          'figure': fig_json,
#      })
#      return HttpResponse(template.render(context))
    else:
      return Http404()
  else:  # GET
    #sessions = Revealdb.find_sessions({})
    #session_ids = [(s.session_id,s.session_id) for s in sessions]

    experiments = revealdb.find_experiments({})
    experiment_ids = [(e.experiment_id,e.experiment_id) for e in experiments]

    experiment_id = experiment_ids[0]
    scenario_id = experiments[0].scenario_id

    analyzers = revealdb.find_analyzers({'scenario_id': scenario_id})
    analyzer = analyzers[0]

    axes = []
    for i in range( 0, len(analyzer.keys) ):
      axes.append( (analyzer.keys[i], analyzer.labels[i]) )
    
#    axes = [(a,a) for a in analyzer.keys]

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


