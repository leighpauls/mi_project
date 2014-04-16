#!/usr/bin/env python
import sys
import json

PUNCTUATION = ''.join([chr(x) for x in xrange(ord('!'), ord('@')+1)])

def string_to_word_set(raw_string):
    """Get the set of words used in raw_string"""
    words = set()
    for word in raw_string.split():
        # remove any punctuation
        word = word.translate(None, PUNCTUATION)
        if len(word) == 0:
            continue
        words.add(word)
    return words

def strings_to_word_sets(strings):
    """Get the all of the words used in the strings
    return (all_words_usage, [words_used])"""
    word_set = set()
    line_word_sets = []
    for string in strings:
        line_word_set = string_to_word_set(string)
        word_set.update(line_word_set)
        line_word_sets.append(line_word_set)
    return (word_set, line_word_sets)

def twss_json_to_word_usage(json_file):
    with open(json_file, "r") as f:
        data = json.loads(f.read())

    # filter the list into the actual TWSS strings
    raw_twss_list = data["results"]["TWSS"]
    filtered_twss_list = []
    for raw_twss in raw_twss_list:
        story_string = raw_twss["TWSS"]
        if story_string.count("\"") != 2:
            # don't have a quote to use
            continue
        try:
            clipped_string = str(story_string[
                story_string.index("\"") + 1
                : story_string.rindex("\"")]).lower()
        except UnicodeEncodeError:
            # bad char in the string
            continue
        filtered_twss_list.append(clipped_string)
    return strings_to_word_sets(filtered_twss_list)

def tfln_json_to_word_usage(json_file):
    with open(json_file, "r") as f:
        data = json.loads(f.read())
    # filter the strings
    tfln_list = []
    for tfln_entry in data["results"]["TFLN"]:
        try:
            filtered_string = str(tfln_entry["TFLN"]["text"]).lower()
        except UnicodeEncodeError:
            # bad char in the string
            continue
        tfln_list.append(filtered_string)
    return strings_to_word_sets(tfln_list)

if __name__=='__main__':
    if len(sys.argv) != 4:
        print "usage:", sys.argv[0], \
            '<twss-json-file> <tfln-json-file> <output-csv-file>'
        exit(-1)
    all_twss_words, twss_word_sets = twss_json_to_word_usage(sys.argv[1])
    all_tfln_words, tfln_word_sets = tfln_json_to_word_usage(sys.argv[2])

    ordered_words = sorted(all_twss_words | all_tfln_words)
    # make a dict of ordered words to word index
    word_idx_lookup = {}
    for i in xrange(len(ordered_words)):
        word_idx_lookup[ordered_words[i]] = i

    twss_word_usages = [
        sorted([word_idx_lookup[word] for word in word_set])
        for word_set in twss_word_sets]
    tfln_word_usages = [
        sorted([word_idx_lookup[word] for word in word_set])
        for word_set in tfln_word_sets]

    with open(sys.argv[3], "w") as f:
        def print_line(line, value):
            num_written = 0
            next_idx = 0
            for active_idx in line:
                # print 0's for unused space
                f.write("0," * (active_idx - next_idx))
                # print a 1 for this space
                f.write("1,")
                next_idx = active_idx + 1
                num_written += (active_idx - next_idx) + 1
            # fill in the remaining 0's
            f.write("0," * (len(ordered_words) - next_idx))
            # write the value
            f.write(value + "\n")

        # print the title line
        for word in ordered_words:
            f.write("'" + word + "',")
        f.write("'IS_TWSS'\n")
        # print the TWSS's
        for line in twss_word_usages:
            print_line(line, "1")

        # print the TFLN's
        for line in tfln_word_usages:
            print_line(line, "0")

