import json

def get_config(filename):
  f = open(filename)
  data = json.load(f)
  names = []
  bounds = []
  parameter_count = len(data["parameter"])
  for item in data["parameter"]:
    names.append(item["name"])
    bounds.append(item["bounds"])
  layers = int(data["layers"])
  return parameter_count, names, bounds, layers

def out_to_config_file(samples):
  f = open("test-point.josn", "w")
  json.dump(samples, f)
