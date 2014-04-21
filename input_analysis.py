#!/usr/bin/env python

import json_to_training_grid as j2t
import sys

if __name__=='__main__':
    if len(sys.argv) != 3:
        print "usage:", sys.argv[0], \
            '<twss-json-file> <tfln-json-file>'
        exit(-1)
    all_twss_words, twss_word_sets = j2t.twss_json_to_word_usage(sys.argv[1])
    all_tfln_words, tfln_word_sets = j2t.tfln_json_to_word_usage(sys.argv[2])

    all_words = all_twss_words | all_tfln_words
    all_word_sets = twss_word_sets + tfln_word_sets

    # find each word's frequency
    word_frequency = {}
    for word_set in all_word_sets:
        for word in word_set:
            if word in word_frequency:
                word_frequency[word] += 1
            else:
                word_frequency[word] = 1

    # invert the word frequencies to sort
    freq_buckets = {}
    for word, freq in word_frequency.iteritems():
        if freq in freq_buckets:
            freq_buckets[freq].append(word)
        else:
            freq_buckets[freq] = [word]

    # find the common words
    items = freq_buckets.items()
    items.reverse()
    common_words = set()
    for frequency, words in items:
        if frequency < 10:
            break
        common_words.update(words)

    # find which records contain each word
    word_usage_mapping = {}
    for i in xrange(len(all_word_sets)):
        for word in all_word_sets[i] & common_words:
            if word in word_usage_mapping:
                word_usage_mapping[word].add(i)
            else:
                word_usage_mapping[word] = set([i])

    # find out how often words are used together
    word_pairing_frequencies = {}
    for word, usages in word_usage_mapping.iteritems():
        word_pairings = {}
        for other_word, other_usages in word_usage_mapping.iteritems():
            # don't compare to self
            if word == other_word:
                continue
            num_pairings = len(usages & other_usages)
            # don't remember non-pairings
            if num_pairings == 0:
                continue
            word_pairings[other_word] = num_pairings
        word_pairing_frequencies[word] = word_pairings

    print word_pairing_frequencies
