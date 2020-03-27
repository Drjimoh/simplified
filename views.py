"""
Routes and views for the flask application.
"""

#import packages
from datetime import datetime
from flask import render_template, session, redirect, url_for, jsonify, request
from shoplte import app
from shoplte import custom_config
from shoplte.models import *

#database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = custom_config.database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

#fixed trending
with app.app_context():
    session_data = {}
    trendings = Products.query.filter(Products.reviews >= 10).order_by(Products.stars.desc()).limit(5).all()


#Routes
@app.route('/')
@app.route('/feeds')
def home():
    """Renders the feeds page."""
    year = datetime.now().year
    title="Feeds"

    #session condition
    if "home" not in session_data:
        session_data["home"] = Products.query.paginate(page=1, per_page=5)

    session["page"] = "home"

    #set products
    products = session_data["home"]
    for each_item in products.items:
        each_item.original = int(float(each_item.stars) * 20)
        print(each_item.original)

    #return index template
    return render_template("index.html", year=year, title=title, feeds=products, trends=trendings)


@app.route('/category/<string:cat>')
def category(cat):
    """Renders the category route."""
    year = datetime.now().year
    title = cat.replace("-", " ").capitalize()

    #get target list category
    cat_checks = title.lower()

    #session condition
    if cat not in session_data:
        session_data[cat] = Products.query.filter_by(category=cat_checks).paginate(page=1, per_page=5)

    session["page"] = cat
    print(cat)
    #set products
    products = session_data[cat]
    for each_item in products.items:
        each_item.original = int(float(each_item.stars) * 20)
        print(each_item.original)

    #return index template
    return render_template("index.html", year=year, title=title, feeds=products, trends=trendings)


@app.route('/search/<string:category>/<string:query>')
def search(category, query):
    """Renders the search complete route."""
    year = datetime.now().year
    title = f"Search result for '{query}'"

    #query in category
    cat_checks = category.lower()

    #session condition
    if f"{cat_checks}-{query}" not in session_data:
        session_data[f"{cat_checks}-{query}"] = Products.query.filter_by(category=cat_checks).filter(Products.name.ilike(f"%{query}%")).paginate(page=1, per_page=5)

    session["page"] = f"cat-search"
    session_data["query"] = [query, cat_checks]

    #set products
    products = session_data[f"{cat_checks}-{query}"]
    for each_item in products.items:
        each_item.original = int(float(each_item.stars) * 20)
        print(each_item.original)

    #return index template
    return render_template("index.html", year=year, title=title, feeds=products, trends=trendings)


@app.route('/search', methods=["GET"])
def search_query():
    """Renders the search complete route."""
    year = datetime.now().year

    #get query
    query = request.args.get("query")
    title = f"Search result for '{query}'"

    #session condition
    if query not in session_data:
        session_data[query] = Products.query.filter(Products.name.ilike(f"%{query}%")).paginate(page=1, per_page=5)
        
    session["page"] = "search"
    session_data["query"] = query

    #set products
    products = session_data[query]
    for each_item in products.items:
        each_item.original = int(float(each_item.stars) * 20)
        print(each_item.original)

    #render template
    return render_template("index.html", year=year, title=title, feeds=products, trends=trendings)


@app.route('/share/<string:sku>')
def share(sku):
    """Renders the category api."""
    year = datetime.now().year

    #get target product
    try:
        products = Products.query.filter(Products.sku == sku).all()
        for each in products:
            title = each.name
            break
    except Exception as e:
        title = "Item not found"
    
    session["page"] = None

    for each_item in products.items:
        each_item.original = int(float(each_item.stars) * 20)
        print(each_item.original)

    #render template
    return render_template("indexparse.html", year=year, title=title, feeds=products, trends=trendings)


@app.route('/favourites/<string:favlist>', methods=["GET"])
def favourites(favlist):
    """Renders the favourites template."""
    year = datetime.now().year
    title="Favourite items"

    #session condition
    if session["page"] != "favourite":
        favlist = favlist.split(",")
        favlist = favlist[1:]

        #get each sku from feeds
        products = []
        for each in favlist:
            results = Products.query.filter(Products.sku == each).all()
            if (results[0] == None):
                continue
            products.append(results[0])

        session["page"] = None

    for each_item in products:
        each_item.original = int(float(each_item.stars) * 20)
        print(each_item.original)

    #render template
    return render_template("indexparse.html", year=year, title=title, feeds=products, trends=trendings)

#route for more...
@app.route('/more', methods=["POST"])
def more():
    page = int(request.form.get("page"))

    try:
        print(page)
        print(session["page"])
    except:
        pass

    def parser(render):
        products = []
        for each in render.items:
            dict_each = {}
            dict_each["name"] = each.name
            dict_each["sku"] = each.sku
            dict_each["price"] = each.price
            dict_each["stars"] = each.stars
            dict_each["original"] = int(float(each.stars) * 20)
            dict_each["link"] = each.link
            dict_each["image_url"] = each.image_url
            dict_each["reviews"] = each.reviews
            dict_each["seller"] = each.seller
            dict_each["category"] = each.category
            dict_each["description"] = each.description
            products.append(dict_each)
        return products
    try:
        #render home json route
        if session["page"] == "home":
            render = Products.query.paginate(page=page, per_page=2)
            products = parser(render)
            return jsonify(products)

        #render category json route
        print(session["page"])
        if session["page"] in ["computing", "electronics", "fashion", "health-and-beauty", "home-and-office", "phones-and-tablets"]:
            categ = session["page"].replace("-", " ").lower()
            render = Products.query.filter_by(category=categ).paginate(page=page, per_page=2)
            products = parser(render)
            return jsonify(products)

        #render search json route
        if session["page"] == "search":
            query = session_data["query"]
            render = Products.query.filter(Products.name.ilike(f"%{query}%")).paginate(page=page, per_page=2)
            products = parser(render)
            return jsonify(products)

        #render category search json route
        if session["page"] == "cat-search":
            query = session_data["query"][0]
            cat_checks = session_data["query"][1]
            render = Products.query.filter_by(category=cat_checks).filter(Products.name.ilike(f"%{query}%")).paginate(page=page, per_page=2)
            products = parser(render)
            return jsonify(products)
    except:
        render = Products.query.paginate(page=page, per_page=2)
        products = parser(render)
        return jsonify(products)
    
    #else
    render = Products.query.paginate(page=page, per_page=2)
    products = parser(render)
    return jsonify(products)


#handle server errors
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("home"))