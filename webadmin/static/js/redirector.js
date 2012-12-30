

function add() {
    var posts = {
        protocol: $('#protocol').val(),
        local_ip: $('#local_ip').val(),
        local_port: $('#local_port').val(),
        remote_ip: $('#remote_ip').val(),
        remote_port: $('#remote_port').val()
    };
    $.post(add_url, posts, function(data) {
        if (data.ok) {
            refresh_list();
            alert('add successfully');
        } else {
            alert(data.error);
        }
    });
}

function refresh_list() {
    $.get(list_url, function(data) {
        var tbody = tag('tbody');
        $.each(data.redirectors, function(i, rd) {
            var state_btn;
            if (rd.enabled) {
                state_btn = tag('a', 'Disable').addClass(
                    'btn', 'btn-warning').attr('onclick', 'disable('+rd.id+');');
            } else {
                state_btn = tag('a', 'Enable').addClass(
                    'btn', 'btn-success').attr('onclick', 'enable('+rd.id+');');
            }
            tbody.push(tag('tr',
                tag('td', rd.protocol),
                tag('td', rd.local),
                tag('td', rd.remote),
                tag('td', rd.enabled),
                tag('td', tag('div',
                    state_btn,
                    tag('a', 'Remove').addClass('btn', 'btn-danger').attr(
                        'onclick', 'remove('+rd.id+');')
                ).addClass('btn-group'))
            ));
        });
        $('#redirectors tbody').html(tbody.html());
    });
}

function enable(rid) {
    $.post(enable_url, {rid:rid}, function(data) {
        if (data.ok) {
            refresh_list();
        } else {
            alert(data.error);
        }
    });
}

function disable(rid) {
    $.post(disable_url, {rid:rid}, function(data) {
        if (data.ok) {
            refresh_list();
        } else {
            alert(data.error);
        }
    });
}

function remove(rid) {
    $.post(remove_url, {rid:rid}, function(data) {
        if (data.ok) {
            refresh_list();
        } else {
            alert(data.error);
        }
    });
}

$(document).ready(function() {
    refresh_list();
});