from server.results import get_results, make_table
from base import paths, utils

from flask import Flask, render_template, abort, request, make_response
from wtforms import Form, DecimalField, SelectField

app = Flask("nukecon",
            template_folder=paths.TEMPLATES,
            static_folder=paths.STATIC)
app.config["APPLICATION_ROOT"] = "/nukecon/"

COMPONENTS = [
    "acp",
    "adn",
    "adp",
    "amp",
    "anp",
    "atp",
    "dgt",
    "dtp",
    "gdp",
    "gnp",
    "gtp",
    "ndp",
    "thp",
    "ttp",
    "udp",
    "ump",
    "utp",
]

class ResultsForm(Form):
    max_resolution = DecimalField('Maximal resolution', default=2.5)
    join_results = SelectField(
            'Postprocessing',
            choices=[ ('none', 'No postprocessing'),
                      ('join', 'Merge chains and make average') ],
            default='none')
    join_angle = DecimalField('Merge angle (&#176;)', default=30)


def csv_response(table):
    output = make_response(utils.table_to_csv(table))
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route("/")
def index():
    return render_template("index.html", components=COMPONENTS)

@app.route("/results/<component>", methods=("POST", "GET"))
def results(component):
    if component not in COMPONENTS:
        abort(404)
    form = ResultsForm(request.form)
    if request.method == "POST" and form.validate():
        if "Download as CSV" == request.form["submit"]:
            return csv_response(make_table(component, form))
        results = get_results(component, form)
    else:
        results = {}
    return render_template("results.html",
                           component=component,
                           components=COMPONENTS,
                           form=form,
                           has_results=bool(results),
                           **results)

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)

