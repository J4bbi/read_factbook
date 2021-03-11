import re
from main import json_objects, find_values, replace_in_list, explore_json
from collections import Counter


def split_values(line):
    values = [t.strip() for t in re.split(r'(?<!\()[,;/](?![\w\s]*[)])', line)]

    # Formatting errors to be corrected

    for val in values:
        if 'cassava' not in val:
            if '(' in val:
                if 'various' in val:
                    replace_in_list(values, val, val[:val.index(' (')])
                elif ')' not in val:
                    replace_in_list(values, val, val.split(' ('))
            elif ')' in val:
                replace_in_list(values, val, val[:len(val)-1].split(', '))

            if ' and ' in val:
                # Edge cases
                if '(' in val:
                    if val == 'grain (mostly spring wheat and barley)':
                        replace_in_list(values, 'grain (mostly spring wheat and barley)',
                                        ['grain', 'wheat', 'barley'])
                    elif val == 'fruits and vegetables (grown in the few oases)':
                        replace_in_list(values, 'fruits and vegetables (grown in the few oases)',
                                        ['fruits', 'vegetables'])
                    else:
                        replace_in_list(values, 'fruit (especially grapes and apricots)',
                                        ['fruits', 'grapes', 'apricots'])

                else:
                    replace_in_list(values, val,
                                    val.replace('other ', '').split(' and '))

            elif 'and ' in val and val[0] == 'a':
                replace_in_list(values, val, val[4:])
                #print()


    # Merging of inflated values

    for val in values:
        if 'cattle' in val and val != 'cattle':
            replace_in_list(values, val, 'cattle')
        elif 'dairy' in val and val != 'dairy products':
            replace_in_list(values, val, 'dairy products')
        elif 'coconut' == val:
            replace_in_list(values, val, 'coconuts')
        elif 'wide variety' in val:
            replace_in_list(values, val, 'fruits')
        elif 'grain' in val:
            replace_in_list(values, val, 'grains')
        elif 'wood' in val or 'lumber' in val:
            replace_in_list(values, val, 'timber')
        elif 'green vegetables' == val or 'fresh vegetables' == val:
            replace_in_list(values, val, 'vegetables')
        elif 'fruit' == val or 'tropical fruits' == val:
            replace_in_list(values, val, 'fruits')
        elif 'other' in val:
            replace_in_list(values, val, 'livestock products')
        elif 'sugar cane' == val:
            replace_in_list(values, val, 'sugarcane')
        elif 'soya' == val:
            replace_in_list(values, val, 'soybeans')
    return values


all_products = []
for country in json_objects:
    obj_list = explore_json(country)
    agriculture_products = find_values(obj_list, 'Agriculture - products')

    if agriculture_products:
        all_products += split_values(agriculture_products[0][1])

c = Counter(all_products)
print(c)