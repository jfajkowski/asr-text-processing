#!/usr/bin/python3
import argparse
import re
import sys
from abc import ABC, abstractmethod


class Tidier(ABC):
    @abstractmethod
    def apply(self, text):
        pass


class JavaScriptTidier(Tidier):
    KEYWORDS = ['$(document)']

    def apply(self, text):
        for keyword in JavaScriptTidier.KEYWORDS:
            if keyword in text:
                return ''
        else:
            return text


class MarkupTidier(Tidier):
    BEGIN = r'[\[<].+?[\]>]'
    END = r'[\[<]\/.+?[\]>]'
    PATTERN = BEGIN + '.+?' + END + '|' + BEGIN + '|' + END

    def __init__(self):
        self.regex = re.compile(MarkupTidier.PATTERN)

    def apply(self, text):
        return self.regex.sub(' ', text)


class CharacterTidier(Tidier):
    CHARACTERS = '\u00A0\t'
    PATTERN = r'[' + CHARACTERS + ']'

    def __init__(self):
        self.regex = re.compile(CharacterTidier.PATTERN)

    def apply(self, text):
        return self.regex.sub(' ', text)


class AsciiArtTidier(Tidier):
    BARS = '-_*# '
    PATTERN = r'[' + BARS + ']{2,}'

    def __init__(self):
        self.regex = re.compile(AsciiArtTidier.PATTERN)

    def apply(self, text):
        return self.regex.sub(' ', text)


class TrailingTidier():
    CHARACTERS = ' '

    def apply(self, text):
        return text.strip(' ')


class UniqueTidier(Tidier):
    def __init__(self):
        self._lines = set()

    def apply(self, text):
        if text not in self._lines:
            self._lines.add(text)
            return text
        else:
            return ''


def parse_args():
    parser = argparse.ArgumentParser(description='filters characters that are out of whitelist')
    parser.add_argument('files', metavar='FILES', default='-', nargs='*')
    return parser.parse_args()


def tidy(files):
    pipeline = [
        JavaScriptTidier(),
        MarkupTidier(),
        CharacterTidier(),
        AsciiArtTidier(),
        TrailingTidier(),
        UniqueTidier()
    ]

    for file in files:
        with sys.stdin if file == '-' else open(file) as f_in:
            for line in f_in:
                line = line.rstrip('\n')
                for tidier in pipeline:
                    line = tidier.apply(line)
                if line:
                    print(line)


def main():
    args = parse_args()
    tidy(args.files)


if __name__ == '__main__':
    main()
