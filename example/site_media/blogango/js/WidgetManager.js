/**
 * Widget Manager
 * ~~~~~~~~~~~~~~
 *
 * This provides the JavaScript interface to the widget manager from the
 * Zine admin panel.
 *
 * :copyright: (c) 2010 by the Zine Team, see AUTHORS for more details.
 * :license: BSD, see LICENSE for more details.
 */
(function() {
  var widget_map = {};
  var widget_positions = []; 
  var next_widget_id = 0;

  $(function() {
    $('#config-panel').hide();
    $('#sidebar').empty();
    $('#widget-form').submit(function() {
      var active_widgets = [];
      $.each(widget_positions, function() {
        active_widgets.push(widget_map[this]);
      });
      $('#active-widgets').val($.dumpJSON(active_widgets));
    });

    $('#inventory').empty();
    for (var type in $all_widgets) {
      $('<li class="widget"></li>')
        .attr('id', 'widget_' + type)
        .text($all_widgets[type])
        .appendTo('#inventory')
        .click(closure(addWidget, type, {}, true))
      };
  
    $.each($active_widgets, function() {
      addWidget(this[0], this[1], false);
    });
  });

  function closure(func) {
    var args = $.makeArray(arguments);
    return function() {
      args[0].apply(this, args.slice(1));
    }
  }

  function addWidget(widget_type, args, animate) {
    var widget_id = next_widget_id++;
    widget_positions.push(widget_id);
    widget_map[widget_id] = [widget_type, args];
    var el = $('#widget_' + widget_type)
      .clone()
      .attr('id', 'w_' + widget_id)
      .prepend($('<div class="buttons">')
        .append($('<span class="button">up</span>')
                 .click(closure(moveWidgetUp, widget_id)))
        .append($('<span class="button">down</span>')
                 .click(closure(moveWidgetDown, widget_id)))
        .append($('<span class="button">remove</span>')
                 .click(closure(removeWidget, widget_id)))
        .append($('<span class="button">configure</span>')
                 .click(closure(configureWidget, widget_id))))
    if (animate)
      el.hide().fadeIn('slow');
    el.appendTo('#sidebar');
  }

  function configureWidget(widget_id) {
    $('#config-panel div.pane').empty();
    $('#config-panel').fadeIn('slow');

    var widget = widget_map[widget_id];
    var submit_url = Zine.BLOG_URL + '/admin/options/widgets';
    var url_args = {
      configure:  widget[0],
      args:       $.dumpJSON(widget[1]),
      initial:    'yes'
    }
    $.getJSON(submit_url, url_args, updateView);

    function updateView(data) {
      if (!data.body) {
        $('#config-panel div.pane')
          .empty()
          .append($('<p>This widget is not configurable.</p>'))
          .append($('<div class="actions">')
            .append($('<input type="submit" name="cancel" value="Cancel">')
              .click(function() {
                $('#config-panel').fadeOut('slow');
                return false;
              })));
      }
      else {
        $('#config-panel div.pane').html(data.body);
        $('#config-panel div.pane form')
          .submit(function() {
            $(this).ajaxSubmit({
              url:      submit_url,
              data:     url_args,
              dataType: 'json',
              success: function(data) {
                if (data.args !== null) {
                  widget_map[widget_id][1] = data.args;
                  $('#config-panel').fadeOut('fast');
                }
                else
                  updateView(data);
              }
            });
            return false;
          })
          .append($('<div class="actions">')
            .append($('<input type="submit" value="Update Settings">'))
            .append(' ')
            .append($('<input type="submit" name="cancel" value="Cancel">')
              .click(function() {
                $('#config-panel').fadeOut('slow');
                return false;
              })));
      }
    }
  }

  function removeWidget(widget_id) {
    widget_positions.splice(widget_positions.indexOf(widget_id), 1);
    $('#w_' + widget_id).slideUp('fast', function() {
      $(this).remove();
    });
  }

  function moveWidgetUp(widget_id) {
    moveWidgetInQueue(widget_id, -1);
    var el = $('#w_' + widget_id);
    el.hide().insertBefore(el.prev()).fadeIn();
  }

  function moveWidgetDown(widget_id) {
    moveWidgetInQueue(widget_id, 1);
    var el = $('#w_' + widget_id);
    el.hide().insertAfter(el.next()).fadeIn();
  }

  function moveWidgetInQueue(widget_id, change) {
    var idx = widget_positions.indexOf(widget_id);
    widget_positions.splice(idx, 1);
    widget_positions.splice(idx + change, 0, widget_id);
  }
})();
