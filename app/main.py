import json
import feedparser
import favicon
import time

from datetime import datetime
from time import mktime
from pathlib import Path
from urllib.parse import urlparse
from flask import Flask, jsonify, render_template, redirect, g
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

if not Path("./persistent").exists():
    exit(1)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///persistent/news_mixer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)

csrf = CSRFProtect()
csrf.init_app(app)

config = json.loads(Path("./persistent/config.json").read_text())


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512))
    date = db.Column(db.Date)
    link = db.Column(db.String(1024))
    desc = db.Column(db.String(16384))
    content = db.Column(db.String(32768))

    def __repr__(self):
        return f"News Object <id: {self.id}, title: {self.title}"


class Favicon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(128))
    url = db.Column(db.String(512))


@app.before_request
def before_request():
   g.request_start_time = time.time()
   g.request_time = lambda: "%.1fs" % (time.time() - g.request_start_time)


@app.route("/")
def index():
    return render_template("homepage.html", news=News.query.order_by(News.date.desc()).limit(20).all())


@app.route("/news/all")
def all_news():
    return render_template("homepage.html", news=News.query.order_by(News.date.desc()).all())


@app.route("/news/today")
def today_news():
    return render_template("homepage.html", news=News.query.filter_by(date=datetime.today().date()).order_by(News.date.desc()).all())


@app.route("/update/")
def refresh():
    for link in config["rss"]:
        try:
            nf = feedparser.parse(link)
        except:
            nf = []

        for res in nf.entries:
            if len(News.query.filter_by(link=res.link).all()) == 0:
                db.session.add(News(
                    title=(res.title if "title" in res else None),
                    date=(datetime.fromtimestamp(mktime(res.published_parsed)).date() if "published_parsed" in res else None),
                    link=(res.link if "link" in res else None),
                    desc=(res.summary if "summary" in res else None),
                    content=(res.content[0].value if "content" in res and isinstance(res.content, list) else None)
                ))
            else:
                News.query.filter_by(link=res.link).update({
                    News.title: (res.title if "title" in res else None),
                    News.date: (datetime.fromtimestamp(mktime(res.published_parsed)).date() if "published_parsed" in res else None),
                    News.link: (res.link if "link" in res else None),
                    News.desc: (res.summary if "summary" in res else None),
                    News.content: (res.content[0].value if "content" in res and isinstance(res.content, list) else None)
                })

    db.session.commit()

    return redirect("/")


@app.template_filter('favicon')
def get_favicon(value):
    if len(Favicon.query.filter_by(domain=urlparse(value).netloc).all()) == 0:
        print(f"Get favicon for {urlparse(value).netloc} ...")
        db.session.add(Favicon(
            domain=urlparse(value).netloc,
            url=favicon.get(f"https://{urlparse(value).netloc}/")[0].url
        ))

        db.session.commit()

    return Favicon.query.filter_by(domain=urlparse(value).netloc).all()[0].url


if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", port=8759, debug=True)

