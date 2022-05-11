import pandas as pd
import numpy as np
import json
import random

node_data_path = 'Node.csv'
link_data_path = 'Link.csv'

node_json_path = 'new_node.json'
link_json_path = 'link.json'

IP_industry_json_path = 'IP_Industry.json'
Cert_industry_json_path = 'Cert_Industry.json'

Link_type_json_path = 'link_type.json'
Connect_json_path = 'connect.json'

class task1:
	def __init__(self):
		self.node_data = pd.read_csv(node_data_path)
		self.link_data = pd.read_csv(link_data_path)
		self.node_data = np.array(self.node_data)
		self.link_data = np.array(self.link_data)

		with open(node_json_path, "r") as json_file:
			self.node_json = json.load(json_file)
		with open(link_json_path, "r") as json_file:
			self.link_json = json.load(json_file)
		with open(Link_type_json_path, "r") as json_file:
			self.link_type_json = json.load(json_file)
		with open(Connect_json_path, "r") as json_file:
			self.connect_json = json.load(json_file)

	def ultra_pruning_three_hop(self, init_node, file_name):
			node_file_name = "./subGraph2/node"+file_name+".json"
			link_file_name = "./subGraph2/link"+file_name+".json"
			#先将起始节点加入子图中
			node = [init_node]
			link = []
			
			#检查第一跳节点的类型，如果是Domain节点，则检查其是否存在相连的Cert节点和IP节点，优先从Cert节点开始计算
			init_type = self.node_json[init_node]['type']
			if(init_type == 'Domain'):
				flag = False
				for i in self.connect_json[init_node]:
					if self.node_json[init_node]['type'] == 'Cert':
						init_node = i
						flag = True
						break
				if flag == False:
					for i in self.connect_json[init_node]:
						if self.node_json[init_node]['type'] == 'IP':
							init_node = i
							flag = True
							break
			
			#第一跳节点
			first_hop_node = []
			first_hop_link = []
			for i in self.connect_json[init_node]:
				node.append(i)
				if init_node+i in self.link_type_json:
						link_type = self.link_type_json[init_node+i]
				else:
					link_type = self.link_type_json[i+init_node]
				link.append([init_node, i, link_type])
				#通过连边强度筛选参与下一轮挖掘的节点
				if(link_type == 'r_cert' or link_type == 'r_dns_a' or link_type == 'r_subdomain' or link_type == 'r_request_jump' or link_type == 'r_whois_name' or link_type == 'r_whois_email' or link_type == 'r_whois_phone'):
					first_hop_node.append(i)
					first_hop_link.append([init_node, i, link_type])
					

			#第二跳节点
			#统计第二跳的IP和Cert数量
			IP_2_hop_Num = 0
			Cert_2_hop_Num =0
			second_hop_node = []
			for each_node in first_hop_node:
				for i in self.connect_json[each_node]:
					#获取边类型
					if each_node+i in self.link_type_json:
						link_type = self.link_type_json[each_node+i]
					else:
						link_type = self.link_type_json[i+each_node]
					#加入节点
					if self.node_json[i]['type'] == "IP":
						IP_2_hop_Num += 1
					elif self.node_json[i]['type'] == "Cert":
						Cert_2_hop_Num += 1
					node.append(i)
					#剪枝
					if(link_type == 'r_cert' or link_type == 'r_dns_a' or link_type == 'r_subdomain' or link_type == 'r_request_jump' or link_type == 'r_whois_name' or link_type == 'r_whois_email' or link_type == 'r_whois_phone'):
						second_hop_node.append(i)
					#加入边
					link.append([i, each_node, link_type])

			#第三跳节点
			third_hop_node = []
			third_hop_link = []
			for each_node in second_hop_node:
				for i in self.connect_json[each_node]:
					third_hop_node.append(i)
					if each_node+i in self.link_type_json:
						link_type = self.link_type_json[each_node+i]
					else:
						link_type = self.link_type_json[i+each_node]
					third_hop_link.append([each_node, i, link_type])
			for each_node in third_hop_node:
				node.append(each_node)
			for each_link in third_hop_link:
				link.append(each_link)
			
			#分别存储下来每个线索生成的子图
			node = list(set(node))
			print(file_name+"node: ", len(node))
			link = self.link_reduce_redundency(link)
			print(file_name+"link: ", len(link))
			dict_json = json.dumps(node)
			with open(node_file_name,'w+') as file:
				file.write(dict_json)
			dict_json = json.dumps(link)
			with open(link_file_name,'w+') as file:
				file.write(dict_json)
			#返回节点和连边
			return node, link

	#挖掘前n跳节点
	def any_hop(self, init_node, file_name, hop_num):
			node_file_name = "./subGraph2/node"+file_name+".json"
			link_file_name = "./subGraph2/link"+file_name+".json"
			#先将起始节点加入子图中
			node = [init_node]
			link = []

			#检查第一跳节点的类型，如果是Domain节点，则检查其是否存在相连的Cert节点和IP节点，优先从Cert节点开始计算
			init_type = self.node_json[init_node]['type']
			if(init_type == 'Domain'):
				flag = False
				for i in self.connect_json[init_node]:
					if self.node_json[init_node]['type'] == 'Cert':
						init_node = i
						flag = True
						break
				if flag == False:
					for i in self.connect_json[init_node]:
						if self.node_json[init_node]['type'] == 'IP':
							init_node = i
							flag = True
							break
			
			last_hop_node = []
			last_hop_node_leave_hop = []
			curr_hop_node = [init_node]
			curr_hop_node_leave_hop = [inf]
			#循环
			for i in range(hop_num):
				last_hop_node = curr_hop_node
				last_hop_node_leave_hop = list(map(lambda x: x - 1, curr_hop_node_leave_hop))
				curr_hop_node = []
				curr_hop_node_leave_hop = []
				count = 0
				for each_node in last_hop_node:
					leave_hop = last_hop_node_leave_hop[count]
					if leave_hop>0:
						for i in self.connect_json[each_node]:
							if self.node_json[i]['type'] == 'Domain':
								if random.random()>0.95:
									node.append(i)
							else:
								node.append(i)
							if each_node+i in self.link_type_json:
									link_type = self.link_type_json[each_node+i]
							else:
								link_type = self.link_type_json[i+each_node]
							link.append([each_node, i, link_type])
							#通过连边强度筛选参与下一轮挖掘的节点
							if(link_type == 'r_cert' or link_type == 'r_dns_a' or link_type == 'r_subdomain' or link_type == 'r_request_jump'):
								curr_hop_node.append(i)
								curr_hop_node_leave_hop.append(inf)
							elif(link_type == 'r_whois_name' or link_type == 'r_whois_email' or link_type == 'r_whois_phone'):
								curr_hop_node.append(i)
								curr_hop_node_leave_hop.append(min(last_hop_node_leave_hop[count],2))
					count += 1

			#分别存储下来每个线索生成的子图
			node = list(set(node))
			print(file_name+"node: ", len(node))
			link = self.link_reduce_redundency(link)
			#连边去重
			new_link = []
			set1 = set(node)
			for each_link in link:
				if each_link[0] in set1 and each_link[1] in set1:
					new_link.append(each_link)
			link = new_link

			print(file_name+"link: ", len(link))
			dict_json = json.dumps(node)
			with open(node_file_name,'w+') as file:
				file.write(dict_json)
			dict_json = json.dumps(link)
			with open(link_file_name,'w+') as file:
				file.write(dict_json)
			#返回节点和连边
			return node, link

	def link_reduce_redundency(self, subgraph_link_json):
		#连边去重复
		# print("before reduce: ", len(subgraph_link_json))
		link = []
		link_reduce = {}
		for each_link in subgraph_link_json:
			node1 = each_link[0]
			node2 = each_link[1]
			#找到方向性
			flag = True
			for each_target in self.link_json[node1]:
				if each_target == node2:
					flag =False
			if flag == True:
				tmp = node1
				node1 = node2
				node2 = tmp
			if(node1+node2 in link_reduce):
				pass
			else:
				link_reduce[node1+node2] = 1
				link.append((node1,node2))
		#print("after reduce: ", len(link))
		return link

