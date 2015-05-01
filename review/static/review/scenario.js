// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

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
            scenario = json.scenario;
            experiment_ids = JSON.parse(json.experiment_ids);
            colors = JSON.parse(json.colors);
            axes = JSON.parse(json.axes);
            samples = JSON.parse(json.samples);

            var experiments = parseInt($('#id_form-TOTAL_FORMS').attr('value'));
            for( var i = 0; i < experiments; i++ ) {
              clear_options( jq_experiment_select_key(i) );
              append_options( jq_experiment_select_key(i), experiment_ids, experiment_ids );
              update_experiment_stats(i); // not sure this async call will work as expected, but should
              // updating colors isn't really necessary
            }
            // TODO: update axes
            // TODO: update samples
        },

        error : function(r,errmsg,err) {
            console.log(r.status + ": " + r.responseText); 
        }
    });
};

function update_experiments() {
    $.ajax({
        url : "/query/",
        type : "POST",
        dataType : "json",
        data : { 
                 csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
                 fun : "request_scenario",
                 scenario : $('#id_scenario').val(), 
                 experiments : $('#id_experiments').val()
        },

        success : function(json) {
            scenario = json.scenario;
            experiment_ids = JSON.parse(json.experiment_ids);
            colors = JSON.parse(json.colors);

            var newval = parseInt($('#id_experiments').val());
            var oldval = parseInt($('#id_form-TOTAL_FORMS').attr('value'));

            console.log( newval )
            console.log( oldval )
            if( newval < oldval ) {
              for( var i = 0; i < oldval-newval; i++ ) {
                remove_experiment(oldval-1-i);
              }
            } else if( newval > oldval ) {
              for( var i = 0; i < newval-oldval; i++ ) {
                add_experiment(oldval+i, experiment_ids, colors);
              }
            }
            $('#id_form-TOTAL_FORMS').attr('value', newval );
        },

        error : function(r,errmsg,err) {
            console.log(r.status + ": " + r.responseText);
        }
    });
};

function remove_experiment( idx ) {
  $(jq_experiment_div_key( idx )).remove();
}

function add_experiment( idx, experiment_ids, colors ) {
  var html, key;
  html = '<div id='+html_experiment_div_key(idx)+'>';
  html += '<p>';
  html += '<tr>';
  html += '<th><label for="'+html_experiment_select_key(idx)+'">Experiment:</label></th>';
  html += '<td><select id="'+html_experiment_select_key(idx)+'" name="'+html_experiment_select_name(idx)+'"></select></td>';
  html += '</tr>';
  html += '<tr>';
  html += '<th><label for="'+html_experiment_color_key(idx)+'">Color:</label></th>';
  html += '<td><select id="'+html_experiment_color_key(idx)+'" name="'+html_experiment_color_name(idx)+'"></select></td>';
  html += '</tr>';
  html += '</p>';
  html += '<p>';
  html += '<tr>';
  html += '<th><label for="'+html_experiment_mintime_key(idx)+'">Minimum Time (s):</label></th>';
  html += '<td><input id="'+html_experiment_mintime_key(idx)+'" name="'+html_experiment_mintime_name(idx)+'" type="text" value="0.002" readonly /></td>'
  html += '<th><label for="'+html_experiment_maxtime_key(idx)+'">Maximum Time (s):</label></th>';
  html += '<td><input id="'+html_experiment_maxtime_key(idx)+'" name="'+html_experiment_maxtime_name(idx)+'" type="text" value="16.001" readonly /></td>'
  html += '<th><label for="'+html_experiment_samples_key(idx)+'">Samples:</label></th>';
  html += '<td><input id="'+html_experiment_samples_key(idx)+'" name="'+html_experiment_samples_name(idx)+'" type="text" value="16000" readonly /></td>'
  html += '</tr>';
  html += '</p>';
  html += '</div>';
  $('#experimentset').append( html );

  append_options( jq_experiment_select_key( idx ), experiment_ids, experiment_ids );
  append_options( jq_experiment_color_key( idx ), colors, colors );
};

function append_options( jq_key, keys, text ) {
  for( var i = 0; i < keys.length; i++) {
      html = '<option value="'+keys[i]+'">'+text[i]+'</option>';
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

            $( jq_experiment_mintime_key(idx) ).val(min_time);
            $( jq_experiment_maxtime_key(idx) ).val(max_time);
            $( jq_experiment_samples_key(idx) ).val(samples);
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

$(function(){
  $("#id_scenario").change(function(event){
    event.preventDefault();
    update_scenario();
  });
});

$(function(){
  $("#id_experiments").change(function(event){
    event.preventDefault();
    update_experiments();
  });
});

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
  $("#id_form-2-experiment").change(function(event){
    event.preventDefault();
    var idx = 2;
    update_experiment_stats( idx );
  });
});

$(function(){
  $("#id_form-3-experiment").change(function(event){
    event.preventDefault();
    var idx = 3;
    update_experiment_stats( idx );
  });
});

