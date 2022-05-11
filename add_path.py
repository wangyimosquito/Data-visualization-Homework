
import json
from tokenize import String


# 单引号改双引号
def one2two(line:String):
	l = list(line)
	for i in range(len(l)):
		if(l[i] == "'"):
			l[i] = '"'
	ans = ''.join(l)
	return ans

#向子图中加入路径，使子图联通
def add_path():
	with open("./reduced_subGraph/node5.json", "r") as json_file:
		node = json.load(json_file)
	with open("./reduced_subGraph/link5.json", "r") as json_file:
		link = json.load(json_file)
	with open("./max_degree_node/group5.json", "r") as json_file:
		maxdegree_nodes = json.load(json_file)

	#建立连边set
	link_set = []
	for each_link in link:
		link_set.append(set(each_link))
	
	print("[",len(node),",",len(link),"]")

	paths = []
	with open("./paths/group5.json","r") as f:
		lines = f.readlines()
		for line in lines:
			line = one2two(line)
			#print(line)
			j = json.loads(line)
			paths.append(j)
	
	#对每个联通分支选择指定条数的Path加入
	for each_max_node in maxdegree_nodes:
		count = 0
		for each_path in paths:
			if each_path[0][0] == each_max_node:
				for each_link in each_path:
					if not(each_link[0] in set(node)):
						node.append(each_link[0])
						flag =True
					if not(each_link[1] in set(node)):
						node.append(each_link[1])
						flag = True
					if not(each_link in link_set):
						link.append(each_link)
				count += 1
				if count == 4:
					break
				
	print("[",len(node),",",len(link),"]")
	dict_json = json.dumps(node)
	with open("./reduced_subGraph2/node5.json",'w+') as file:
		file.write(dict_json)
	dict_json = json.dumps(link)
	with open("./reduced_subGraph2/link5.json",'w+') as file:
		file.write(dict_json)

add_path()



# print(len(subgraph_node_json))
# print(len(link))

# set1 = set(subgraph_node_json)
# new_link = []
# for each_link in link:
# 	if each_link[0] in set1 and each_link[1] in set1:
# 		new_link.append(each_link)

# print(len(new_link))

# dict_json = json.dumps(new_link)
# with open("./subGraph2/link5.json",'w+') as file:
# 	file.write(dict_json)

# count = 0
# for each_node in node:
# 	if node_json[each_node]['type'] == 'Domain':
# 		if len(connect_json[each_node])>50:
# 			#print(len(connect_json[each_node]))
# 			count += 1
# print(count)

# print(len(node), len(link))


# for each_path in path:
# 	for each_link in each_path:
# 		if not(each_link[0] in set(node)):
# 			node.append(each_link[0])
# 		if not(each_link[1] in set(node)):
# 			node.append(each_link[1])
# 		if not(each_link in set(link)):
# 			link.append(each_link)

# print(len(node), len(link))
		


