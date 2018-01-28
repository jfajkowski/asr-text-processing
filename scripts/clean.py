#!/usr/bin/python3

import argparse
import os
import re
import sys
import yaml
from abc import ABC, abstractmethod


LOCALE_YML = os.path.dirname(os.path.realpath(__file__)) + '/locale.yml'


class Cleaner(ABC):
    @abstractmethod
    def clean(self, text):
        pass


class HyperlinksCleaner(Cleaner):
    PATTERN = '(?:https?:\/\/)(?:www)?\.?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?'

    def __init__(self):
        self.regex = re.compile(HyperlinksCleaner.PATTERN)

    def clean(self, text):
        if None in self.regex.split(text):
            print(text)
        return ' '.join(self.regex.split(text))


class EmoticonsCleaner(Cleaner):
    SIDEWAYS = [r'[;:xX][-]?[dDoOsSpP]+?']
    UPRIGHT = [r'[*;^][_,][*;^]']

    def __init__(self):
        self.sideways_regex = re.compile(r'\b' + r'\b|\b'.join(EmoticonsCleaner.SIDEWAYS) + r'\b|'
                                         r'' + r'|\b'.join(EmoticonsCleaner.SIDEWAYS) + r'\b')
        self.upright_regex = re.compile(r'\b' + r'\b|\b'.join(EmoticonsCleaner.UPRIGHT) + r'\b|'
                                        r'' + r'|\b'.join(EmoticonsCleaner.UPRIGHT) + r'\b')

    def clean(self, text):
        text = self.sideways_regex.sub(' ', text)
        text = self.upright_regex.sub(' ', text)
        return text


class AlphanumericCleaner(Cleaner):
    SPLIT_PATTERN = r'(\W+)'

    def __init__(self):
        self.regex = re.compile(AlphanumericCleaner.SPLIT_PATTERN)

    def clean(self, text):
        words = self.regex.split(text)
        filtered = filter(lambda w: w.isalnum() and (w.isalpha() or w.isnumeric()), words)
        return ' '.join(filtered)


class CharacterCleaner(Cleaner):
    def __init__(self, characters):
        self.regex = re.compile(r'[^' + characters + ']')

    def clean(self, text):
        return self.regex.sub(' ', text)


class SeparatorCleaner(Cleaner):
    def __init__(self, separators):
        self.separators = separators
        self.regex = re.compile(r'[' + separators + ']+')

    def clean(self, text):
        return self.regex.sub(' ', text).strip(self.separators)


class TyposCleaner(Cleaner):
    MAX_IN_ROW = 3

    def clean(self, text):
        cleaned = ''
        prev_letter = ''
        buffer = ''
        for curr_letter in text:
            if curr_letter != prev_letter:
                cleaned += buffer if len(buffer) <= TyposCleaner.MAX_IN_ROW else prev_letter
                buffer = ''
            buffer += curr_letter
            prev_letter = curr_letter
        cleaned += buffer if len(buffer) < TyposCleaner.MAX_IN_ROW else prev_letter
        return cleaned


def parse_args():
    parser = argparse.ArgumentParser(description='filters characters that are out of whitelist')
    parser.add_argument('locale', metavar='LOCALE', default='pl-PL')
    parser.add_argument('files', metavar='FILES', default='-', nargs='*')
    parser.add_argument('-d', '--delimiter', dest='delimiter', type=str, default='\t')
    parser.add_argument('-f', '--field', dest='field', type=int, default=1)
    return parser.parse_args()


def clean(files, locale, delimiter='\t', field=1, locale_yml=LOCALE_YML):
        characters, separators = read_locale_config(locale, locale_yml)
        pipeline = [
            HyperlinksCleaner(),
            EmoticonsCleaner(),
            AlphanumericCleaner(),
            CharacterCleaner(characters),
            SeparatorCleaner(separators),
            TyposCleaner()
        ]

        for file in files:
            with sys.stdin if file == '-' else open(file) as f_in:
                for line in f_in:
                    line = line.rstrip('\n').split(delimiter)
                    for cleaner in pipeline:
                        line[field - 1] = cleaner.clean(line[field - 1])
                    line = delimiter.join(line)
                    print(line)


def read_locale_config(locale, locale_yml):
    with open(locale_yml) as c_in:
        config = yaml.load(c_in)
    language_code = re.search('[a-z]{2}', locale)[0]
    region_code = re.search('[A-Z]{2}', locale)[0]
    characters = config[language_code][region_code]['characters']
    separators = config[language_code][region_code]['separators']
    return characters, separators


def main():
    args = parse_args()
    clean(args.files, args.locale, args.delimiter, args.field)


if __name__ == '__main__':
    main()
