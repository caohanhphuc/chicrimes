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

def delete_non_index(dict_list, header_list, index_iucr, violent_index_iucr):
	new_dicts = []
	header_list.append("Violent")
	for d in dict_list:
		if d["IUCR"] in index_iucr:
			new_dicts.append(d)
			if d["IUCR"] in violent_index_iucr:
				d["Violent"] = 1
			else:
				d["Violent"] = 0
	return (new_dicts, header_list)

def write_data_dicts(filename, headers, rows_list_of_dicts):
    with open(filename,'w') as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()
        f_csv.writerows(rows_list_of_dicts)

def cleaning (filename, remove_list, newfile, index_iucr, violent_index_iucr):
	dict_list = get_data_list_of_dicts(filename)
	headers = get_headers(filename)
	(dict_list, headers) = del_column(dict_list, remove_list, headers)
	dict_list = handle_ignore(dict_list, headers)
	#dict_list = handle_boolean(dict_list, ["Arrest", "Domestic"])
	(dict_list, headers) = clean_date(dict_list, headers)
	(dict_list, headers) = delete_non_index(dict_list, headers, index_iucr, violent_index_iucr)
	write_data_dicts(newfile, headers, dict_list)

remove_list = {"Primary Type", "Description", "Arrest", "Domestic", "Year", "Location", "X Coordinate", "Y Coordinate", "Latitude", "Longitude"}
index_iucr = {"110", "130", "261", "262", "263", "264", "265", "266", "271", "272", "273", "274", "275", "281", "291", "312", "313", "031A", "031B", "320", "325", "326", "330", "331", "334", "337", "033A", "033B", "340", "041A", "041B", "420", "430", "450", "451", "452", "453", "461", "462", "479", "480", "481", "482", "483", "485", "487", "488", "489", "490", "491", "492", "493", "495", "496", "497", "498", "510", "051A", "051B", "520", "530", "550", "551", "552", "553", "555", "556", "557", "558", "610", "620", "630", "650", "810", "820", "850", "860", "865", "870", "880", "890", "895", "910", "915", "917", "918", "920", "925", "927", "928", "930", "935", "937", "938", "1010", "1020", "1025", "1090", "1753", "1754"}
violent_index_iucr = {"110", "130", "261", "262", "263", "264", "265", "266", "271", "272", "273", "274", "275", "281", "291", "1753", "1754", "51A", "51B", "520", "530", "550", "551", "552", "553", "555", "556", "557", "558"};
cleaning("2002.csv", remove_list, "2002_violent_cleaned.csv", index_iucr, violent_index_iucr)
