// This form can be much more back-cache friendly if it is predominantly driven
// by jquery and less by the server-side.  Currently there is conflict between
// the way the framework drops in certain values, like default values.  Using
// a more jquery centric approach, most controls should actually be built here
// on document load

// using jQuery
function getCookie(name) {
  var cookieValue = null;
  if( document.cookie && document.cookie != '' ) {
    var cookies = document.cookie.split( ';' );
    for( var i = 0; i < cookies.length; i++ ) {
      var cookie = jQuery.trim( cookies[i] );
      // Does this cookie string begin with the name we want?
      if( cookie.substring( 0, name.length + 1 ) == ( name + '=' ) ) {
        cookieValue = decodeURIComponent( cookie.substring( name.length + 1 ) );
        break;
      }
    }
  }
  return cookieValue;
}
var csrftoken = getCookie( 'csrftoken' );

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  }
});

function update_scenario() {
  $.ajax({
    url : "/query/",
    type : "POST",
    dataType : "json",
    data : { 
      csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
      fun : "request_scenario",
      scenario : $('#id_scenario').val() 
    }, 

    success : function(json) {
      s = JSON.parse(json.scenario);
      scenario = s.scenario_id;
      $('#id_sample_start_time').attr('value', s.sample_start_time );
      $('#id_sample_end_time').attr('value', s.sample_end_time );
      $('#id_samples').attr('value', s.samples );
      $('#id_sample_rate').attr('value', s.sample_rate ); 
      experiment_ids = JSON.parse(json.experiment_ids);
      colors = JSON.parse(json.colors);
      axes_filters = JSON.parse(json.axes_filters);

      var experiments = parseInt($('#id_form-TOTAL_FORMS').attr('value'));
      console.log( "experiments: " + experiments );
      for( var i = 0; i < experiments; i++ ) {
        clear_options( jq_experiment_select_key(i) );
        append_options( jq_experiment_select_key(i), experiment_ids, experiment_ids );
        update_experiment_stats(i);
      }
      // TODO: update other scenario specific controls, e.g. stats and axes
      update_filters( axes_filters );

    },

    error : function(r,errmsg,err) {
      console.log(r.status + ": " + r.responseText); 
    }
  });
};

function update_experiments( newval, oldval ) {
  $.ajax({
    url : "/query/",
    type : "POST",
    dataType : "json",
    data : { 
      csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
      fun : "request_scenario",
      scenario : $('#id_scenario').val(), 
      experiments : newval
    },

    success : function(json) {
      scenario = json.scenario;
      experiment_ids = JSON.parse(json.experiment_ids);
      colors = JSON.parse(json.colors);

      update_experimentset( newval, oldval, experiment_ids, colors )
    },

    error : function(r,errmsg,err) {
      console.log(r.status + ": " + r.responseText);
    }
  });
};

function update_experimentset( newval, oldval, experiment_ids, colors ) {
  if( newval < oldval ) {
    // selection has decreased to less than the number of experiments listed 
    // so clean those controls equal to and greater than the selection
    clean_experiments( newval );
  } else if( newval > oldval ) {
    // selection has increased to greater than the number of experiments listed
    // so add new controls up to the number in selection
    add_experiments( newval, experiment_ids, colors );
  } else {
    // this handles back-cache conflict
    // - step 1 clean out any controls that may have existed where their index
    // was not equal to the default number set in set in the initial document 
    clean_experiments( newval );
    // - step 2 add back in any controls if cached selection was greater than
    // the default selection
    add_experiments( newval, experiment_ids, colors );

    // TODO: stash dummy parameters to reset the newly readded controls to the 
    // values they had when the form was submitted.
    // -and-
    // refresh the content for that control so the form is valid
  }
  // update the formset hidden attributes
  $('#id_form-TOTAL_FORMS').attr('value', newval );
}

function update_filters( axes_filters ) {

  min_time = axes_filters['min_time'];
  max_time = axes_filters['max_time'];
  axes = axes_filters['axes'];

  console.log( "min_time: " + min_time );
  console.log( "max_time: " + max_time );
  //console.log( "axes: " + axes + " length:" + axes.length );

  keys = [];
  values = [];
  for( var i = 0; i < axes.length; i++ ) {
    keys.push( axes[i][0] );
    values.push( axes[i][1] );
  }
  console.log( "keys: " + keys );
  console.log( "values: " + values );

  clear_options( '#id_xaxis' );
  clear_options( '#id_yaxis' );
  append_options( '#id_xaxis', keys, values, 0 );
  append_options( '#id_yaxis', keys, values, 1 );

  $('#id_xaxis_lower').attr('value', min_time );
  $('#id_xaxis_upper').attr('value', max_time );

}

