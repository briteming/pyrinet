from models import *
from flask import *
import forms

get_client = lambda: current_app.get_client()

module = Blueprint('redirector', __name__)


@module.route('/list', methods=['GET'])
def list():
    return jsonify(total=Redirector.objects().count(),
        redirectors=map(lambda x: x.dump(), Redirector.objects().all()))


@module.route('/add', methods=['POST'])
def add():
    form = forms.AddForm(request.form)
    if form.validate():
        if Redirector.filter(protocol=(
                Redirector.TCP if form.protocol.data == 'tcp' else Redirector.UDP),
                local_ip=form.local_ip.data,
                local_port=form.local_port.data).count():
            return jsonify(ok=False, error='duplicated')
        rd = Redirector()
        rd.copy_form(form)
        g.db.add(rd)
        g.db.commit()
        info = rd.dump()
        get_client().redirect(protocol=info['protocol'], local=info['local'],
            remote=info['remote'])
        return jsonify(ok=True)
    return jsonify(ok=False, error='invalid form')


@module.route('/disable', methods=['POST'])
def disable():
    rid = request.form.get('rid', None)
    try:
        rd = Redirector.get(id=int(rid))
    except:
        return jsonify(ok=False, error='no such redirector')
    if rd.enabled == False:
        return jsonify(ok=True)
    rd.enabled = False
    g.db.commit()
    info = rd.dump()
    get_client().drop_redirect(protocol=info['protocol'], local=info['local'])
    return jsonify(ok=True)


@module.route('/enable', methods=['POST'])
def enable():
    rid = request.form.get('rid', None)
    try:
        rd = Redirector.get(id=int(rid))
    except:
        return jsonify(ok=False, error='no such redirector')
    if rd.enabled:
        return jsonify(ok=True)
    rd.enabled = True
    g.db.commit()
    info = rd.dump()
    get_client().redirect(protocol=info['protocol'], local=info['local'],
            remote=info['remote'])
    return jsonify(ok=True)


@module.route('/remove', methods=['POST'])
def remove():
    rid = request.form.get('rid', None)
    try:
        rd = Redirector.get(id=int(rid))
    except:
        return jsonify(ok=False, error='no such redirector')
    g.db.delete(rd)
    g.db.commit()
    if rd.enabled:
        info = rd.dump()
        get_client().drop_redirect(
            protocol=info['protocol'], local=info['local'])
    return jsonify(ok=True)
