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
			curr_hop_node = [init_node]
			#循环
			for i in range(hop_num):
				last_hop_node = curr_hop_node
				curr_hop_node = []
				for each_node in last_hop_node:
					for i in self.connect_json[each_node]:
						node.append(i)
						if each_node+i in self.link_type_json:
								link_type = self.link_type_json[each_node+i]
						else:
							link_type = self.link_type_json[i+each_node]
						link.append([each_node, i, link_type])
						#通过连边强度筛选参与下一轮挖掘的节点
						if(link_type == 'r_cert' or link_type == 'r_dns_a' or link_type == 'r_subdomain' or link_type == 'r_request_jump' or link_type == 'r_whois_name' or link_type == 'r_whois_email' or link_type == 'r_whois_phone'):
							curr_hop_node.append(i)
			
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

	def link_reduce_redundency(self, subgraph_link_json):
		#获取连边
		#连边去重复
		print("before reduce: ", len(subgraph_link_json))
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
		print("after reduce: ", len(link))
		return link

#多线索集合挖掘函数
	def subgraph(self, init_node_list, group_name):
		node = []
		link = []
		clue_num = 1
		for each_clue in init_node_list:
			node_tmp, link_tmp = self.any_hop(each_clue, '_'+group_name+'_'+str(clue_num),2)
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

if(__name__ == '__main__'):
	t = task1()
	# t.ultra_pruning_three_hop("IP_21ce145cae6730a99300bf677b83bbe430cc0ec957047172e73659372f0031b8")
	t.subgraph(['Domain_24acfd52f9ceb424d4a2643a832638ce1673b8689fa952d9010dd44949e6b1d9','Domain_9c72287c3f9bb38cb0186acf37b7054442b75ac32324dfd245aed46a03026de1','Domain_717aa5778731a1f4d6f0218dd3a27b114c839213b4af781427ac1e22dc9a7dea','Domain_8748687a61811032f0ed1dcdb57e01efef9983a6d9c236b82997b07477e66177','Whois_Phone_f4a84443fb72da27731660695dd00877e8ce25b264ec418504fface62cdcbbd7'],'3' )
	
	t.statistic_gen("./subGraph2/node3.json")
	# t.statistic_gen("./reduced_subGraph/node2.json")
	#t.any_hop('Domain_c58c149eec59bb14b0c102a0f303d4c20366926b5c3206555d2937474124beb9', 'test', 3)