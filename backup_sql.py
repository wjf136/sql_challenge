import os
import re
import collections
import shlex
import json

def get_all_file_names(directory):
  """directory must be absolute path. 
  Returns an array with the fully qualified name"""
  return map(lambda x:os.path.join(directory, x) , os.listdir(directory))

def read_file(file):
  """file is a string of the absolute path to the file.
  Returns a string representation of the file"""
  with open(file, 'r') as f:
    file_string = f.read()
  return file_string

class ParsedData(object):
  
  def __init__(self, file_str):
    self.table = self.__get_table_name(file_str)
    self.fields = self.__get_fields(file_str)
    self.primary_key = self.fields.keys()[0]
    self.values = self.__get_values(file_str)
  
  def __get_table_name(self, data_str):
    match_obj = re.search(r'-- Definition of table `(.*)`' , data_str)
    return match_obj.group(1)

  def __get_fields(self, data_str):
    begin = data_str.find("CREATE TABLE")
    end = data_str.find("ENGINE")
    fields = collections.OrderedDict()

    #Get the segment that defines the tables and parse each line
    for line in data_str[begin:end].splitlines():
      exp = re.search(' `(.*?)` (.*?)\s(.+?)(\,)?$', line)
      if exp:
        fields[exp.group(1)] = [exp.group(2), exp.group(3)]
    return fields

  def __get_values(self, data_str):
    begin = data_str.find("VALUES")
    values = {}
    for line in data_str[begin:].splitlines():
      exp = re.search(' \((.*?),(.*)\)', line)
      if exp:
        key = exp.group(1)
        field_vals = shlex.split(exp.group(2))[0].split(',')
        field_vals_dict = {}
        for ordered_key in self.fields.keys()[1:]:
          field_vals_dict[ordered_key] = field_vals.pop(0)
        values[key] = field_vals_dict
    return values

  def generate_full_object(self):
    return {'table': self.table,
            'fields': self.fields,
            'values': self.values,
            'primary_key': self.primary_key}

class BackupData(object):

  def __init__(self):
    self.content = {}
    self.json = ''

  def load_from_dictionary(self, dictionary):
    self.content = dictionary
    self.__update_json()

  def load_from_json(seld, json):
    self.json = json
    self.__update_content()

  def __update_json(self):
    self.json = json.dumps(self.content)

  def __update_content(self):
    self.content = json.loads(self.json)