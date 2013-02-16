/**
 * Zine Administration Tools
 * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 *
 * Part of the Zine core framework. Provides default script
 * functions for the administration interface.
 *
 * :copyright: (c) 2010 by the Zine Team, see AUTHORS for more details.
 * :license: BSD, see LICENSE for more details.
 */

$(function() {
  // fade in messages
  (function() {
    var shuttingDown = false;
    var hiddenMsg = null, left, top, right, bottom;
    var messages = $('div.message').hide().fadeIn('slow');

    function fadeInMsg() {
      hiddenMsg.css('visibility', 'visible').animate({opacity: '1.0'});
      hiddenMsg = null;
    }

    messages.mouseenter(function() {
      if (shuttingDown && !$(this).is('.message-error'))
        return;
      if (hiddenMsg)
        fadeInMsg();
      var msg = $(this);
      var pos = msg.offset();
      left = pos.left - 2, top = pos.top - 2;
      right = left + msg.width() + parseInt(msg.css('padding-left')) +
              parseInt(msg.css('padding-right')) + 4;
      bottom = top + msg.height() + parseInt(msg.css('padding-top')) +
               parseInt(msg.css('padding-bottom')) + 4;
      msg.animate({opacity: '0.01'}, 'fast', function() {
        hiddenMsg = msg;
        hiddenMsg.css('visibility', 'hidden');
      });
    });

    $(document).mousemove(function(evt) {
      if (!hiddenMsg)
        return;
      if (evt.clientX < left || evt.clientX > right ||
          evt.clientY < top || evt.clientY > bottom)
        fadeInMsg();
    });

    window.setTimeout(function() {
      msg = null;
      shuttingDown = true;
      messages.each(function() {
        if (!$(this).is('.message-error')) {
          $(this).animate({height: 'hide', opacity: 'hide'}, 'slow');
        }
      });
    }, 8000);
  })();

  // support for toggleable sections
  $('div.toggleable').each(function() {
    var
      fieldset = $(this),
      children = fieldset.children().slice(1);
    // collapse it if it should be collapsed and there are no errors in there
    if ($(this).is('.collapsed') && $('.errors', this).length == 0)
      children.hide();
    $('h3', this).click(function() {
      children.toggle();
      fieldset.toggleClass('collapsed');
    });
  });

  // Add bookmarklets to pages that want them
  (function() {
    var container = $('div.post-bookmarklets');
    if (!container.length)
      return;
    var
      bookmarkletURL = Zine.ADMIN_URL + '/_bookmarklet',
      bookmarklet = 'document.location.href="' + bookmarkletURL +
      '?mode=newpost&text="+encodeURI(getSelection?getSelection()' +
      ':document.getSelection?document.getSelection():document.' +
      'selection.createRange().text)+"&title="+encodeURI(document.' +
      'title)+"&url="+encodeURI(document.location.href)';
    container.append($('<h2>').text(_('Bookmarklet')));
    container.append($('<p>').text(
      _('Right click on the following link and choose ' +
        '“Add to favorites” or “Bookmark link” to create a ' +
        'posting shortcut.')));
    container.append($('<p>').text(
      _('Next time you visit an interesting page, just select some ' +
        'text and click on the bookmark.')));
    container.append($('<p>').append($('<a>')
      .attr('href', 'javascript:' + encodeURI(bookmarklet))
      .text(_('Blog It!'))
      .click(function() {
        alert(_('Right click on this link and choose “Add to ' +
                'favorites” or “Bookmark link” to create a ' +
                'posting shortcut.'));
        return false;
      })));
  })();

  // Tag support for the post editor.
  (function() {
    var tag_field = $("#f_tags");
    if (tag_field.length)
      Zine.callJSONService('get_taglist', {}, function(rv) {
        tag_field.autocomplete(rv.tags, {
          highlight: false,
          multiple: true,
          multipleSeparator: ", ",
          scroll: true,
          scrollHeight: 300
        });
      });
  })();

  // If we're on a new-post/edit-post page we can update the
  // page title dynamically based on the text field.
  (function() {
    var input_box = $('#post_form #f_title');
    if (input_box.length == 0)
      return;

    // windows browser put the invisible space directly into the
    // window manager title which causes a question mark to show
    // up.  Because of that we fire the change() event right away
    // to force an updated title without the invisble space.
    var title = document.title.split(/\u200B/, 2)[1];
    input_box.bind('change', function() {
      var arg = input_box.val();
      document.title = (arg ? arg + ' — ' : '') + title;
    }).change();
  })();

  // Make some textareas resizable
  (function() {
    var ta = $('textarea.resizable');
    if (ta.length == 0)
      return;

    ta.TextAreaResizer();

    // make all forms remember the height of the textarea.  This
    // code does funny things if multiple textareas are resizable
    // but it should work for most situations.
    var cookie_set = false;
    $('form').submit(function() {
      if (cookie_set)
        return;
      var height = parseInt($('form textarea.resizable').css('height'));
      if (height > 0)
        document.cookie = 'ta_height=' + height;
      cookie_set = true;
    });

    // if we have the textarea height in the cookie, update the
    // height for the textareas.
    var height_cookie = document.cookie.match(/ta_height=(\d+)/);
    var height;
    if(height_cookie)
    {
        height = height_cookie[1];
    }
    if (height != null)
      ta.css('height', height + 'px');
  })();
});
