#!/usr/bin/env python

import json_to_training_grid as j2t
import sys, random
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier

TRAINING_RATIO = 0.7

if __name__=='__main__':
    if len(sys.argv) != 4:
        print "usage:", sys.argv[0], \
            '<twss-json-file> <tfln-json-file> <output-csv'
        exit(-1)
    all_twss_words, twss_word_sets = j2t.twss_json_to_word_usage(sys.argv[1])
    all_tfln_words, tfln_word_sets = j2t.tfln_json_to_word_usage(sys.argv[2])

    all_words = all_twss_words | all_tfln_words
    all_word_sets = twss_word_sets + tfln_word_sets

    # break each wordset into arrays of attributes
    ordered_words = sorted(all_words)
    training_inputs = []
    training_outputs = []
    testing_inputs = []
    testing_outputs = []
    testing_sources = []

    random.seed(0)
    for word_sets, output in [(twss_word_sets, 1), (tfln_word_sets, 0)]:
        for word_set in word_sets:
            attribute_row = []
            for word in all_words:
                attribute_row.append(1 if (word in word_set.words) else 0)

            if random.random() < TRAINING_RATIO:
                training_inputs.append(attribute_row)
                training_outputs.append(output)
            else:
                testing_inputs.append(attribute_row)
                testing_outputs.append(output)
                testing_sources.append(word_set.text)

    # print 'training:', len(training_inputs), 'testing:', len(testing_inputs)

    results = []
    for max_features in [1, 5, 10, 15, 20, 30, 50]:
        # clf = RandomForestClassifier(n_estimators=200, n_jobs=7)
        n_estimators = 100
        # max_features = 12
        clf = ExtraTreesClassifier(
            n_jobs=6,
            n_estimators=n_estimators,
            max_features=max_features)
        # print "n_estimators: ", n_estimators
        # print "max_features: ", max_features

        clf.fit(training_inputs, training_outputs)
        predicted_outputs = clf.predict(testing_inputs)
        probs = clf.predict_proba(testing_inputs)

        # print "'threshold','recall','precision'"
        # clf = tree.DecisionTreeClassifier()
        estimator_result = {}
        estimator_result["line"] = []
        estimator_result["max_features"] = max_features
        for THRESHOLD in (x * 0.05 for x in xrange(1, 20)):
            cm = [[0, 0], [0, 0]];
            # THRESHOLD = 0.7
            for i in xrange(len(testing_outputs)):
                prediction = 1 if probs[i][1] > THRESHOLD else 0
                cm[testing_outputs[i]][prediction] += 1
            result = {}
            result["threshold"] = THRESHOLD
            result["precision"] = (float(cm[1][1]) / float(cm[0][1] + cm[1][1]))
            result["recall"] = (float(cm[1][1]) / float(cm[1][0] + cm[1][1]))
            estimator_result["line"].append(result)
        results.append(estimator_result)


    with open(sys.argv[3], "w") as f:
        # print the title line
        for estimator_result in results:
            base_string = 'res_' + str(estimator_result["max_features"]) + "_features_"
            f.write(base_string + "recall,")
            f.write(base_string + "precision,")
        f.write("\n")

        # write the results
        for i in xrange(len(results[0]["line"])):
            for estimator_result in results:
                f.write(str(estimator_result["line"][i]["recall"]) + ",")
                f.write(str(estimator_result["line"][i]["precision"]) + ",")
            f.write("\n")
