import pandas as pd
import numpy as np
import json


node_data_path = 'Node.csv'
link_data_path = 'Link.csv'

node_json_path = 'node.json'
link_json_path = 'link.json'
link_type_json_path = 'link_type.json'

class readData:
	def __init__(self):
		self.node_data = pd.read_csv(node_data_path)
		self.link_data = pd.read_csv(link_data_path)
		self.node_data = np.array(self.node_data)
		self.link_data = np.array(self.link_data)
	
	#生成节点信息json文件ID: {'type': 'IP'...}
	def node_to_dic(self):
		node_json = {}
		new_node_json = {}
		for i in self.node_data:
			#需要将字符串识别为数组
			industry = self.parse_industry(i[3])
			node_json[i[0]] = {'name': i[1], 'type': i[2], 'industry': i[3]}
			new_node_json[i[0]] = {'name': i[1], 'type': i[2], 'industry': industry}
		dict_json = json.dumps(node_json)
		with open(node_json_path,'w+') as file:
			file.write(dict_json)
		dict_json = json.dumps(new_node_json)
		with open("new_node.json",'w+') as file:
			file.write(dict_json)
	
	#生成有向连边邻接表A——>[B,C,D]
	def link_to_dic(self):
		link_json = {}
		source = []
		source_index = {}
		for i in range(len(self.node_data)):
			source_id = self.node_data[i][0]
			source_index[source_id] = i
			source.append([])

		for i in self.link_data:
			source_id = i[1]
			target_id = i[2]
			index = source_index[source_id]
			source[index].append(target_id)

		for key, value in source_index.items():
			source_id = key
			index = value
			link_json[source_id] = source[index]
		
		# for key, value in link_json.items():
		# 	print(key)
		# 	print(value)
		# 	break
		
		dict_json = json.dumps(link_json)
		with open(link_json_path,'w+') as file:
			file.write(dict_json)
	
	#生成节点涉及非法产业列表
	def parse_industry(self, str):
		industry = []
		for c in str:
			if c == 'A':
				industry.append('A')
			if c == 'B':
				industry.append('B')
			if c == 'C':
				industry.append('C')
			if c == 'D':
				industry.append('D')
			if c == 'E':
				industry.append('E')
			if c == 'F':
				industry.append('F')
			if c == 'G':
				industry.append('G')
			if c == 'H':
				industry.append('H')
			if c == 'I':
				industry.append('I')
		return industry

	#节点连边类型字典 ID1+ID2 : Link-type
	def link_type_dic(self):
		link_json = {}
		for i in self.link_data:
			link_json[i[1]+i[2]] = i[0]
		
		dict_json = json.dumps(link_json)
		with open(link_type_json_path,'w+') as file:
			file.write(dict_json)

	#所有节点的无向邻接表，即每个节点所有相连节点：A->[B,C,D,E...]
	def connect_dic(self):
		connect_json = {}
		for i in self.link_data:
			if i[1] in connect_json:
				old = connect_json[i[1]]
				old.append(i[2])
				connect_json[i[1]] = old
			else:
				connect_json[i[1]] = [i[2]]

			if i[2] in connect_json:
				old = connect_json[i[2]]
				old.append(i[1])
				connect_json[i[2]] = old
			else:
				connect_json[i[2]] = [i[1]]
		dict_json = json.dumps(connect_json)
		with open("connect.json",'w+') as file:
			file.write(dict_json)
		
if(__name__ == '__main__'):
	test = readData()
	test.connect_dic()