#多线索集合挖掘函数
	def subgraph(self, init_node_list, group_name, deep):
		node = []
		link = []
		clue_num = 1
		for each_clue in init_node_list:
			node_tmp, link_tmp = self.any_hop(each_clue, '_'+group_name+'_'+str(clue_num),deep)
			node.extend(node_tmp)
			link.extend(link_tmp)
			clue_num += 1
		#节点去重
		node = list(set(node))
		link = list(set(link))
		print("total group node: ", len(node))
		print("total group link: ",len(link))
		#保存子图节点和连边
		dict_json = json.dumps(node)
		with open("./subGraph2/node"+group_name+".json",'w+') as file:
			file.write(dict_json)
		dict_json = json.dumps(link)
		with open("./subGraph2/link"+group_name+".json",'w+') as file:
			file.write(dict_json)

	#删除外围节点
	def reduce_group_size(self, group_name, reduce_partial):
		node_file_name = "./subGraph2/node"+group_name+".json"
		link_file_name = "./subGraph2/link"+group_name+".json"
		with open(node_file_name, "r") as json_file:
			ori_node = json.load(json_file)
		with open(link_file_name, "r") as json_file:
			ori_link = json.load(json_file)
		node = []
		node_dic  ={}
		link = []
		#对于其中的最外围域名节点进行删减
		for each_node in ori_node:
			flag = True
			for each_link in ori_link:#检查该节点是否为最外层节点
				if (each_node == each_link[0]):
					flag = False
					break
			if flag == True:
				rand = random.random()
				if self.node_json[each_node]['type'] == 'Domain' and rand<reduce_partial:
					pass
				else:
					node.append(each_node)
					node_dic[each_node] = 1
			else:
				node.append(each_node)
				node_dic[each_node] = 1

		new_node = []	
		#对余下的点生成边列表
		for each_node in node:
			flag = False
			for each_target_node in self.link_json[each_node]:
				if each_target_node in node_dic:
					link.append((each_node, each_target_node))
					flag = True
					new_node.append(each_target_node)
			if flag == True:
				new_node.append(each_node)
		new_node = list(set(new_node))

		print("reduced total group node: ", len(new_node))
		print("reduced total group link: ", len(link))
		dict_json = json.dumps(new_node)
		with open("./reduced_subGraph/node"+group_name+".json",'w+') as file:
			file.write(dict_json)
		dict_json = json.dumps(link)
		with open("./reduced_subGraph/link"+group_name+".json",'w+') as file:
			file.write(dict_json)

	#对于团伙1的核心资产和核心链路识别，以及规模缩减
	def get_core_asset_node(self, group_name):
		with open("./reduced_subGraph/node"+group_name+".json", "r") as json_file:
			ori_node = json.load(json_file)
		#首先找到其核心资产
		core_node = []
		totol_candidate = []
		#如果一个节点的连边50%以上都是较弱连边，则其不是核心节点
		for each_node in ori_node:
			if self.node_json[each_node]['type'] == 'IP' or self.node_json[each_node]['type'] == 'Cert':
				totol_candidate.append(each_node)
				#对于IP节点统计其连边类型为弱的数量
				if self.node_json[each_node]['type'] == 'IP':
					count_weak = 0
					total_link = len(self.connect_json[each_node])
					#print("node[",each_node,"] total link num: ", total_link)
					for each_target in self.connect_json[each_node]:
						if each_node+each_target in self.link_type_json:
							if(self.link_type_json[each_node+each_target]) == 'r_asn' or (self.link_type_json[each_node+each_target]) == 'r_cidr':
								count_weak += 1
						else:
							if(self.link_type_json[each_target+ each_node]) == 'r_asn' or (self.link_type_json[each_target+each_node]) == 'r_cidr':
								count_weak += 1
					if count_weak/total_link < 0.5:
						core_node.append(each_node)
				#对于证书节点，肯定不存在弱边
				else:
					total_link = len(self.connect_json[each_node])
					#print("node[",each_node,"] total link num: ", total_link)
					core_node.append(each_node)

		print("delete weak most candidate: ", len(totol_candidate)," -> ",len(core_node))
		#如果一个域名连接了两个或者两个以上的IP，则这个IP不是核心节点
		delete_core = []
		for core1 in core_node:
			if self.node_json[core1]['type'] == 'IP':
				for core2 in core_node:
					if self.node_json[core2]['type'] == 'IP':
						if core1 == core2:
							pass
						else:
							#检查是否存在域名节点同时指向这两个节点
							for each_node in ori_node:
								if self.node_json[each_node]['type'] == 'Domain':
									if each_node+core1 in self.link_type_json and each_node+core2 in self.link_type_json:
										delete_core.append(core1)
										delete_core.append(core2)
										break
		tmp = core_node
		core_node = []
		for each_node in tmp:
			if not(each_node in set(delete_core)):
				core_node.append(each_node)
		print("delete distribute IP: ", len(tmp),"->", len(core_node))
		dict_json = json.dumps(core_node)
		with open("./core_asset/node"+group_name+".json",'w+') as file:
			file.write(dict_json)

	def reduce_group1_size(self):
		with open("./subGraph2/node1.json", "r") as json_file:
			ori_node = json.load(json_file)
		with open("./subGraph2/link1.json", "r") as json_file:
			ori_link = json.load(json_file)
		delete_node = []
		#对于两个domain节点最多的节点，进行domain节点删减
		for each_link in self.connect_json['Cert_fe794a69eacd63b21245bf4eda826222fc6c5862bebf77aa05459cb308cfd063']:
			if self.node_json[each_link]['type'] == 'Domain':
				if each_link in set(ori_node):
					if random.random() <0.99:
						delete_node.append(each_link)

		for each_link in self.connect_json['Cert_c01f10c61adcaa00ba6d4b85d30ec802bae76597915d7da4f8f094714ab0c597']:
			if self.node_json[each_link]['type'] == 'Domain':
				if each_link in set(ori_node):
					if random.random() <0.9:
						delete_node.append(each_link)

		new_node = []
		for each_node in ori_node:
			if not(each_node in set(delete_node)):
				new_node.append(each_node)
		print("reduce node: ", len(ori_node),"->", len(new_node))
		#对于剩下的节点的连边进行筛选：
		new_link = []
		for each_link in ori_link:
			source = each_link[0]
			target = each_link[1]
			if source in set(new_node) and target in set(new_node):
				new_link.append(each_link)
		print("reduce link: ", len(ori_link),"->", len(new_link))
		#保存删减过的点和连边
		dict_json = json.dumps(new_node)
		with open("./reduced_subGraph/node1.json",'w+') as file:
			file.write(dict_json)
		dict_json = json.dumps(new_link)
		with open("./reduced_subGraph/link1.json",'w+') as file:
			file.write(dict_json)

	def reduce_group2_size(self):
		with open("./subGraph2/node2.json", "r") as json_file:
			ori_node = json.load(json_file)
		with open("./subGraph2/link2.json", "r") as json_file:
			ori_link = json.load(json_file)
		delete_node = []
		#对于domain较多的节点分别进行不同程度的删减,并且只删减叶节点
		for each_link in self.connect_json['Domain_f6a5ffbe3609107c67362efaf5b804721398c40da76db27bc161aeef895e67bb']:
			if self.node_json[each_link]['type'] == 'Domain':
				if each_link in set(ori_node):
					if random.random() <0.5:
						delete_node.append(each_link)
		for each_link in self.connect_json['Domain_755f926df710773363ed73c670a17cc1cc728f5ef75bbdeaa3054a6f4c5a51a0']:
			if self.node_json[each_link]['type'] == 'Domain':
				if each_link in set(ori_node):
					if random.random() <0.5:
						delete_node.append(each_link)
	
		new_node = []
		for each_node in ori_node:
			if not(each_node in set(delete_node)):
				new_node.append(each_node)
		print("reduce node: ", len(ori_node),"->", len(new_node))
		#对于剩下的节点的连边进行筛选：
		new_link = []
		for each_link in ori_link:
			source = each_link[0]
			target = each_link[1]
			if source in set(new_node) and target in set(new_node):
				new_link.append(each_link)
		#对孤点进行删除
		iso_node = []
		for each_node in new_node:
			flag = False
			for each_link in new_link:
				if	each_link[0] == each_node or each_link[1] == each_node:
					flag = True
					break
			if flag == False:
				iso_node.append(each_node)
		tmp = new_node
		new_node = []
		for each_node in tmp:
			if not(each_node in set(iso_node)):
				new_node.append(each_node)
		print("reduce iso node node: ", len(tmp),"->", len(new_node))
		print("reduce link: ", len(ori_link),"->", len(new_link))
		
		#保存删减过的点和连边
		dict_json = json.dumps(new_node)
		with open("./reduced_subGraph/node2.json",'w+') as file:
			file.write(dict_json)
		dict_json = json.dumps(new_link)
		with open("./reduced_subGraph/link2.json",'w+') as file:
			file.write(dict_json)

	def reduce_group3_size(self):
		with open("./subGraph2/node3.json", "r") as json_file:
			ori_node = json.load(json_file)
		with open("./subGraph2/link3.json", "r") as json_file:
			ori_link = json.load(json_file)
		delete_node = []
		#对于所有度较大的IP和Cert节点进行删减
		reduce_IP_Cert_node = []
		for each_node in ori_node:
			if self.node_json[each_node]['type'] == 'IP' or  self.node_json[each_node]['type'] == 'Cert':
				if len(self.connect_json[each_node]) > 50:
					reduce_IP_Cert_node.append(each_node)
		for each_node in reduce_IP_Cert_node:
			for each_link in self.connect_json[each_node]:
				if self.node_json[each_link]['type'] == 'Domain':
					if each_link in set(ori_node):
						
						if random.random() <0.9:
							delete_node.append(each_link)

		
		delete_node = list(set(delete_node))
		#对其中所有domain节点进行随机删减
		for each_node in ori_node:
			if self.node_json[each_node]['type'] == 'Domain':
				for each_link in self.connect_json[each_node]:
					if self.node_json[each_link]['type'] == 'Domain':
						if each_link in set(ori_node):
							if random.random() <0.1:
								delete_node.append(each_link)
					elif self.node_json[each_link]['type'] == 'IP':
						if each_link in set(ori_node):
							if random.random() <0.1:
								delete_node.append(each_link)

		new_node = []
		for each_node in ori_node:
			if not(each_node in set(delete_node)):
				new_node.append(each_node)
		print("reduce node: ", len(ori_node),"->", len(new_node))
		#对于剩下的节点的连边进行筛选：
		new_link = []
		for each_link in ori_link:
			source = each_link[0]
			target = each_link[1]
			if source in set(new_node) and target in set(new_node):
				new_link.append(each_link)
		#对孤点进行删除
		#建立现存连边涉及点的集合
		link_node_set = []
		for each_link in new_link:
			link_node_set.append(each_link[0])
			link_node_set.append(each_link[1])
		link_node_set = set(link_node_set)
		iso_node = []
		for each_node in new_node:
			if not(each_node in link_node_set):
				iso_node.append(each_node)
		tmp = new_node
		new_node = []
		for each_node in tmp:
			if not(each_node in set(iso_node)):
				new_node.append(each_node)
		print("reduce iso node node: ", len(tmp),"->", len(new_node))
		print("reduce link: ", len(ori_link),"->", len(new_link))

		#保存删减过的点和连边
		dict_json = json.dumps(new_node)
		with open("./reduced_subGraph/node3.json",'w+') as file:
			file.write(dict_json)
		dict_json = json.dumps(new_link)
		with open("./reduced_subGraph/link3.json",'w+') as file:
			file.write(dict_json)

	def reduce_group4_size(self):
		with open("./subGraph2/node4.json", "r") as json_file:
			ori_node = json.load(json_file)
		with open("./subGraph2/link4.json", "r") as json_file:
			ori_link = json.load(json_file)
		delete_node = []
		#对于所有度较大的IP和Cert节点进行删减
		reduce_IP_Cert_node = []
		for each_node in ori_node:
			if self.node_json[each_node]['type'] == 'IP' or  self.node_json[each_node]['type'] == 'Cert':
				if len(self.connect_json[each_node]) > 6:
					reduce_IP_Cert_node.append(each_node)
		for each_node in reduce_IP_Cert_node:
			for each_link in self.connect_json[each_node]:
				if self.node_json[each_link]['type'] == 'Domain':
					if each_link in set(ori_node):
						if len(self.connect_json[each_node]) > 500:
							if random.random() <0.99:
								delete_node.append(each_link)
						else:
							if random.random() <0.9:
								delete_node.append(each_link)
		
		delete_node = list(set(delete_node))
		#对其中所有domain节点进行随机删减
		for each_node in ori_node:
			if self.node_json[each_node]['type'] == 'Domain':
				for each_link in self.connect_json[each_node]:
					if self.node_json[each_link]['type'] == 'Domain':
						if each_link in set(ori_node):
							if random.random() <0.99:
								delete_node.append(each_link)
					elif self.node_json[each_link]['type'] == 'IP':
						if each_link in set(ori_node):
							if random.random() <0.3:
								delete_node.append(each_link)

		new_node = []
		for each_node in ori_node:
			if not(each_node in set(delete_node)):
				new_node.append(each_node)
		print("reduce node: ", len(ori_node),"->", len(new_node))
		#对于剩下的节点的连边进行筛选：
		new_link = []
		for each_link in ori_link:
			source = each_link[0]
			target = each_link[1]
			if source in set(new_node) and target in set(new_node):
				new_link.append(each_link)
		#对孤点进行删除
		#建立现存连边涉及点的集合
		link_node_set = []
		for each_link in new_link:
			link_node_set.append(each_link[0])
			link_node_set.append(each_link[1])
		link_node_set = set(link_node_set)
		iso_node = []
		for each_node in new_node:
			if not(each_node in link_node_set):
				iso_node.append(each_node)
		tmp = new_node
		new_node = []
		for each_node in tmp:
			if not(each_node in set(iso_node)):
				new_node.append(each_node)
		print("reduce iso node node: ", len(tmp),"->", len(new_node))
		print("reduce link: ", len(ori_link),"->", len(new_link))

		#保存删减过的点和连边
		dict_json = json.dumps(new_node)
		with open("./reduced_subGraph/node4.json",'w+') as file:
			file.write(dict_json)
		dict_json = json.dumps(new_link)
		with open("./reduced_subGraph/link4.json",'w+') as file:
			file.write(dict_json)

	def reduce_group5_size(self):
		with open("./subGraph2/node5.json", "r") as json_file:
			ori_node = json.load(json_file)
		with open("./subGraph2/link5.json", "r") as json_file:
			ori_link = json.load(json_file)
		delete_node = []
		#对于所有度较大的IP和Cert节点进行删减
		reduce_IP_Cert_node = []
		for each_node in ori_node:
			if self.node_json[each_node]['type'] == 'IP' or  self.node_json[each_node]['type'] == 'Cert':
				if len(self.connect_json[each_node]) > 500:
					reduce_IP_Cert_node.append(each_node)
		for each_node in reduce_IP_Cert_node:
			for each_link in self.connect_json[each_node]:
				if self.node_json[each_link]['type'] == 'Domain':
					if each_link in set(ori_node):
						if len(self.connect_json[each_node]) > 500:
							if random.random() <0.9:
								delete_node.append(each_link)

		
		delete_node = list(set(delete_node))
		#对其中所有domain节点进行随机删减
		# for each_node in ori_node:
		# 	if self.node_json[each_node]['type'] == 'Domain':
		# 		for each_link in self.connect_json[each_node]:
		# 			if self.node_json[each_link]['type'] == 'Domain':
		# 				if each_link in set(ori_node):
		# 					if random.random() <0.9:
		# 						delete_node.append(each_link)
		# 			elif self.node_json[each_link]['type'] == 'IP':
		# 				if each_link in set(ori_node):
		# 					if random.random() <0.4:
		# 						delete_node.append(each_link)

		new_node = []
		for each_node in ori_node:
			if not(each_node in set(delete_node)):
				new_node.append(each_node)
		print("reduce node: ", len(ori_node),"->", len(new_node))
		#对于剩下的节点的连边进行筛选：
		new_link = []
		for each_link in ori_link:
			source = each_link[0]
			target = each_link[1]
			if source in set(new_node) and target in set(new_node):
				new_link.append(each_link)
		#对孤点进行删除
		#建立现存连边涉及点的集合
		link_node_set = []
		for each_link in new_link:
			link_node_set.append(each_link[0])
			link_node_set.append(each_link[1])
		link_node_set = set(link_node_set)
		iso_node = []
		for each_node in new_node:
			if not(each_node in link_node_set):
				iso_node.append(each_node)
		tmp = new_node
		new_node = []
		for each_node in tmp:
			if not(each_node in set(iso_node)):
				new_node.append(each_node)
		print("reduce iso node node: ", len(tmp),"->", len(new_node))
		print("reduce link: ", len(ori_link),"->", len(new_link))

		#保存删减过的点和连边
		dict_json = json.dumps(new_node)
		with open("./reduced_subGraph/node5.json",'w+') as file:
			file.write(dict_json)
		dict_json = json.dumps(new_link)
		with open("./reduced_subGraph/link5.json",'w+') as file:
			file.write(dict_json)

	#统计子图中域名，IP，Cert类型结点的数量
	def statistic_gen(self, node_path):
		with open(node_path, "r") as json_file:
			node = json.load(json_file)
	
		domain_num = 0
		IP_num = 0
		Cert_num = 0
		Whois_Name_num = 0
		Whois_Phone_num = 0
		Whois_Email_num = 0
		IP_C_num= 0
		ASN_num = 0

		for each_node in node:
			if self.node_json[each_node]['type'] == "Domain":
				domain_num += 1
			elif self.node_json[each_node]['type'] == "IP":
				IP_num += 1
			elif self.node_json[each_node]['type'] == "Cert":
				Cert_num += 1
			elif self.node_json[each_node]['type'] == "Whois_Name":
				Whois_Name_num += 1
			elif self.node_json[each_node]['type'] == "Whois_Phone":
				Whois_Phone_num += 1
			elif self.node_json[each_node]['type'] == "Whois_Email":
				Whois_Email_num += 1
			elif self.node_json[each_node]['type'] == "IP_C":
				IP_C_num += 1
			elif self.node_json[each_node]['type'] == "ASN":
				ASN_num += 1

		print("d: ", domain_num)
		print("IP: ", IP_num)
		print("Cert: ", Cert_num)
		print("Whois Name: ", Whois_Name_num)
		print("Whois Phone: ", Whois_Phone_num)
		print("Whois Email: ", Whois_Email_num)
		print("IP_C: ", IP_C_num)
		print("ASN: ", ASN_num)

	def industry_statistic_gen(self, node_path):
		with open(node_path, "r") as json_file:
			node = json.load(json_file)
		
		industry_count = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E':0, 'F':0, 'G':0, 'H': 0, 'I':0 }
		for each_node in node:
			if len(self.node_json[each_node]['industry'])!=0:
				for each_industry in self.node_json[each_node]['industry']:
					old = industry_count[each_industry]
					old += 1
					industry_count[each_industry] = old
		print(industry_count)

