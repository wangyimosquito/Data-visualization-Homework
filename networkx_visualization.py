import networkx as nx
import matplotlib.pyplot as plt
import json

node_data_path = 'Node.csv'
link_data_path = 'Link.csv'

node_json_path = 'new_node.json'
link_json_path = 'link.json'

IP_industry_json_path = 'IP_Industry.json'
Cert_industry_json_path = 'Cert_Industry.json'

Link_type_json_path = 'link_type.json'
Connect_json_path = 'connect.json'

#可视子图节点和连边函数路径
with open("./reduced_subGraph2/node5.json", "r") as json_file:
	subgraph_node_json = json.load(json_file)
with open("./reduced_subGraph2/link5.json", "r") as json_file:
	subgraph_link_json = json.load(json_file)

# with open("./subGraph2/node1.json", "r") as json_file:
# 	subgraph_node_json = json.load(json_file)
# with open("./subGraph2/link1.json", "r") as json_file:
# 	subgraph_link_json = json.load(json_file)

with open(node_json_path, "r") as json_file:
	node_json = json.load(json_file)

with open(Connect_json_path, "r") as json_file:
	connect = json.load(json_file)

def visualize():
	G1 = nx.DiGraph()

	#获取所有节点
	G1.add_nodes_from(subgraph_node_json)
	link = subgraph_link_json
	G1.add_edges_from(link)

	#获取标签,并根据标签设置颜色
	Label = {}
	Color = []
	count = 0 
	for each_node in subgraph_node_json:
		if each_node == 'Domain_24acfd52f9ceb424d4a2643a832638ce1673b8689fa952d9010dd44949e6b1d9' or each_node == 'Domain_9c72287c3f9bb38cb0186acf37b7054442b75ac32324dfd245aed46a03026de1' or each_node == 'Domain_717aa5778731a1f4d6f0218dd3a27b114c839213b4af781427ac1e22dc9a7dea' or each_node == 'Domain_8748687a61811032f0ed1dcdb57e01efef9983a6d9c236b82997b07477e66177' or each_node == 'Whois_Phone_f4a84443fb72da27731660695dd00877e8ce25b264ec418504fface62cdcbbd7':
			Color.append('green')
			if node_json[each_node]['type'] == 'Domain':
				Label[each_node] = 'D'
			else:
				Label[each_node] = node_json[each_node]['type']
		else:
			if node_json[each_node]['type']=='Domain':
				Label[each_node] = 'D'
				Color.append("blue")
			else:
				Label[each_node] = node_json[each_node]['type']
				Color.append("red")

	nx.draw(G1, node_size=600, labels=Label,with_labels=True,node_color=Color, alpha=0.5, edge_color = 'grey',pos = nx.kamada_kawai_layout(G1))
	#nx.draw(G1, node_size=600, labels=Label,with_labels=True,node_color=Color, alpha=0.5, edge_color = 'grey',pos = nx.spring_layout(G1))
	plt.show()

#检查图连通性
def connection():
	G1 = nx.Graph()
	#获取所有节点
	G1.add_nodes_from(subgraph_node_json)
	link = subgraph_link_json
	G1.add_edges_from(link)
	print(nx.is_connected(G1))
	representation_node = []

	for i in nx.connected_components(G1):
		print(len(i))
		
		#找出联通分支里度最高的点
		max_degree = 0
		max_node = " "
		for each_node in i:
			if len(connect[each_node])>max_degree:
				max_node = each_node
		representation_node.append(max_node)
		# if len(i)>4000:
		# 	dict_json = json.dumps(list(i))
		# 	with open("./reduced_subGraph2/node4.json",'w+') as file:
		# 		file.write(dict_json)
	print("banch num: ", len(representation_node))

#修改删去
def delete_extra_node():
	print(len(subgraph_node_json))
	node = set(subgraph_node_json)
	new_link = []
	for each_link in subgraph_link_json:
		if each_link[0] in node and each_link[1] in node:
			new_link.append(each_link)
	print(len(subgraph_link_json),"->" ,len(new_link))
	dict_json = json.dumps(new_link)
	with open("./reduced_subGraph2/link4.json",'w+') as file:
		file.write(dict_json)
# connection()
# delete_extra_node()
