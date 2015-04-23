from django import forms

class Filters(forms.Form):
  experiment1 = forms.ChoiceField( label='Experiment 1', required = True )
  experiment2 = forms.ChoiceField( label='Experiment 2', required = True )
  xaxis = forms.ChoiceField( label='x-axis', required = True )
  yaxis = forms.ChoiceField( label='y-axis', required = True )
  samples = forms.ChoiceField( label='How many samples to view?', required = True )

class Single_Exp_Filters(forms.Form):
  experiment1 = forms.ChoiceField( label='Experiment 1', required = True )
  xaxis = forms.ChoiceField( label='x-axis', required = True )
  yaxis = forms.ChoiceField( label='y-axis', required = True )
  samples = forms.ChoiceField( label='How many samples to view?', required = True ) 
