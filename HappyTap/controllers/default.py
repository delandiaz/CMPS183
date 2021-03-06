# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import urllib2
import json
import datetime
from math import radians, sin, cos, sqrt, asin
from gluon.tools import geocode

def index():
    #Get the Current time and what day of the week it is.
    #These will be used to compare against restaurant's happy hour times
    #to see if any are occurring now.
    time_now = datetime.datetime.now()
    day_today = time_now.weekday()
    time_now = time_now.time()
    
    user_latitude = request.vars.user_latitude
    user_longitude = request.vars.user_longitude
    position_received = 'n'
    if user_latitude is not None and user_longitude is not None:
        position_received = 'y'
    restaurants = db().select(db.restaurant.ALL)
    restaurants_near_user = []
    posts = []
    earth_radius = 6372.8 # Earth radius in kilometers
    
    if (position_received == 'y'):
        #User's latitude and longitude were successfully retrieved. 
        #Now we can search our database for restaurants nearby their location
        for r in restaurants:
            #A check to make sure the restaurant has a documented latitude and longitude to work from.
            #If not, we attempt to update them.
            if (r['latitude'] is None and r['longitude'] is None): 
                address = str(r['address']) + ' ' + str(r['city']) + ' ' + str(r['state_']) + ' ' + str(r['zipcode']) + ' USA' 
                area = (latitude, longitude) = geocode(address) 
                r['latitude'] = area[0] 
                r['longitude'] = area[1]
                db(db.restaurant.id == r['id']).update(latitude = area[0], longitude = area[1])
                
            #Haversine function to get distance in kilometers from two gps coordinates
            dLat = radians(float(r['latitude']) - float(user_latitude))
            dLon = radians(float(r['longitude']) - float(user_longitude))
            lat1 = radians(float(user_latitude))
            lat2 = radians(float(r['latitude']))

            a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2                                                        
            c = 2*asin(sqrt(a))                                            
            distance_km = earth_radius * c
            
            #If the user is within a 4km radius of any restaurant, we append the restaurant to our
            #list of restaurants that will be displayed on the home page.
            if (distance_km < 4):              
                HH = db(db.happy_hours.id == r['id']).select().first()
                
                #If happy hours exist for the current restaurant, check to see if their happy hours are occurring now.
                if (HH is not None):
                    if day_today == 0:
                        if HH['monday_start_time'] is not None and HH['monday_end_time'] is not None:                            
                            if HH['monday_start_time'] < time_now and HH['monday_end_time'] > time_now:
                                r['has_happy_hours'] = True
                    elif day_today == 1:
                        if HH['tuesday_start_time'] is not None and HH['tuesday_end_time'] is not None:
                            if HH['tuesday_start_time'] < time_now and HH['tuesday_end_time'] > time_now:
                                r['has_happy_hours'] = True
                    elif day_today == 2:
                        if HH['wednesday_start_time'] is not None and HH['wednesday_end_time'] is not None:
                            if HH['wednesday_start_time'] < time_now and HH['wednesday_end_time'] > time_now:
                                r['has_happy_hours'] = True
                    elif day_today == 3:
                        if HH['thursday_start_time'] is not None and HH['thursday_end_time'] is not None:
                            if HH['thursday_start_time'] < time_now and HH['thursday_end_time'] > time_now:
                                r['has_happy_hours'] = True
                    elif day_today == 4:
                        if HH['friday_start_time'] is not None and HH['friday_end_time'] is not None:
                            if HH['friday_start_time'] < time_now and HH['friday_end_time'] > time_now:
                                r['has_happy_hours'] = True
                    elif day_today == 5:
                        if HH['saturday_start_time'] is not None and HH['saturday_end_time'] is not None:
                            if HH['saturday_start_time'] < time_now and HH['saturday_end_time'] > time_now:
                                r['has_happy_hours'] = True
                    elif day_today == 6:
                        if HH['sunday_start_time'] is not None and HH['sunday_end_time'] is not None:
                            if HH['sunday_start_time'] < time_now and HH['sunday_end_time'] > time_now:
                                r['has_happy_hours'] = True
                    if r['has_happy_hours'] is None:
                        r['has_happy_hours'] = False
                    restaurants_near_user.append(r)        
                else:
                    if r['has_happy_hours'] is None:
                        r['has_happy_hours'] = False
                    restaurants_near_user.append(r)
                
    #go through restaurants near user and place the ones that have happy hours occurring at the front of the list
    temp = []
    for r in restaurants_near_user:
        if r['has_happy_hours'] == True:
            temp.append(r)
    for r in restaurants_near_user:
        if r['has_happy_hours'] == False:
             temp.append(r)
                
    #Display the first 8 restaurants in database   
    num_restaurants = len(temp)
    i = 0   
    while (i < 8):
        if (i == num_restaurants):
            break
        posts.append(temp[i])
        i += 1
    
    q=db.restaurant #sql Query
    
    def generate_view_button(row):
            b = A('View', _class='btn', _href=URL('default', 'view', args=[row.id]))
            return b
    
    links = [
            dict(header='', body = generate_view_button),
            ]
    
    #create SQLFORM Grid listing all restaurants and relavent attributes
    start_idx=1
    form = SQLFORM.grid(q, args=request.args[:start_idx],
                        fields=[db.restaurant.name,
                                db.restaurant.city,
                                db.restaurant.state_,
                                db.restaurant.phone,
                                db.restaurant.address,],
            editable=False,
            deletable=False,
            paginate=6,
            csv=False,
            user_signature=False, 
            links=links,
            details=False,
    )

    return dict(posts=posts, position_received=position_received, user_latitude=user_latitude, user_longitude=user_longitude, form=form)

