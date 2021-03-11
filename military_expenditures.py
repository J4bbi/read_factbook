from main import json_objects, find_values, replace_in_list, explore_json
from models import db_session, Property, FloatValue
import re


def split_values(line):
    values = []  #[t.strip() for t in re.split(r'/', line)]

    for v in [t.strip() for t in re.split(r'/', line)]:
        m = re.match(r'(.*)\%.*\((.*)\)', v)
        values.append((m.group(1), m.group(2)))

    return values


all_products = []
property_name = 'Military expenditures'

me_p = Property(type='float',
                name=property_name,
                description="This entry gives estimates on spending on defense programs for the most recent year available as a percent of gross domestic product (GDP); the GDP is calculated on an exchange rate basis, i.e., not in terms of purchasing power parity (PPP). For countries with no military forces, this figure can include expenditures on public security and police.",
                year_cia=2020)

db_session.add(me_p)
db_session.commit()

for country in json_objects:
    # print(country['id']['text'])
    obj_list = explore_json(country)
    military_expenditures = find_values(obj_list, property_name) or []

    for me in military_expenditures:
        if me:
            me_values = split_values(me[1])[0]
            year_est = me_values[1][:4]

            me_obj = FloatValue(country=country['id']['text'],
                                property_id=me_p.id,
                                year_est=int(year_est),
                                value=float(me_values[0]))
            db_session.add(me_obj)
            db_session.commit()
            print(split_values(me[1]))

    #print(military_expenditures)