function remove_experiment( idx ) {
  // removes the specified experiment by jquery selector
  $(jq_experiment_div_key( idx )).remove();
}

function clean_experiments( idx ) {
  // iterate over the set of selections beginning at the specified index and 
  // remove all divs if they exist
  var count = $('#id_form-MAX_NUM_FORMS').attr('value');
  for( var i = idx; i < count; i++ ) 
    if( $(jq_experiment_div_key( i )).length )
      $(jq_experiment_div_key( i )).remove();
}

function add_experiments( idx, experiment_ids, colors ) {
  // iterate over all selections and add if the selection does not exist
  for( var i = 0; i < idx; i++ ) 
    if( !$(jq_experiment_div_key( i )).length ) 
      add_experiment( i, experiment_ids, colors );
}

function selector_html( key, name, label ) {
  var html = "";
  html += '<th><label for="' + key + '">' + label + ':</label></th>';
  html += '<td><select id="' + key + '" name="' + name + '"></select></td>';
  return html;
}

function readonlytextfield_html( key, name, label ) {
  var html = "";
  html += '<th><label for="' + key + '">' + label + ':</label></th>';
  html += '<td><input id="' + key + '" name="' + name + '" type="text" readonly /></td>'
  return html;
}

function add_experiment( idx, experiment_ids, colors ) {
  var html, key;
  html = '<div id='+html_experiment_div_key(idx)+'>';
  html += '<hr>';
  html += '<p>';
  html += '<tr>';
  html += selector_html( html_experiment_select_key(idx), html_experiment_select_name(idx), "Experiment" );
  html += '</tr>';
  html += '<tr>';
  html += selector_html( html_experiment_color_key(idx), html_experiment_color_name(idx), "Color" );
  html += '</tr>';
  html += '</p>';
  html += '<p>';
  html += '<tr>';
  html += readonlytextfield_html( html_experiment_mintime_key(idx), html_experiment_mintime_name(idx), "Minimum Time (s)" );
  html += readonlytextfield_html( html_experiment_maxtime_key(idx), html_experiment_maxtime_name(idx), "Maximum Time (s)" );
  html += '</tr>';
  html += '</p>';
  html += '<p>';
  html += '<tr>';
  html += readonlytextfield_html( html_experiment_samples_key(idx), html_experiment_samples_name(idx), "Samples" );
  html += readonlytextfield_html( html_experiment_timestep_key(idx), html_experiment_timestep_name(idx), "Time Step (s)" );
  html += '</tr>';
  html += '</p>';
  html += '<p>';
  html += '<tr>';
  html += readonlytextfield_html( html_experiment_intermediatetrials_key(idx), html_experiment_intermediatetrials_name(idx), "Intermediate Trials Ignored" );
  html += '</tr>';
  html += '</p>';
  html += '</div>';
  $('#experimentset').append( html );

  append_options( jq_experiment_select_key( idx ), experiment_ids, experiment_ids );
  append_options( jq_experiment_color_key( idx ), colors, colors );

  // dynamically add a new event handler
  $(jq_experiment_select_key(idx)).on( "change", function(){
      event.preventDefault();
      update_experiment_stats( idx );
  });
};

function append_options( jq_key, keys, text, selected ) {
  //console.log(keys);
  for( var i = 0; i < keys.length; i++) {
    html = '<option value="'+keys[i]+'"';
    if( i == selected ) {
      html += ' selected="selected"';
    }
    html += '>'+text[i]+'</option>';
    $(jq_key).append(html);
  }
};

function clear_options( jq_key ) {
  $(jq_key)
           .find('option')
           .remove()
           .end()
  ;
};

