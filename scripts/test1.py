import numpy as np 
import pandas as pd 
import csv
import io

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn import datasets
from sklearn import preprocessing

_FILEPATH = "2002_cleaned.csv"
_POSTCLEANEDPATH = "2002_postcleaned.csv"

def get_headers(filename):
    with open(filename) as f:
        f_csv = csv.reader(f)
        headers = next(f_csv)
    return headers

def get_data_slice(column_name, list_of_dicts):
    list = []
    for dict in list_of_dicts:
        list.append(dict[column_name])
    return list

def get_data_list_of_dicts(filename):
    dict_list = []
    with open(filename) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
        	dict_list.append(row)
    #print dict_list
    return dict_list

def handle_categorical(dict_list, cat_headers):
	encoders = list()
	for header in cat_headers:
		encoder = preprocessing.LabelEncoder()
		col_data = get_data_slice(header, dict_list)
		encoder.fit(col_data)
		encoders.append(encoder)
		transformed = encoder.transform(col_data)
		for i in range (0, len(dict_list)):
			dict_list[i][header] = transformed[i]
	return (dict_list, encoders)

def split_dataset(data, train_percentage, headers, target_header):
    X_train, X_test, y_train, y_test = train_test_split(data[headers], data[target_header], train_size=train_percentage)
    return X_train, X_test, y_train, y_test

def post_cleaning(dict_list, headers, filename):
	with open(filename,'w') as f:
		f_csv = csv.DictWriter(f, headers)
		f_csv.writeheader()
		f_csv.writerows(dict_list)

def main():
	dict_list = get_data_list_of_dicts(_FILEPATH)
	headers = get_headers(_FILEPATH)
	(dict_list, encoders) = handle_categorical(dict_list, ['Case number', 'IUCR', 'Block', 'Location Description', 'FBI Code'])
	post_cleaning(dict_list, headers, _POSTCLEANEDPATH)

	data = pd.read_csv(_POSTCLEANEDPATH)
	data = data.fillna(0)
	print data.describe()
	
	headers.remove("IUCR")
	X_train, X_test, y_train, y_test = split_dataset(data, 0.8, headers, ["IUCR"])

	print "X_train Shape: ", X_train.shape
	print "y_train Shape: ", y_train.shape
	print "X_test Shape: ", X_test.shape
	print "y_test Shape: ", y_test.shape

	clf = RandomForestClassifier()
	clf.fit(X_train, y_train)
	print("Trained model: ", clf)

	predictions = clf.predict(X_test)

	print "Train Accuracy: ", accuracy_score(y_train, clf.predict(X_train))
	print "Test Accuracy: ", accuracy_score(y_test, predictions)

if __name__ == "__main__":
	main()