if(__name__ == '__main__'):
	t = task1()
	# t.ultra_pruning_three_hop("IP_21ce145cae6730a99300bf677b83bbe430cc0ec957047172e73659372f0031b8")
	#t.subgraph(['Domain_24acfd52f9ceb424d4a2643a832638ce1673b8689fa952d9010dd44949e6b1d9', 'Domain_9c72287c3f9bb38cb0186acf37b7054442b75ac32324dfd245aed46a03026de1', 'Domain_717aa5778731a1f4d6f0218dd3a27b114c839213b4af781427ac1e22dc9a7dea','Domain_8748687a61811032f0ed1dcdb57e01efef9983a6d9c236b82997b07477e66177','Whois_Phone_f4a84443fb72da27731660695dd00877e8ce25b264ec418504fface62cdcbbd7'],'3',3)
	#t.subgraph(['IP_7e730b193c2496fc908086e8c44fc2dbbf7766e599fabde86a4bcb6afdaad66e', 'Cert_6724539e5c0851f37dcf91b7ac85cb35fcd9f8ba4df0107332c308aa53d63bdb'], '4', 3)
	#t.reduce_group4_size()
	#t.subgraph(['Whois_Phone_fd0a3f6712ff520edae7e554cb6dfb4bdd2af1e4a97a39ed9357b31b6888b4af', 'IP_21ce145cae6730a99300bf677b83bbe430cc0ec957047172e73659372f0031b8','Domain_7939d01c5b99c39d2a0f2b418f6060b917804e60c15309811ef4059257c0818a','Domain_587da0bac152713947db682a5443ef639e35f77a3b59e246e8a07c5eccae67e5'], '5', 3)
	#t.reduce_group3_size()
	# t.get_core_asset_node('4')
	#t.get_core_asset_node('3')
	# t.get_core_asset_node('2')
	# t.get_core_asset_node('1')
	t.industry_statistic_gen("./reduced_subGraph/node5.json")
	#t.statistic_gen("./subGraph2/node3.json")

