#!/usr/bin/env python

import json_to_training_grid as j2t
import sys, random
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier

TRAINING_RATIO = 0.7

if __name__=='__main__':
    if len(sys.argv) != 3:
        print "usage:", sys.argv[0], \
            '<twss-json-file> <tfln-json-file>'
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

    clf = RandomForestClassifier(n_estimators=200, n_jobs=7)
    # n_estimators = 470
    # max_features = 2
    # clf = ExtraTreesClassifier(
    #     n_jobs=6,
    #     n_estimators=n_estimators,
    #     max_features=max_features)
    # print "n_estimators: ", n_estimators
    # print "max_features: ", max_features

    clf.fit(training_inputs, training_outputs)
    predicted_outputs = clf.predict(testing_inputs)
    probs = clf.predict_proba(testing_inputs)

    print "'threshold','precision','recall'"
    # clf = tree.DecisionTreeClassifier()
    for THRESHOLD in xrange(0.1, 0.9, 0.05):

        cm = [[0, 0], [0, 0]];
        # THRESHOLD = 0.7
        for i in xrange(len(testing_outputs)):
            prediction = 1 if probs[i][1] > THRESHOLD else 0
            cm[testing_outputs[i]][prediction] += 1

        print cm
        print THRESHOLD, ",", \
            (float(cm[1][1]) / float(cm[0][1] + cm[1][1])), ",", \
            (float(cm[1][1]) / float(cm[1][0] + cm[1][1]))
        # print "Precision:", (float(cm[1][1]) / float(cm[0][1] + cm[1][1]))
        # print "Recall:", (float(cm[1][1]) / float(cm[1][0] + cm[1][1]))
