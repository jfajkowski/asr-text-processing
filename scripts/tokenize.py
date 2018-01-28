#!/usr/bin/python3

import argparse
import re
import sys
from abc import ABC, abstractmethod


class Tokenizer(ABC):
    @abstractmethod
    def tokenize(self, text):
        pass


class UniversalTokenizer(Tokenizer):
    PATTERN = re.compile(r'[^\w]')

    def tokenize(self, text):
        return UniversalTokenizer.PATTERN.sub(' ', text).split()


LANGUAGE_MAP = {
    'pl': UniversalTokenizer()
}
LANGUAGE_PATTERN = '[a-z]{2}'


def parse_args():
    parser = argparse.ArgumentParser(description='a pipe tool to extract single words from sentences')
    parser.add_argument('locale', metavar='LOCALE')
    parser.add_argument('files', metavar='FILES', nargs='*', default='-')
    return parser.parse_args()


def load_tokenizer(locale):
    language_short = re.match(LANGUAGE_PATTERN, locale).group()
    if language_short not in LANGUAGE_MAP:
        raise argparse.ArgumentTypeError('"{}" is invalid or not supported locale.'.format(locale))
    return LANGUAGE_MAP[language_short]


def tokenize(files, tokenizer):
    words = set()
    for file in files:
        with sys.stdin if file == '-' else open(file) as f_in:
            for line in f_in:
                utterance = line.rstrip('\n')
                utterance_words = tokenizer.tokenize(utterance)
                words.update(set(utterance_words))
    return words


def print_words(words):
    for word in sorted(words):
        print(word)


def main():
    args = parse_args()
    tokenizer = load_tokenizer(args.locale)
    words = tokenize(args.files, tokenizer)
    print_words(words)


if __name__ == '__main__':
    main()
