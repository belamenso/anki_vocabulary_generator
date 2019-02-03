import io
import genanki
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlencode


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
    def fetch_html(word):
        url = 'https://pl.bab.la/slownik/angielski-polski/' + (urlencode({'': word})[1:])  # for polish letters
        connection = urllib.request.urlopen(url)
        ret = connection.read().decode('utf-8')
        connection.close()
        return ret

    @staticmethod
    def definition(word):
        _def = BabLaFetcher.html_to_card_text(BabLaFetcher.fetch_html(word))
        if _def.strip() == '':
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
        try:
            data.append([line, BabLaFetcher.definition(line).replace('\n', '<br />')])
        except DefinitionFetcher.NoDefinition:
            print('No definition found for', line)
    AnkiWriter.save(data, out_deck_name, out_filename)


if __name__ == '__main__':
    convert_word_list('list.txt', 'test_deck', 'test_1')
