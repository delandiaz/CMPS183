# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################
import urllib2
import json
from math import radians, sin, cos, sqrt, asin
from gluon.tools import geocode

@request.restful()
def api():
    API_BASE = "http://opentable.herokuapp.com"
    '''API restaurant parameters
    'id'
    'name'
    'address'
    'city'
    'state'
    'area'
    'country'
    'phone'
    'reserve_url'
    'mobile_reserve_url'
    '''
    def GET(*args,**vars):
        patterns = 'auto'
        parser = db.parse_as_rest(patterns,args,vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status,parser.error)
    def POST(*args,**vars):
        return dict()
    def PUT(*args,**vars):
        return dict()
    def DELETE(*args,**vars):
        return dict()
    return locals()



def index():
    user_latitude = request.vars.user_latitude
    user_longitude = request.vars.user_longitude
    position_received = 'n'
    if user_latitude is not None and user_longitude is not None:
        position_received = 'y'
    restaurants = db().select(db.restaurant.ALL)
    posts = []
    earth_radius = 6372.8 # Earth radius in kilometers
    
    if (position_received == 'y'):
        for r in restaurants:
            #Haversine function to get distance in kilometers from two gps coordinates
            dLat = radians(float(r['latitude']) - float(user_latitude))
            dLon = radians(float(r['longitude']) - float(user_longitude))
            lat1 = radians(float(user_latitude))
            lat2 = radians(float(r['latitude']))

            a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2                                                        
            c = 2*asin(sqrt(a))                                            
            distance_km = earth_radius * c
            print distance_km
            if (distance_km < 3.5):
                posts.append(r)
    
    #i = 0
    #Display the first 8 restaurants in database
    #while (i < 8):
    #    posts.append(restaurants[i])
    #    i += 1

    return dict(posts=posts, position_received=position_received, user_latitude=user_latitude, user_longitude=user_longitude)

def create():
    #Code below removes everything from database
    #db(db.restaurant).delete()
    #redirect(URL('default', 'index'))

    #Code used to enter all restaurants from OpenTable api into our database        
    url = "http://opentable.herokuapp.com/api/restaurants?city=Santa%20Cruz"
    json_obj = urllib2.urlopen(url)
    data = json.load(json_obj)
    total_entries = data['total_entries']
    current_page = 1
    
    while (total_entries > 0):
        url = "http://opentable.herokuapp.com/api/restaurants?city=Santa%20Cruz&per_page=100&page=" + str(current_page)
        json_obj = urllib2.urlopen(url)
        data = json.load(json_obj)
        
        for r in data['restaurants']:
            #access latitude and longitude by geocoding the restaurant address
            addy = str(r['address']) + ', ' + str(r['city']) + ', ' + str(r['state']) + ', ' + str(r['country'])
            area = (latitude, longitude) = geocode(addy)
            
            db.restaurant.insert(id = r['id'],
                             name = r['name'],
                             city = r['city'],
                             state_ = r['state'],
                             phone = r['phone'],
                             zipcode = r['postal_code'],
                             address = r['address'],
                             latitude = area[0],
                             longitude = area[1]
                                 )
        total_entries -= 100
        current_page += 1
        
    redirect(URL('default', 'index'))
    '''
    form=SQLFORM(db.restaurant, button=[])
    if form.process().accepted:
        session.flash = T('Added')
        redirect(URL('default', 'index'))
    '''
        
    return dict(form=form)

def view():
    """View a post"""    
    p = db.restaurant(request.args(0)) or redirect(URL('default', 'index'))
    form2 = SQLFORM(db.restaurant, record=p, readonly=True)
    restaurant_name = p['name']
    restaurant_city = p['city']
    restaurant_state = p['state_']
    restaurant_zip = p['zipcode']
    restaurant_address = p['address']
    restaurant_hours = p['hours']
    restaurant_phone = p['phone']
    restaurant_id = p['id']
    latitude = p['latitude']
    longitude = p['longitude']
    
    '''
    form=SQLFORM.factory(Field('search'), _class='form-search')
    form.custom.widget.search['_class'] = 'input-long search-query'
    form.custom.submit['_value'] = 'Search'
    form.custom.submit['_class'] = 'btn'
    if form.accepts(request):
        address=form.vars.search
        (latitude, longitude) = geocode(address)
    else:
        '''
        
    return dict(form2=form2, latitude=latitude, longitude=longitude, restaurant_name=restaurant_name, restaurant_id=restaurant_id, restaurant_city=restaurant_city, restaurant_state=restaurant_state, restaurant_zip=restaurant_zip, restaurant_address=restaurant_address, restaurant_hours=restaurant_hours, restaurant_phone=restaurant_phone )

def edit():
    """Edit a post"""
    p = db.restaurant(request.args(0)) or redirect(URL('default', 'index'))

    form = SQLFORM(db.restaurant, record=p)
    if form.process().accepted:
        session.flash = T('Updated')
        redirect(URL('default', 'view', args=[p.id]))
    # p.name would contain the name of the poster.
    return dict(form=form)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def test():

    posts = db().select(db.restaurant.ALL)

    return dict(posts=posts)

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
