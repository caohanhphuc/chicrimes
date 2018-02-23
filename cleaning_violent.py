import csv
import time
import io
import preprocessing

#0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
#"Primary Type", "Description", "Year", "Location"

def get_data_list_of_dicts(filename):
    dict_list = []
    with open(filename) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
        	case_num = row['\xef\xbb\xbfCase Number']
        	del row['\xef\xbb\xbfCase Number']
        	row['Case number'] = case_num
        	dict_list.append(row)
    return dict_list

def get_headers(filename):
    with open(filename) as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
	headers.remove('\xef\xbb\xbfCase Number');
	headers.insert(0, 'Case number')
    return headers

def get_data_slice(column_name, list_of_dicts):
    list = []
    for dict in list_of_dicts:
        list.append(dict[column_name])
    return list

def del_column(dict_list, remove_list, headers):
	for elem in dict_list:
		for column_name in remove_list:
			if column_name in elem:
				del elem[column_name]
	new_headers = list()
	for header in headers:
		if header not in remove_list:
			new_headers.append(header)
	return (dict_list, new_headers)

def clean_date(dict_list, headers):
	for elem in dict_list:
		cur_time = elem["Date"]
		dt = time.strptime(cur_time, "%m/%d/%Y %I:%M:%S %p")
		elem["Hour"] = dt.tm_hour
		elem["Weekday"] = dt.tm_wday
		elem["Monthday"] = dt.tm_mday
		elem["Month"] = dt.tm_mon
		del elem["Date"]
	headers.remove("Date")
	headers.extend(["Hour", "Weekday", "Monthday", "Month"])
	return (dict_list, headers)

def handle_boolean(dict_list, boolean_headers):
	for i in range(0, len(dict_list)):
		for header in boolean_headers:
			if (dict_list[i][header] == "true"):
				dict_list[i][header] = 1
			else:
				dict_list[i][header] = 0
	return dict_list

def handle_ignore(dict_list, header_list): 
    new_dicts = []
    for dicts in dict_list:
        delete = 0
        for header in header_list:
            if dicts[header] == None:
                delete = 1
                break
        if delete == 0:
            new_dicts.append(dicts)
    return new_dicts

def delete_non_index(dict_list, header_list, index_iucr, violent_index_iucr, all_iucr):
	new_dicts = []
	header_list.append("Violent")
	#s = set()
	for d in dict_list:
		iucr = d["IUCR"]
		iucr_str = d["IUCR"]
		if iucr_str[0] == '0':
			iucr_str = iucr_str[1:]
		if iucr in violent_index_iucr or iucr_str in violent_index_iucr:
			d["Violent"] = 0
		elif iucr in index_iucr or iucr_str in index_iucr: 
			d["Violent"] = 1
		elif iucr in all_iucr or iucr_str in all_iucr:
			d["Violent"] = 2
		else:
			if (iucr in {"0840", "0841", "0842", "0843", "0499"}):
				d["Violent"] = 1
			elif (iucr in {"5008", "5005"}):
				d["Violent"] = 2
			else:
				print("Not in list: ")
				print(iucr)
		new_dicts.append(d)
	#print(s)
	return (new_dicts, header_list)

def write_data_dicts(filename, headers, rows_list_of_dicts):
    with open(filename,'w') as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()
        f_csv.writerows(rows_list_of_dicts)

def cleaning (filename, remove_list, newfile, index_iucr, violent_index_iucr, all_iucr):
	dict_list = get_data_list_of_dicts(filename)
	headers = get_headers(filename)
	(dict_list, headers) = del_column(dict_list, remove_list, headers)
	dict_list = handle_ignore(dict_list, headers)
	#dict_list = handle_boolean(dict_list, ["Arrest", "Domestic"])
	(dict_list, headers) = clean_date(dict_list, headers)
	(dict_list, headers) = delete_non_index(dict_list, headers, index_iucr, violent_index_iucr, all_iucr)
	write_data_dicts(newfile, headers, dict_list)

