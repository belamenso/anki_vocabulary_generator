import io
import re
import genanki
import urllib.error
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlencode

from debug_utils import header, nab


def encode(word):
    return urlencode({'': word})[1:]


def fetch_html(url):
    connection = urllib.request.urlopen(url)
    ret = connection.read().decode('utf-8')
    connection.close()
    return ret


def clean_up(text):
    return re.sub(r'\n\s+\n', '\n',
                  re.sub(r'^ +$', '',
                         re.sub(r'\n+', '\n', text, 999999), 9999),
                  99999).strip()


class DefinitionFetcher:

    class NoDefinition(Exception):
        pass

    @staticmethod
    def definition(word):
        pass


class BabLaFetcher(DefinitionFetcher):
    @staticmethod
    def html_to_card_text(html_data):
        b = BeautifulSoup(html_data, 'html.parser')
        out_text = []
        for result in b.select_one('.quick-results.container').select('.quick-result-overview'):
            out_text.append('\n'.join(result.getText().strip().split('\n\n')[1:]))
        return '\n'.join(out_text)

    @staticmethod
    def definition(word):
        _def = BabLaFetcher.html_to_card_text(fetch_html('https://pl.bab.la/slownik/angielski-polski/' + encode(word)))
        if _def.strip() == '':
            raise DefinitionFetcher.NoDefinition
        return _def


class MerriamWebsterFetcher(DefinitionFetcher):
    @staticmethod
    def html_to_card_text(html_data):
        b = BeautifulSoup(html_data, 'html.parser')
        out_text = []
        parent = b.select_one('.left-content')
        for child in parent.children:
            try:
                if 'anchor-seporator' == child.get('id'):
                    break
                elif child.get('class') is not None and 'entry-header' in child.get('class') and 'row' in child.get('class'):
                    out_text.append(clean_up(child.getText()))
                elif child.get('id').startswith('dictionary-entry-'):
                    for c in child.select('div'):
                        if c.get('class') is not None and 'vg' in c.get('class'):
                            out_text.append(clean_up(c.getText()))
            except AttributeError:
                pass
        ret = '\n'.join(out_text)
        return ret

    @staticmethod
    def definition(word):
        _def = ''
        try:
            _def = MerriamWebsterFetcher.html_to_card_text(fetch_html('https://www.merriam-webster.com/dictionary/' + encode(word)))
        except urllib.error.HTTPError: pass
        if _def.strip() == '':  # TODO: stupid
            raise DefinitionFetcher.NoDefinition
        return _def


class AnkiWriter:
    @staticmethod
    def save(data, deck_name, filename):
        my_model = genanki.Model(
            1843122420,
            'Simple Model',
            fields=[
                {'name': 'Word'},
                {'name': 'Definition'}
            ],
            templates=[{
                    'name': 'Card 1',
                    'qfmt': '{{Definition}}',
                    'afmt': '<h3>{{Word}}</h3><hr />{{FrontSide}}'
                }]
        )
        my_deck = genanki.Deck(
            1426631669,
            deck_name
        )
        for word, definition in data:
            my_note = genanki.Note(model=my_model, fields=[word, definition])
            my_deck.add_note(my_note)
        genanki.Package(my_deck).write_to_file(filename + '.apkg')


def convert_word_list(in_filename, out_deck_name, out_filename):
    data = []
    for line in io.open(in_filename, mode='r', encoding='utf-8').read().split('\n'):
        line = line.strip()

        d1, d2 = '', ''

        try:
            d1 = BabLaFetcher.definition(line).replace('\n', '<br />')
            nab('click')
        except DefinitionFetcher.NoDefinition: pass

        try:
            d2 = MerriamWebsterFetcher.definition(line).replace('\n', '<br />')
            nab('zip')
        except DefinitionFetcher.NoDefinition: pass

        if d1 and d2:
            data.append([line, d1 + '<hr />' + d2])
        elif d1:
            data.append([line, d1])
        elif d2:
            data.append([line, d2])
        if not (d1 or d2):
            nab('error')
            print('No definition found for', line)

    AnkiWriter.save(data, out_deck_name, out_filename)


if __name__ == '__main__':
    convert_word_list('list.txt', 'test_deck', 'test_1')
    nab('bird')
