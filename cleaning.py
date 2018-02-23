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

def write_data_dicts(filename, headers, rows_list_of_dicts):
    with open(filename,'w') as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()
        f_csv.writerows(rows_list_of_dicts)

def cleaning (filename, remove_list, newfile):
	dict_list = get_data_list_of_dicts(filename)
	headers = get_headers(filename)
	(dict_list, headers) = del_column(dict_list, remove_list, headers)
	dict_list = handle_ignore(dict_list, headers)
	dict_list = handle_boolean(dict_list, ["Arrest", "Domestic"])
	(dict_list, headers) = clean_date(dict_list, headers)
	write_data_dicts(newfile, headers, dict_list)

remove_list = {"Primary Type", "Description", "Year", "Location", "X Coordinate", "Y Coordinate", "Latitude", "Longitude"}
cleaning("2002.csv", remove_list, "2002_cleaned.csv")
