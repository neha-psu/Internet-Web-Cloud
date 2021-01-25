from flask import render_template
from flask.views import MethodView
import gbmodel

class Index(MethodView):
    def get(self):
        model = gbmodel.get_model()
        entries = [dict(name=row[0], email=row[1], phone=row[2], address=row[3],\
                state=row[4], zip=row[5], country=row[6], amount=row[7], message=row[8] )\
                 for row in model.select()]
        return render_template('index.html',entries=entries)