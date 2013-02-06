/**
 * JSON Support
 * ~~~~~~~~~~~~
 *
 * Add JSON support for jQuery.
 *
 * :copyright: (c) 2010 by the Zine Team, see AUTHORS for more details.
 * :license: BSD, see LICENSE for more details.
 */

(function($) {
  function escapeString(s) {
    return '"' + (s.replace(/\\/g, '\\\\').
                    replace(/\r?\n/g, '\\n').
                    replace(/"/g, '\\"')) + '"';
  }

  /**
   * load an object from JSON
   */
  $.loadJSON = function(string) {
    return eval('(' + string + ')');
  }

  /**
   * Dump an object to JSON
   */
  $.dumpJSON = function(obj) {
    return (function dump(obj, key) {
      if (key)
        return escapeString(obj + '');
      else if (typeof obj === 'number')
        return obj.toString();
      else if (typeof obj === 'boolean')
        return obj ? 'true' : 'false';
      else if (typeof obj === 'string')
        return escapeString(obj);
      else if (obj === null)
        return 'null';
      else if (obj instanceof Array) {
        var result = [];
        for (var i = 0, n = obj.length; i != n; i++) {
          result.push(dump(obj[i], false));
        };
        return '[' + result.join(', ') + ']';
      }
      else {
        var result = [];
        for (var key in obj) {
          result.push(dump(key, true) + ': ' + dump(obj[key], false));
        }
        return '{' + result.join(', ') + '}';
      }
    })(obj, false);
  }
})(jQuery);
