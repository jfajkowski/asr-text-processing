#!/usr/bin/python3

import argparse
import logging
import random


def parse_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument('-f', '--file', dest='files', action='append', nargs=2, metavar=('CORPUS', 'RATIO'), default=[])
    group.add_argument('-b', '--bytes', dest='bytes', type=int)
    group.add_argument('-c', '--chars', dest='chars', type=int)
    group.add_argument('-l', '--lines', dest='lines', type=int)
    group.add_argument('-w', '--words', dest='words', type=int)
    return parser.parse_args()


def normalize(files):
    normalized = []
    ratio_sum = sum([float(i[1]) for i in files])
    for corpus, ratio in files:
        normalized.append((corpus, float(ratio) / ratio_sum))
    return normalized


def mix(files, max_count, count_method):
    count = 0
    results = []
    logging.info('Selecting ~{} {}'.format(max_count, count_method_unit(count_method)))
    for corpus, ratio in files:
        max_corpus_count = int(max_count * ratio)
        corpus_count = select_from_corpus(corpus, max_corpus_count, count_method)
        count += corpus_count
        results.append((corpus, corpus_count))
    logging.info('Selected ~{} {}'.format(count, count_method_unit(count_method)))
    return results


def select_from_corpus(corpus, max_corpus_count, count_method):
    iteration = 0
    corpus_count = 0
    logging.info('Selecting ~{} {} from {}'.format(max_corpus_count, count_method_unit(count_method), corpus))
    while corpus_count < max_corpus_count:
        with open(corpus, encoding='UTF-8') as c_in:
            lines, iteration_count = random_lines(c_in, max_corpus_count - corpus_count, count_method)
            for line in lines:
                print(line.rstrip('\n'))
            iteration += 1
            corpus_count += iteration_count
    logging.info(
        'Selected {} {} from {} in {} iteration(s)'.format(corpus_count, count_method_unit(count_method),
                                                           corpus, iteration))
    return corpus_count


def random_lines(file, max_count, count_method):
    count = 0
    selected = []
    for i, line in enumerate(file):
        if count < max_count:
            selected.append(line)
            count += count_method(line)
        else:
            m = random.randint(0, i)
            if m < len(selected):
                count -= count_method(selected[m])
                selected[m] = line
                count += count_method(selected[m])
    return selected, count


def count_bytes(line):
    return len(line.encode('UTF-8'))


def count_chars(line):
    return len(line)


def count_lines(line):
    return 1 if line else 0


def count_words(line):
    return len(line.split(' '))


def count_method_unit(count_method):
    return count_method.__name__.replace('count_', '')


def main():
    logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(name)s: %(message)s', level=logging.INFO)
    args = parse_args()
    files = normalize(args.files)
    logging.info('Desired ratio: {}'.format(','.join([str(f) for f in files])))
    if args.bytes:
        files = mix(files, args.bytes, count_bytes)
    elif args.chars:
        files = mix(files, args.chars, count_chars)
    elif args.lines:
        files = mix(files, args.lines, count_lines)
    elif args.words:
        files = mix(files, args.words, count_words)
    files = normalize(files)
    logging.info('Achieved ratio: {}'.format(','.join([str(f) for f in files])))


if __name__ == '__main__':
    main()
