from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
# We need to define our Model, which is the Python version of our SQL table.
# Every table gets a model, and we use that model to play around with its associated table from Python.

# First off, you tell the app where to find the database and initialize SQLAlchemy:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schools.sqlite3'
db = SQLAlchemy(app)
# Let SQLALchemy infer the data type of each column by looking at the existing columns, this is called reflecting
db.Model.metadata.reflect(db.engine)

'''
To create the model, we need to tell the model four things
1. It's name, here "School", because it's a list of schools
2. The table name to both find the data and to learn the columns from. That’s schools-geocoded, because TablePlus took the name right from the CSV file and did not give us any other choice.
3. A weird line about "extend_existing" which is always exactly the same
4. Even though SQLALchemy learns the columns by reflecting, it needs a unique column to be able to keep each row separate, like an id. In this case, it’s the LOC_CODE column. This is called the “primary key.”
'''
class School(db.Model):
    __tablename__ = 'schools-geocoded'
    __table_args__ = {'extend_existing': True}
    LOC_CODE = db.Column(db.Text, primary_key=True)

@app.route("/")
def index():

    # School.query.count() uses our model - School - to visit the database, build a new query, and count the number of rows in the table.
    print("Total number of schools is", School.query.count())
    # school_count = f"{School.query.count():,}"
    school_count = School.query.count()

    # Make a query to our School model to filter for a specific data point
    # What comes back from the database is that one row where LOC_CODE='X270' - we only got one because we asked for .first().
    # You can just ask for each column with a period.
    school = School.query.filter_by(LOC_CODE='X270').first()
    print("School's name is", school.SCHOOLNAME)

    # If we want to get fancier, we can also select multiple rows with .all()
    # Since we asked for .all() what comes back is similar to a list.
    # Remember that SQLALchemy is not like pandas, and you only get to use one item at a time!
    schools = School.query.all()

    # When you use print in the Flask app, it does not print to the web page. That’s the render_template part.
    # Instead, print prints to the command line. It’s totally useless for showing things to the user, but a nice cheat to check things and help us debug.
    return render_template("list.html", count=school_count, schools=schools, location="New York City")

@app.route('/city')
def city_list():
    # Get the unique city values from the database
    cities = School.query.with_entities(School.city).distinct().all()
    # They're in a weird list of one-element lists, though, like
    # [['Yonkers'],['Brooklyn'],['Manhattan']]
    # so we'll take them out of that
    cities = [city[0].title() for city in cities]
    # Now that they're both "New York," we can now dedupe and sort
    cities = sorted(list(set(cities)))
    return render_template("cities.html", cities=cities)

@app.route('/schools/<slug>')
def detail(slug):
    school = School.query.filter_by(LOC_CODE=slug).first()
    return render_template("detail.html", school=school)

@app.route('/city/<cityname>')
def city(cityname):
    cityname = cityname.replace("-", " ")
    schools = School.query.filter_by(city=cityname.upper()).all()
    return render_template("list.html", schools=schools, count=len(schools), location=cityname)

@app.route('/zip/<zipcode>')
def zip(zipcode):
    schools = School.query.filter_by(ZIP=zipcode).all()
    return render_template("list.html", schools=schools, count=len(schools), location=zipcode)

if __name__ == "__main__":

    app.run(debug=True)