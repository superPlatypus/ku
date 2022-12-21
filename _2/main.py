# import zipfile
# import requests
# import io
# import sys
# from graphviz import Source
#
# def get_deps(main_package):
# 	r = requests.get(f"https://pypi.org/pypi/{main_package}/json").json()
# 	version = r["info"]["version"]
# 	releases = r["releases"]
# 	last_release = releases[version][0]
# 	url_whl = last_release["url"]
# 	name = url_whl.split("/")[-1]
# 	whl_file = requests.get(url_whl)
# 	deps = set()
# 	archive = zipfile.ZipFile(io.BytesIO(whl_file.content))
# 	for f in archive.namelist():
# 		if f.endswith("METADATA"):
# 			for l in archive.open(f).read().decode("utf-8").split("\n"):
# 				if 'requires-dist' in l.lower():
# 					dep = str(l).split(" ")
# 					if "extra" in dep: break
# 					dep =dep[1]
# 					dep = dep.split("\\")[0]
# 					deps.add(dep)
#
#
# 	return deps
#
# def format_to_dicts(main_package, deps):
# 	deps_format = {}
# 	deps_format[main_package] = []
# 	for dep in deps:
# 		dep = dep.split(" ")
# 		if dep == main_package: continue
# 		if not "extra" in dep:
# 			package_name = dep[0]
# 			int_deps = get_deps(package_name)
# 			int_deps_format = format_to_dicts(package_name, int_deps)
# 			deps_format[main_package].append(int_deps_format)
# 	return deps_format
#
# def convert_to_graphviz(dicts):
# 	graphviz = ""
# 	for key in dicts:
# 		if dicts[key] == []:
# 			return f"\"{key}\";\n"
# 		for dict in dicts[key]:
# 			graphviz+=f"\"{key}\"->{convert_to_graphviz(dict)}"
# 	return graphviz
#
#
#
# main_package = sys.argv[1]
# deps = get_deps(main_package)
# dicts = format_to_dicts(main_package, deps)
# links = convert_to_graphviz(dicts)
# graphviz = "digraph G {\n"+links+"}"
# print(graphviz)
# with open('output.dot', 'w') as file:
# 	file.write(graphviz)
# path = 'output.dot'
# s = Source.from_file(path)
# s.view()





import requests
import argparse
import string


def get_requires_dist(module_name):
	# запрос на сайт для получения зависимостей
	# base_url = f"https://pypi.org/pypi/{module_name}/json"
	r = requests.get(f"https://pypi.org/pypi/{module_name}/json")
	# r = requests.get(base_url)
	data = r.json()

	if data.get("message") and data["message"] == "Not Found":
		print("Модуль не найден")
		return []

	requires_dist = data["info"]["requires_dist"]

	# выделение названий зависимостей
	dependencies = [module_name]

	if requires_dist:
		for dep in requires_dist:
			dep = dep.split(" ")[0]
			dependencies.append(dep)

	return dependencies


def create_nodes(dependencies, module_name):
	# организация вершин графа
	ascii_uppercase = list(string.ascii_uppercase)
	nodes = []

	for i in range(len(dependencies)):
		name = ""
		# если превышен лимит букв, то прибавляется число
		if i > len(ascii_uppercase):
			name += ascii_uppercase[(i % len(ascii_uppercase)) - 1] + str(i % len(ascii_uppercase))
		name = ascii_uppercase[i]

		# [название вершины, название зависимости, название головного модуля]
		nodes.append([name, dependencies[i], module_name])
	return nodes


def create_graph(nodes):
	# digraph Module { A[label='django'] A -> B }
	graph = "digraph Module {\n"

	# объявление вершин и их заголовки
	for node in nodes:
		graph += f'  {node[0]}[label="{node[1]}"]\n'

	# установление связей
	for node in nodes:
		module = []
		# исключение первого элемента
		if node[1] != node[2]:
			# поиск главного модуля
			for i in range(len(nodes)):
				if nodes[i][1] == node[2]:
					module = nodes[i]
			graph += f"  {module[0]} -> {node[0]}\n"
	graph += "}"
	return graph


if __name__ == "__main__":
	# получение названия модуля из командной строки
	parser = argparse.ArgumentParser()
	parser.add_argument("module")
	args = parser.parse_args()
	module_name = args.module

	dependencies = get_requires_dist(module_name)
	nodes = create_nodes(dependencies, module_name)
	graph = create_graph(nodes)

	print(graph)