remove_list = {"Primary Type", "Description", "Arrest", "Domestic", "Year", "Location", "X Coordinate", "Y Coordinate", "Latitude", "Longitude"}
all_iucr = {"110", "130", "261", "262", "263", "264", "265", "266", "271", "272", "273", "274", "275", "281", "291", "312", "313", "031A", "031B", "320", "325", "326", "330", "331", "334", "337", "033A", "033B", "340", "041A", "041B", "420", "430", "450", "451", "452", "453", "461", "462", "479", "480", "481", "482", "483", "485", "487", "488", "489", "490", "491", "492", "493", "495", "496", "497", "498", "510", "051A", "051B", "520", "530", "550", "551", "552", "553", "555", "556", "557", "558", "610", "620", "630", "650", "810", "820", "850", "860", "865", "870", "880", "890", "895", "910", "915", "917", "918", "920", "925", "927", "928", "930", "935", "937", "938", "1010", "1020", "1025", "1090", "1753", "1754", "141", "142", "440", "454", "460", "470", "475", "484", "486", "494", "545", "554", "560", "580", "581", "583", "584", "1030", "1035", "1050", "1055", "1110", "1120", "1121", "1122", "1130", "1135", "1140", "1150", "1151", "1152", "1153", "1154", "1155", "1156", "1160", "1170", "1185", "1195", "1200", "1205", "1206", "1210", "1220", "1230", "1235", "1240", "1241", "1242", "1245", "1255", "1260", "1261", "1265", "1305", "1310", "1320", "1330", "1335", "1340", "1345", "1350", "1360", "1365", "1370", "1375", "141A", "141B", "141C", "142A", "142B", "1435", "143A", "143B", "143C", "1440", "1450", "1460", "1475", "1476", "1477", "1478", "1479", "1480", "1481", "1505", "1506", "1507", "1510", "1511", "1512", "1513", "1515", "1520", "1521", "1525", "1526", "1530", "1531", "1535", "1536", "1537", "1540", "1541", "1542", "1544", "1549", "1562", "1563", "1564", "1565", "1566", "1570", "1572", "1574", "1576", "1578", "1580", "1582", "1585", "1590", "1610", "1611", "1620", "1621", "1622", "1623", "1624", "1625", "1626", "1627", "1630", "1631", "1632", "1633", "1640", "1650", "1651", "1661", "1670", "1680", "1681", "1682", "1690", "1691", "1692", "1693", "1694", "1695", "1696", "1697", "1710", "1715", "1720", "1725", "1750", "1751", "1752", "1755", "1775", "1780", "1790", "1791", "1792", "1811", "1812", "1821", "1822", "1840", "1850", "1860", "1900", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029", "2030", "2031", "2032", "2033", "2034", "2040", "2050", "2060", "2070", "2080", "2090", "2091", "2092", "2093", "2094", "2095", "2110", "2111", "2120", "2160", "2170", "2210", "2220", "2230", "2240", "2250", "2251", "2500", "2820", "2825", "2826", "2830", "2840", "2850", "2851", "2860", "2870", "2890", "2895", "2900", "3000", "3100", "3200", "3300", "3400", "3610", "3710", "3720", "3730", "3731", "3740", "3750", "3751", "3760", "3770", "3800", "3910", "3920", "3960", "3966", "3970", "3975", "3980", "4210", "4220", "4230", "4240", "4255", "4310", "4386", "4387", "4388", "4389", "4410", "4420", "4510", "4625", "4650", "4651", "4652", "4740", "4750", "4800", "4810", "4860", "5000", "5001", "5002", "5003", "5004", "5007", "5009", "500E", "500N", "5011", "501A", "501H", "502P", "502R", "502T", "5110", "5111", "5112", "5120", "5121", "5122", "5130", "5131", "5132"};
index_iucr = {"110", "130", "261", "262", "263", "264", "265", "266", "271", "272", "273", "274", "275", "281", "291", "312", "313", "031A", "031B", "320", "325", "326", "330", "331", "334", "337", "033A", "033B", "340", "041A", "041B", "420", "430", "450", "451", "452", "453", "461", "462", "479", "480", "481", "482", "483", "485", "487", "488", "489", "490", "491", "492", "493", "495", "496", "497", "498", "510", "051A", "051B", "520", "530", "550", "551", "552", "553", "555", "556", "557", "558", "610", "620", "630", "650", "810", "820", "850", "860", "865", "870", "880", "890", "895", "910", "915", "917", "918", "920", "925", "927", "928", "930", "935", "937", "938", "1010", "1020", "1025", "1090", "1753", "1754"}
violent_index_iucr = {"110", "130", "261", "262", "263", "264", "265", "266", "271", "272", "273", "274", "275", "281", "291", "1753", "1754", "51A", "51B", "520", "530", "550", "551", "552", "553", "555", "556", "557", "558"};
cleaning("2002.csv", remove_list, "2002_violent_cleaned.csv", index_iucr, violent_index_iucr, all_iucr)
