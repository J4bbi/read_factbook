import os
from fractions import Fraction

from bs4 import BeautifulSoup, NavigableString
import re
from models import Property, FloatValue, IntegerValue, db_session, Category

root_dir = 'factbook/geos'


def get_json():
    files = []
    for d, sd, fs in os.walk(root_dir):
        for f in fs:
            if not f.startswith('print'):
                jf = d + "/" + f
                files.append(jf)

    return files


html_files = get_json()


def find_values(obj, header):
    for i in obj:
        if i == header:
            return obj[i]
        elif isinstance(obj[i], dict):
            print(obj[i])
            result = find_values(obj[i], header)

            if result is not None:
                return result


def get_field_listing(link):
    linked = link.split('/')
    file = linked[2].split('#')
    field_html = 'factbook/' + linked[1] + '/' + file[0]
    field_link = '../fields/' + file[1] + '.html'

    field_soup = BeautifulSoup(open(field_html, 'r'), 'html.parser')
    container = field_soup.find_all(href=field_link)[0].parent.parent.parent.find(class_='category_data')

    return container.text.strip()


def process_value(c_elem, _class):
    if c_elem.find(class_=_class):
        val = c_elem.find(class_=_class).text.strip()
        return val if val != '' else None


def process_text(container, data_type):
    c_name = process_value(container, 'subfield-name')
    c_date = process_value(container, 'subfield-date')
    c_value = ''

    ps = container.find_all('p')
    brs = container.find_all('br')

    if ps:
        if brs:
            container.br.replace_with("\n")

        for i, p in enumerate(ps):
            c_value += p.text.strip()
            if len(ps) > 1 and i < len(ps):
                c_value += "\n"
    elif data_type == 'note':
        if brs:
            container.br.replace_with("\n")
        c_value = container.text.strip()
    else:
        c_value = re.sub(r'\n', '', container.text.strip())

    if c_date:
        c_value = c_value.replace(c_date, '').strip()

    if c_name:
        c_value = c_value.replace(c_name, '').strip()

    return c_name, c_value[6:], c_date


def process_data(name, c_elem, element_id):
    element = {'name': name, 'value': [], 'id': element_id}

    for c in c_elem.children:
        if not isinstance(c, NavigableString):
            # Class will be of the last type one of
            # text, numeric, note, attachment

            try:
                data_type = list(c['class']).pop()
                value = {'type': data_type}

                # If text then value is contents
                if data_type == 'text' or data_type == 'note':
                    value['value'] = process_text(c, data_type)
                elif data_type == 'numeric' or data_type == 'historic':
                    c_name = process_value(c, 'subfield-name')
                    c_number = process_value(c, 'subfield-number')
                    c_note = process_value(c, 'subfield-note')
                    c_date = process_value(c, 'subfield-date')
                    value['value'] = (c_name, c_number, c_note, c_date)

                element['value'].append(value)

            except KeyError:
                # dismiss comparison element
                pass

    return element


def find_element(element_name, element_list=None):
    if element_list is None:
        element_list = hierarchy

    # results = list(filter(lambda x: (x['name'] == element_name), element_list))

    for element in element_list:
        if element['name'] == element_name:
            return element
        elif 'children' in element:
            result = find_element(element_name, element['children'])

            if result:
                return result


def get_data(file):
    soup = BeautifulSoup(open(file, 'r'), 'html.parser')
    sas = soup.find('ul', class_='expandcollapse')

    for elem in [c for c in sas.children if not isinstance(c, NavigableString)]:
        anchor = elem.find('a')

        if 'anchor' in elem['id']:
            heading = anchor.text.strip()
            heading = heading[:heading.index(' :')]
            hierarchy.append({'children': [], 'name': heading, 'id': ''})
        else:
            for elem_child in [c for c in elem.children if not isinstance(c, NavigableString)]:
                if 'field-anchor' not in elem_child['id']:
                    key = heading.lower().replace(' ', '-') + '-' + elem_child['id'][6:]
                    key_anchor = sas.find(id='field-anchor-' + key).find('a')
                    name = key_anchor.text.strip()

                    child_id = key_anchor['href'].split('#')[1]

                    data = process_data(name, elem_child, child_id)
                    cia_elem = list(filter(lambda x: (x['name'] == heading), hierarchy))[0]
                    cia_elem['id'] = key_anchor['href'].split('#')[1]

                    if data:
                        cia_elem['children'].append(data)


check = False
c_e = Category(name='Economy')
db_session.add(c_e)
db_session.commit()

for f in html_files:
    hierarchy = []
    heading = None

    get_data(f)
    print(hierarchy)

    result = find_element('GDP (purchasing power parity)')

    if result:

        if not check:
            p = Property(type='integer',
                         category_id=c_e.id,
                         name=result['name'],
                         description=get_field_listing('../docs/notesanddefs.html#' + result['id']),
                         year_cia=2019)
            db_session.add(p)
            db_session.commit()
            check = True

        note = list(filter(lambda x: (x['type'] == 'note'), result['value']))

        for v in [c for c in result['value'] if c['type'] != 'note']:
            year_est = None

            country = f.split('/')[2][:2]

            try:
                year_est = int(v['value'][3][1:5])
            except IndexError:
                pass
            except ValueError:
                year_est = int("20" + v['value'][3][3:5])

            values = v['value'][1].split(' ')
            value = Fraction(values[0][1:])  # int(re.sub(r'[$.]', '', values[0]))

            if values[1] == 'billion':
                value = 10 ** 9 * value
            elif values[1] == 'million':
                value = 10 ** 6 * value
            elif values[1] == 'trillion':
                value = 10 ** 12 * value

            test = None

            if note:
                test = note[0]['value'][1]

            i = IntegerValue(property_id=p.id,
                             country=country,
                             year_est=year_est,
                             value=int(value),
                             note=test)

            db_session.add(i)
            db_session.commit()
