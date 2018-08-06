from collections import OrderedDict
import yaml

def addOrderedDictToYamlInterpreter():
	from yaml import SafeLoader, SafeDumper
	from yaml.representer import SafeRepresenter

	_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

	def dict_representer(dumper, data):
	    return dumper.represent_dict(data.iteritems())


	def dict_constructor(loader, node):
	    return OrderedDict(loader.construct_pairs(node))

	SafeDumper.add_representer(OrderedDict, dict_representer)
	SafeLoader.add_constructor(_mapping_tag, dict_constructor)

	SafeDumper.add_representer(str, SafeRepresenter.represent_str)