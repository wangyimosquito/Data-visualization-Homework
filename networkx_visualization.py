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
with open("./subGraph2/node3.json", "r") as json_file:
	subgraph_node_json = json.load(json_file)
with open("./subGraph2/link3.json", "r") as json_file:
	subgraph_link_json = json.load(json_file)


with open(node_json_path, "r") as json_file:
	node_json = json.load(json_file)

G1 = nx.DiGraph()

#获取所有节点
G1.add_nodes_from(subgraph_node_json)

#获取连边
#连边去重复
# link = []
# link_reduce = {}
# for each_link in subgraph_link_json:
# 	node1 = each_link[0]
# 	node2 = each_link[1]
# 	#找到方向性
# 	if(link_json[node1] == node2):
# 		pass
# 	else:
# 		tmp = node1
# 		node1 = node2
# 		node2 = tmp
# 	if(node1+node2 in link_reduce):
# 		pass
# 	else:
# 		link_reduce[node1+node2] = 1
# 		link.append((node1,node2))
link = subgraph_link_json
G1.add_edges_from(link)

#获取标签,并根据标签设置颜色
Label = {}
Color = []
count = 0 
for each_node in subgraph_node_json:
	if each_node == 'Domain_24acfd52f9ceb424d4a2643a832638ce1673b8689fa952d9010dd44949e6b1d9' or each_node == 'Domain_9c72287c3f9bb38cb0186acf37b7054442b75ac32324dfd245aed46a03026de1':
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
