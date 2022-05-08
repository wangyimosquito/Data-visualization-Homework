import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt

node_data_path = 'Node.csv'
link_data_path = 'Link.csv'

node_json_path = 'new_node.json'
link_json_path = 'link.json'

IP_industry_json_path = 'IP_Industry.json'
Cert_industry_json_path = 'Cert_Industry.json'

connect_json_path = 'connect.json'

class count:
	def __init__(self):
		self.node_data = pd.read_csv(node_data_path)
		self.link_data = pd.read_csv(link_data_path)
		self.node_data = np.array(self.node_data)
		self.link_data = np.array(self.link_data)

		with open(node_json_path, "r") as json_file:
			self.node_json = json.load(json_file)
		with open(link_json_path, "r") as json_file:
			self.link_json = json.load(json_file)	

	def count_all_illegal_domain(self):
		illegal_num = 0
		count = 0
		for key, value in self.node_json.items():
			if count== 0:
				print(value['industry'])
				print(len(value['industry']))
			count += 1
			if(len(value['industry'])!= 0):
				illegal_num += 1
		print("total illegal domain node num: ", illegal_num)

	def count_diff_industry(self):
		illegal = [0,0,0,0,0,0,0,0,0]
		for key, value in self.node_json.items():
			for every_industry in value['industry']:
				if(every_industry == 'A'):
					illegal[0] += 1
				if(every_industry == 'B'):
					illegal[1] += 1
				if(every_industry == 'C'):
					illegal[2] += 1
				if(every_industry == 'D'):
					illegal[3] += 1
				if(every_industry == 'E'):
					illegal[4] += 1
				if(every_industry == 'F'):
					illegal[5] += 1
				if(every_industry == 'G'):
					illegal[6] += 1
				if(every_industry == 'H'):
					illegal[7] += 1
				if(every_industry == 'I'):
					illegal[8] += 1
		print(illegal)
	
	#统计各个IP涉及的非法产业
	def IP_Cert_json(self):
		IP_json = {}
		Cert_json = {}
		for key, value in self.link_json.items():
			industry = self.node_json[key]['industry']
			if len(industry) != 0:
				for every_tagert_node in value:
					node_type = self.node_json[every_tagert_node]['type']
					if node_type == "IP":
						if every_tagert_node in IP_json:
							old_value = IP_json[every_tagert_node]
							new_value = old_value
							for every_industry in industry:
								#去重
								flag = True
								for every_old_industry in old_value:
									if every_old_industry == every_industry:
										flag = False
										break
								if flag == True:
									new_value.append(every_industry)
							IP_json[every_tagert_node] = new_value
						else:
							IP_json[every_tagert_node] = industry
					elif node_type == "Cert":
						if every_tagert_node in Cert_json:
							old_value = Cert_json[every_tagert_node]
							new_value = old_value
							for every_industry in industry:
								#去重
								flag = True
								for every_old_industry in old_value:
									if every_old_industry == every_industry:
										flag = False
										break
								if flag == True:
									new_value.append(every_industry)
							Cert_json[every_tagert_node] = new_value
						else:
							Cert_json[every_tagert_node] = industry
		dict_json = json.dumps(IP_json)
		with open(IP_industry_json_path,'w+') as file:
			file.write(dict_json)
		dict_json = json.dumps(Cert_json)
		with open(Cert_industry_json_path,'w+') as file:
			file.write(dict_json)


	def count_total_IP_Cert(self):
		IP_num = 0
		Cert_num = 0
		for key, value in self.node_json.items():
			if value['type'] == "IP":
				IP_num += 1
			elif value['type'] == "Cert":
				Cert_num += 1
		print("IP num: ", IP_num)
		print("Cert num: ", Cert_num)
	
	def illegal_distribution(self):
		with open(IP_industry_json_path, "r") as json_file:
			ip = json.load(json_file)
		with open(Cert_industry_json_path, "r") as json_file:
			cert = json.load(json_file)
		print("dirty ip: ", len(ip))
		print("dirty cert: ", len(cert))
		#计算所有脏Cert涉及的非法产业分布
		num = [0,0,0,0,0,0,0,0,0]
		for key, value in cert.items():
			num[len(value)-1] += 1
		print("distribution of illegal industry num: ", num)

	def degree_distribution(self):
		node_degree = {}
		for key,value in self.node_json.items():
			node_degree[key] = 0
		
		for key, value in self.link_json.items():
			old = node_degree[key]
			node_degree[key] = old+1
			for each_target in value:
				old = node_degree[each_target]
				node_degree[each_target] = old + 1
		
		degree = {}
		for value in node_degree.values():
			if value in degree:
				old = degree[value]
				degree[value] = old+1
			else:
				degree[value] = 1
		
		#数据分布可视化
		
		x_data = []
		y_data = []
		for key,value in degree.items():
			x_data.append(int(key))
			y_data.append(int(value))
		# print(x_data)
		# print(y_data)
		plt.scatter(x_data, y_data)
		plt.show()
	
	def test(self):
		with open(connect_json_path, "r") as json_file:
			connect = json.load(json_file)
		for key,value in connect.items():
			print(key)
			print(value)
			break

if(__name__ == '__main__'):
	C = count()
	C.test()