def create():
    #Code used to enter all restaurants in Santa Cruz from OpenTable api into our database        
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
    return dict(form=form)

def view():
    """View a post""" 
    p = db.restaurant(request.args(0)) or redirect(URL('default', 'index'))

    button_text = '' #Will either be "Add Happy Hours" or "Revise Happy Hours"
    MST = MET = MSPEC = TUST = TUET = TUSPEC = WST = WET = WSPEC = THST = THET = THSPEC = FST = FET = FSPEC = SAST = SAET = SASPEC = SUST = SUET = SUSPEC = None
    HH = db.happy_hours(request.args(0))
    #If happy hours exist for this restaurant, get it's data as a strings to display in our view
    if HH is not None:
        button_text = 'Revise Happy Hours'
        MST = str(HH['monday_start_time'])
        MET = str(HH['monday_end_time'])
        MSPEC = HH['monday_specials']
        TUST = str(HH['tuesday_start_time'])
        TUET = str(HH['tuesday_end_time'])
        TUSPEC = HH['tuesday_specials']
        WST = str(HH['wednesday_start_time'])
        WET = str(HH['wednesday_end_time'])
        WSPEC = HH['wednesday_specials']
        THST = str(HH['thursday_start_time'])
        THET = str(HH['thursday_end_time'])
        THSPEC = HH['thursday_specials']
        FST = str(HH['friday_start_time'])
        FET = str(HH['friday_end_time'])
        FSPEC = HH['friday_specials']
        SAST = str(HH['saturday_start_time'])
        SAET = str(HH['saturday_end_time'])
        SASPEC = HH['saturday_specials']
        SUST = str(HH['sunday_start_time'])
        SUET = str(HH['sunday_end_time'])
        SUSPEC = HH['sunday_specials']

    else:
        button_text = 'Enter Happy Hours'
        
    #More data to be passed to view     
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
    
    return dict(latitude=latitude, longitude=longitude, restaurant_name=restaurant_name, restaurant_id=restaurant_id, restaurant_city=restaurant_city, restaurant_state=restaurant_state, restaurant_zip=restaurant_zip, restaurant_address=restaurant_address, restaurant_hours=restaurant_hours, restaurant_phone=restaurant_phone,MST=MST, MET=MET, MSPEC=MSPEC, TUST=TUST, TUET=TUET, TUSPEC=TUSPEC, WST=WST, WET=WET, WSPEC=WSPEC, THST=THST, THET=THET, THSPEC=THSPEC, FST=FST, FET=FET, FSPEC=FSPEC, SAST=SAST, SAET=SAET, SASPEC=SASPEC, SUST=SUST, SUET=SUET, SUSPEC=SUSPEC, button_text=button_text )

