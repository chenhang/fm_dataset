import json
import os
import re

from dateutil.parser import parse


def load_json(file_name, default=dict):
    if os.path.exists(file_name):
        with open(file_name) as json_data:
            d = json.load(json_data)
            return d
    else:
        return default()


def write_json(file_name, json_data):
    print('writing:' + file_name)
    with open(file_name, 'w') as outfile:
        json.dump(json_data, outfile, ensure_ascii=False)
        print('writing done:' + file_name)
        return True


def convert_date(date_str):
    # "1987-06-23T23:00:00.0000000Z"
    datetime_object = parse(date_str).astimezone()
    return "{0}/{1}/{2}".format(datetime_object.year,
                                datetime_object.month,
                                datetime_object.day)


def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name.replace(" ", ""))
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items() if k is not None and v is not None)
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj if x is not None)
    if obj is None:
        return ""
    else:
        return obj


def data_changed(local_item, item):
    return ordered(local_item) != ordered(item)


class XmlListConfig(list):
    def __init__(self, aList):
        super().__init__()
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    def __init__(self, parent_element, **kwargs):
        super().__init__(**kwargs)
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})
