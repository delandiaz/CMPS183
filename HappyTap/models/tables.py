# -*- coding: utf-8 -*-

# Table for happy hours
db.define_table('happy_hours',
                Field('monday_start_time', 'time'),
                Field('monday_end_time', 'time'),
                Field('monday_specials', 'text', widget=SQLFORM.widgets.text.widget),
                Field('tuesday_start_time', 'time'),
                Field('tuesday_end_time', 'time'),
                Field('tuesday_specials', 'text', widget=SQLFORM.widgets.text.widget),
                Field('wednesday_start_time', 'time'),
                Field('wednesday_end_time', 'time'),
                Field('wednesday_specials', 'text', widget=SQLFORM.widgets.text.widget),
                Field('thursday_start_time', 'time'),
                Field('thursday_end_time', 'time'),
                Field('thursday_specials', 'text', widget=SQLFORM.widgets.text.widget),
                Field('friday_start_time', 'time'),
                Field('friday_end_time', 'time'),
                Field('friday_specials', 'text', widget=SQLFORM.widgets.text.widget),
                Field('saturday_start_time', 'time'),
                Field('saturday_end_time', 'time'),
                Field('saturday_specials', 'text', widget=SQLFORM.widgets.text.widget),
                Field('sunday_start_time', 'time'),
                Field('sunday_end_time', 'time'),
                Field('sunday_specials', 'text', widget=SQLFORM.widgets.text.widget)
    )

db.happy_hours.id.readable = False

#Table for restaurant data
db.define_table('restaurant',
                Field('id'),
                Field('name'),
                Field('address'),
                Field('city'),
                Field('state_'),
                Field('zipcode'),
                Field('latitude'),
                Field('longitude'),
                Field('website'),
                Field('phone', widget=SQLFORM.widgets.text.widget),
                Field('hours', 'string', widget=SQLFORM.widgets.text.widget),
                Field('has_happy_hours')
                )
db.restaurant.has_happy_hours.readable = db.restaurant.has_happy_hours.writable = False
db.restaurant.has_happy_hours.writable
db.restaurant.name.readable = True
db.restaurant.latitude.readable = db.restaurant.latitude.writable = False
db.restaurant.longitude.readable = db.restaurant.longitude.writable = False
db.restaurant.phone.requires = IS_MATCH('^1?((-)\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$', error_message="Not a valid phone number")
db.restaurant.zipcode.requires = IS_MATCH('^[0-9]{5}(-[0-9]{4})?$', error_message="Not a valid US Zipcode")
db.restaurant.id.readable = False
db.restaurant.hours.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='Tuesday-Thursday, 5:30pm-10:00pm')
#db.restaurant.specials.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='$1 Margarita Pitchers')
db.restaurant.phone.widget = lambda f,v: SQLFORM.widgets.string.widget(f, v, _placeholder='(000)000-0000')
