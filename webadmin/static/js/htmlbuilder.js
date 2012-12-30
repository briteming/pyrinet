
function html_escape (str) {
    return $('#_escape').text(str).html();
}

function SafeStr(str) {
    this.str = str;
}

SafeStr.prototype.toString = function () {
    return this.str;
};

function safeStr(str) {
    return new SafeStr(str);
}

function Tag(name, attrs) {
    this._tag = name;
    this._class = [];
    this._subs = [];

    if (attrs !== undefined) {
        this._attrs = arguments[1];
    } else {
        this._attrs = {};
    }
}


Tag.prototype.addClass = function() {
    for (var i in arguments) {
        this._class.push(arguments[i]);
    }
    return this;
};


Tag.prototype.attr = function(k, v) {
    if (v === undefined) return this._attrs[k];
    this._attrs[k] = v;
    return this;
};


Tag.prototype.push = function(child) {
    this._subs.push(child);
    return this;
};


Tag.prototype.html = function() {
    var s = '';
    this._subs.map(function (child) {
        if (child !== undefined) {
            if (typeof(child) == 'string') {
                s += html_escape(child);
            } else {
                s += child.toString();
            }
        }
    });
    return s;
};


Tag.prototype.toString = function() {
    var s = '<' + this._tag;
    for (var k in this._attrs) {
        s += ' ' + k + '="' + this._attrs[k] + '"';
    }
    if (this._class.length) {
        s += ' class="';
        this._class.map(function (cls) {
            s += cls + ' ';
        });
        s = s.substring(0, s.length-1) + '"';
    }
    s += '>';
    this._subs.map(function(child) {
        if (typeof(child) == 'string') {
            s += html_escape(child);
        } else if (child !== undefined) {
            s += child.toString();
        }
    });
    s += '<\/' + this._tag + '>';
    return s;
};


function tag(name) {
    var t = new Tag(name, {});
    for (var i = 1; i < arguments.length; i++) {
        t.push(arguments[i]);
    }
    return t;
}