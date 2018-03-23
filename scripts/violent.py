import numpy as np 
import pandas as pd 
import csv
import io
import matplotlib.pyplot as plt
#import seaborn as sns; sns.set()

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn import datasets
from sklearn import preprocessing
from sklearn import tree

_YEAR = "2003"
_FILE2002 = "../data/2002_violent_cleaned.csv"
_POSTCLEANED2002 = "../data/2002_violent_postcleaned.csv"
_FILETEST = "../data/" + _YEAR + "_violent_cleaned.csv"
_POSTCLEANEDTEST = "../data/" + _YEAR + "_violent_postcleaned.csv"

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

def visualize_classifier(classifier, X, y):
    # Define the minimum and maximum values for X and Y
    # that will be used in the mesh grid
    min_x, max_x = X.iloc[:, 0].min() - 1.0, X.iloc[:, 0].max() + 1.0
    min_y, max_y = X.iloc[:, 1].min() - 1.0, X.iloc[:, 1].max() + 1.0

    # Define the step size to use in plotting the mesh grid 
    mesh_step_size = 0.01

    # Define the mesh grid of X and Y values
    x_vals, y_vals = np.meshgrid(np.arange(min_x, max_x, mesh_step_size), np.arange(min_y, max_y, mesh_step_size))

    # Run the classifier on the mesh grid
    output = classifier.predict(np.c_[x_vals.ravel(), y_vals.ravel()])

    # Reshape the output array
    output = output.reshape(x_vals.shape)

    # Create a plot
    plt.figure()

    # Choose a color scheme for the plot 
    plt.pcolormesh(x_vals, y_vals, output, cmap=plt.cm.gray)

    # Overlay the training points on the plot 
    plt.scatter(X.iloc[:, 0], X.iloc[:, 1], c=y, s=75, edgecolors='black', linewidth=1, cmap=plt.cm.Paired)

    # Specify the boundaries of the plot
    plt.xlim(x_vals.min(), x_vals.max())
    plt.ylim(y_vals.min(), y_vals.max())

    # Specify the ticks on the X and Y axes
    plt.xticks((np.arange(int(X.iloc[:, 0].min() - 1), int(X.iloc[:, 0].max() + 1), 1.0)))
    plt.yticks((np.arange(int(X.iloc[:, 1].min() - 1), int(X.iloc[:, 1].max() + 1), 1.0)))

    plt.show()


def main():
	dict_list = get_data_list_of_dicts(_FILE2002)
	headers = get_headers(_FILE2002)
	(dict_list, encoders) = handle_categorical(dict_list, ['Block', 'Location Description'])
	post_cleaning(dict_list, headers, _POSTCLEANED2002)

	data = pd.read_csv(_POSTCLEANED2002)
	data = data.fillna(0)
	#print data.describe()
	
	headers.remove("Violent")
	X_train, X_test, y_train, y_test = split_dataset(data, 0.8, headers, ["Violent"])

	'''
	print "X_train Shape: ", X_train.shape
	print "y_train Shape: ", y_train.shape
	print "X_test Shape: ", X_test.shape
	print "y_test Shape: ", y_test.shape
	'''

	##################################################################
	#testing using _YEAR
	dict_list_test = get_data_list_of_dicts(_FILETEST)
	headers_test = get_headers(_FILETEST)
	(dict_list_test, encoders_test) = handle_categorical(dict_list_test, ['Block', 'Location Description'])
	post_cleaning(dict_list_test, headers_test, _POSTCLEANEDTEST)

	data_test = pd.read_csv(_POSTCLEANEDTEST)
	headers_test.remove("Violent")
	X_train_test, X_test_test, y_train_test, y_test_test = split_dataset(data, 0.0, headers, ["Violent"])
	##################################################################

	#depth_train_test2002_test2003 = dict()

	for i in range (1, 2):
		clf = RandomForestClassifier(oob_score=True, max_depth = i, random_state=0)
		clf.fit(X_train, y_train)
		print("Max depth:", clf.max_depth)

		##################################################################
		#prediction for _YEAR
		predictions_test = clf.predict(X_test_test)
		arr_y_test_test = np.ravel(y_test_test)
		arr_predictions_test = np.ravel(predictions_test)
		test_20xx = accuracy_score(y_test_test, predictions_test)
		print "Test Accuracy ", _YEAR, ": ", test_20xx

		#visualize_classifier(clf, X_train, y_train);

		cfs_matrix_test = confusion_matrix(y_test_test, predictions_test, labels=[0, 1, 2])
		print cfs_matrix_test
		
		##################################################################

		index = 0
		'''
		for tree_ in clf.estimators_:
			if (index > 1):
				break;
			with open('../visuals/depth=10_tree_' + str(index) + '.dot', 'w') as visual:
				visual = tree.export_graphviz(tree_, out_file = visual)
			index = index + 1
		'''

		importances = clf.feature_importances_
		indices = np.argsort(importances)

		for f in range(X_train.shape[1]):
			print("%d. feature %s (%f)" % (f + 1, headers[indices[f]], importances[indices[f]]))
		
		#print("Trained model: ", clf)

		predictions = clf.predict(X_test)

		train_2002 = accuracy_score(y_train, clf.predict(X_train))
		test_2002 = accuracy_score(y_test, predictions)
		print "Train Accuracy 2002: ", train_2002
		print "Test Accuracy 2002: ", test_2002

		#depth_train_test2002_test2003[i] = (train_2002, test_2002, test_20xx)
		mat = confusion_matrix(y_test, predictions, labels=[0, 1, 2])
		print mat

	#with open("depth_accuracy.txt",'w') as f:
	#	for key, val in depth_train_test2002_test2003.items():
	#		row_text = str(key) + "\t" + str(val[0]) + "\t" + str(val[1]) + "\t" + str(val[2]) + "\n"
	#		f.write(row_text)
if __name__ == "__main__":
	main()