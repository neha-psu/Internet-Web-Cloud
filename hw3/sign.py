from flask import redirect, request, url_for, render_template
from flask.views import MethodView
import gbmodel

class Sign(MethodView):
    def get(self):
        return render_template('sign.html')

    def post(self):
        """
        Accepts POST requests, and processes the form;
        Redirect to index when completed.
        """
        model = gbmodel.get_model()
        model.insert(request.form['name'], request.form['email'],\
            request.form['phone'],request.form['address'],request.form['state'],\
            request.form['zip'], request.form['country'], request.form['amount'], request.form['message'])
        return redirect(url_for('index'))