def edit():
    """Edit a post"""
    p = db.restaurant(request.args(0)) or redirect(URL('default', 'index'))

    form = SQLFORM(db.restaurant, record=p)
    
    if form.process().accepted:
        session.flash = T('Updated')
        redirect(URL('default', 'view', args=[p.id]))
    # p.name would contain the name of the poster.
    return dict(form=form)

def add_happy_hours():
    p = db.restaurant(request.args(0)) or redirect(URL('default', 'index'))
    HH = db(db.happy_hours.id == p['id']).select().first()
    restaurant_id = p['id']
    if HH is not None:
        #Happy hours exist. User wants to edit them.
        form = SQLFORM(db.happy_hours, record = HH)
        form.add_button('Cancel', URL('default', 'view', args=[restaurant_id]))
        if form.process().accepted:
            session.flash = T('Happy Hours Revised')
            redirect(URL('default', 'view', args=[p.id]))
    else:
        #User wants to add happy hours for the first time
        form = SQLFORM.factory(Field('mon_start', 'time',
                                     label = 'Monday start time'),
                               Field('mon_end', 'time',
                                     label = 'Monday end time'),
                               Field('mon_specials', 'text',
                                     label = 'Monday specials'),
                              Field('tues_start', 'time',
                                     label = 'Tuesday start time'),
                               Field('tues_end', 'time',
                                     label = 'Tuesday end time'),
                               Field('tues_specials', 'text',
                                     label = 'Tuesday specials'),
                               Field('wed_start', 'time',
                                     label = 'Wednesday start time'),
                               Field('wed_end', 'time',
                                     label = 'Wednesday end time'),
                               Field('wed_specials', 'text',
                                     label = 'Wednesday specials'),
                               Field('thur_start', 'time',
                                     label = 'Thursday start time'),
                               Field('thur_end', 'time',
                                     label = 'Thursday end time'),
                               Field('thur_specials', 'text',
                                     label = 'Thursday specials'),
                               Field('fri_start', 'time',
                                     label = 'Friday start time'),
                               Field('fri_end', 'time',
                                     label = 'Friday end time'),
                               Field('fri_specials', 'text',
                                     label = 'Friday specials'),
                               Field('sat_start', 'time',
                                     label = 'Saturday start time'),
                               Field('sat_end', 'time',
                                     label = 'Saturday end time'),
                               Field('sat_specials', 'text',
                                     label = 'Saturday specials'),
                               Field('sun_start', 'time',
                                     label = 'Sunday start time'),
                               Field('sun_end', 'time',
                                     label = 'Sunday end time'),
                               Field('sun_specials', 'text',
                                     label = 'Sunday specials')
                              )
        form.add_button('Cancel', URL('default', 'view', args=[restaurant_id]))
        
        if form.process().accepted:      
            #Success! Insert data into the happy hours database
            happy_hours_id = db.happy_hours.insert(id = p['id'],                                  
                                  monday_start_time = form.vars.mon_start,
                                  monday_end_time = form.vars.mon_end,
                                  monday_specials = form.vars.mon_specials,
                                  tuesday_start_time = form.vars.tues_start,
                                  tuesday_end_time = form.vars.tues_end,
                                  tuesday_specials = form.vars.tues_specials,
                                  wednesday_start_time = form.vars.wed_start,
                                  wednesday_end_time = form.vars.wed_end,
                                  wednesday_specials = form.vars.wed_specials,
                                  thursday_start_time = form.vars.thur_start,
                                  thursday_end_time = form.vars.thur_end,
                                  thursday_specials = form.vars.thur_specials,
                                  friday_start_time = form.vars.fri_start,
                                  friday_end_time = form.vars.fri_end,
                                  friday_specials = form.vars.fri_specials,
                                  saturday_start_time = form.vars.sat_start,
                                  saturday_end_time = form.vars.sat_end,
                                  saturday_specials = form.vars.sat_specials,
                                  sunday_start_time = form.vars.sun_start,
                                  sunday_end_time = form.vars.sun_end,
                                  sunday_specials = form.vars.sun_specials
                                  )
            session.flash = T('Happy Hours Added')
            redirect(URL('default', 'view', args=[restaurant_id]))
    
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

@request.restful()
def api():
    API_BASE = "http://opentable.herokuapp.com"
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