function update_experiment_stats( idx ) {
  console.log( "update_experiment_stats called for idx:" + idx );
  var key = jq_experiment_select_key( idx );
  $.ajax({
    url : "/query/",
    type : "POST",
    dataType : "json",
    data : { 
      csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
      fun : "request_experiment_stats",
      scenario : $('#id_scenario').val(), 
      experiment_id : $(key).val()
    }, 

    success : function(json) {
      min_time = json.min_time;
      max_time = json.max_time;
      samples = json.samples;
      time_step = json.time_step;
      intermediate_trials = json.intermediate_trials;

      $( jq_experiment_mintime_key(idx) ).val(min_time);
      $( jq_experiment_maxtime_key(idx) ).val(max_time);
      $( jq_experiment_samples_key(idx) ).val(samples);
      $( jq_experiment_timestep_key(idx) ).val(time_step);
      $( jq_experiment_intermediatetrials_key(idx) ).val(intermediate_trials);
    },

    error : function(r,errmsg,err) {
      console.log(r.status + ": " + r.responseText);
    }
  });
};

function html_experiment_div_key( idx ) {
  return "experiment-"+idx;
}
function jq_experiment_div_key( idx ) {
  return "#" + html_experiment_div_key(idx);
}

function html_experiment_select_name( idx ) {
  return "form-"+idx+"-experiment";
}
function html_experiment_select_key( idx ) {
  return "id_"+html_experiment_select_name(idx);
}
function jq_experiment_select_key( idx ) {
  return "#" + html_experiment_select_key(idx);
}

function html_experiment_color_name( idx ) {
  return "form-"+idx+"-color";
}
function html_experiment_color_key( idx ) {
  return "id_"+html_experiment_color_name(idx);
}
function jq_experiment_color_key( idx ) {
  return "#" + html_experiment_color_key(idx);
}

function html_experiment_mintime_name( idx ) {
  return "form-"+idx+"-min_time";
}
function html_experiment_mintime_key( idx ) {
  return "id_"+html_experiment_mintime_name(idx);
}
function jq_experiment_mintime_key( idx ) {
  return "#" + html_experiment_mintime_key(idx);
}

function html_experiment_maxtime_name( idx ) {
  return "form-"+idx+"-max_time";
}
function html_experiment_maxtime_key( idx ) {
  return "id_"+html_experiment_maxtime_name(idx);
}
function jq_experiment_maxtime_key( idx ) {
  return "#" + html_experiment_maxtime_key(idx);
}

function html_experiment_samples_name( idx ) {
  return "form-"+idx+"-samples";
}
function html_experiment_samples_key( idx ) {
  return "id_"+html_experiment_samples_name(idx);
}
function jq_experiment_samples_key( idx ) {
  return "#" + html_experiment_samples_key(idx);
}

function html_experiment_timestep_name( idx ) {
  return "form-"+idx+"-time_step";
}
function html_experiment_timestep_key( idx ) {
  return "id_"+html_experiment_timestep_name(idx);
}
function jq_experiment_timestep_key( idx ) {
  return "#" + html_experiment_timestep_key(idx);
}

function html_experiment_intermediatetrials_name( idx ) {
  return "form-"+idx+"-intermediate_trials";
}
function html_experiment_intermediatetrials_key( idx ) {
  return "id_"+html_experiment_intermediatetrials_name(idx);
}
function jq_experiment_intermediatetrials_key( idx ) {
  return "#" + html_experiment_intermediatetrials_key(idx);
}

$(function(){
  $("#id_scenario").change(function(event){
    event.preventDefault();
    update_scenario();
  });
});

$(function(){
  $("#id_experiments").change(function(event){
    event.preventDefault();
    var newval = parseInt($('#id_experiments').val());
    var oldval = parseInt($('#id_form-TOTAL_FORMS').attr('value'));
    update_experiments( newval, oldval );
  });
});

// event handlers for default configuration
$(function(){
  $("#id_form-0-experiment").change(function(event){
    event.preventDefault();
    var idx = 0;
    update_experiment_stats( idx );
  });
});

$(function(){
  $("#id_form-1-experiment").change(function(event){
    event.preventDefault();
    var idx = 1;
    update_experiment_stats( idx );
  });
});

$(function(){
  $( document ).ready( function( ) {

    var oldval = parseInt($('#id_experiments').val());
    var newval = parseInt($('#id_form-TOTAL_FORMS').attr('value'));

    update_experiments( newval, oldval );

    $('#id_experiments option[value='+newval+']').prop('selected', true );
  });
});
