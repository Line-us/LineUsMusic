from lineus import LineUs
import re
import pprint
import time


class Keyboard:
    """A class to control a small keyboard like a Stylophone using a Line-us"""

    __default_keyboard = 'VolcaFM'
    __keyboard = __default_keyboard
    __keyboard_params_list = {
        'VolcaFM': {
            'major_x': 0,
            'minor_x': 100,
            'high_key_note': 'g-',
            'high_key_y': 1600,
            'low_key_note': 'f+',
            'low_key_y': -1500,
            'natural_x': 1000,
            'sharp_x': 1300,
        },
        'Stylophone': {
            'major_x': 0,
            'minor_x': 100,
            'high_key_note': 'b-',
            'high_key_y': 1000,
            'low_key_note': 'c+',
            'low_key_y': -1000,
            'natural_x': 1000,
            'sharp_x': 1400,
        },
    }
    __keyboard_params = None
    __note_spacing = 0
    __bpm = 90
    __note_time_ms = __bpm / 60 * 1000

    __notes = ('c', 'C', 'd', 'D', 'e', 'f', 'F', 'g', 'G', 'a', 'A', 'b')
    __major_notes = ('c', 'd', 'e', 'f', 'g', 'a', 'b')
    __minor_notes = ('C', 'D', '_', 'F', 'G', 'A', '_')

    def __init__(self):
        self.__keyboard_params = self.__keyboard_params_list.get(self.__keyboard)
        total_notes = self.count_notes(
            self.decode_note(self.__keyboard_params.get('high_key_note')),
            self.decode_note(self.__keyboard_params.get('low_key_note'))
        )
        self.__note_spacing = (self.__keyboard_params.get('high_key_y') -
                               self.__keyboard_params.get('low_key_y')) / (total_notes + 1)

    def set_bpm(self, bpm):
        self.__bpm = bpm
        self.__note_time_ms = self.__bpm / 60 * 1000

    def decode_note(self, raw_note):
        # Note examples
        # c+2   - c, one octave up 2 time units long
        # C1    - c sharp, 1 time unit long
        decoded_note = {
            'octave': 0,
            'length': 1,
            'portamento': None,
        }
        try:
            if raw_note[0] in self.__major_notes:
                decoded_note['type'] = 'natural'
        except ValueError:
            pass
        try:
            if raw_note[0] in self.__minor_notes:
                decoded_note['type'] = 'sharp'
        except ValueError:
            pass
        if 'type' not in decoded_note:
            raise LookupError
        decoded_note['raw_note'] = raw_note[0].lower()
        raw_note = raw_note[1:]

        if len(raw_note) == 0:
            return decoded_note

        decoded_note['octave'] = 0
        while len(raw_note) > 0 and raw_note[0] in ('+', '-'):
            if raw_note[0] == '+':
                decoded_note['octave'] += 1
            if raw_note[0] == '-':
                decoded_note['octave'] -= 1
            raw_note = raw_note[1:]

        if len(raw_note) == 0:
            return decoded_note

        duration = re.match(r'(^\d+)(.*)', raw_note)
        if duration is not None:
            decoded_note['length'] = duration.group(1)
            raw_note = duration.group(2)

        if len(raw_note) == 0:
            return decoded_note

        # portamento
        if raw_note[0] == '/':
            raw_note = raw_note[1:]
            portamento = self.decode_note(raw_note)
            if portamento is not None:
                decoded_note['portamento'] = portamento
        return decoded_note

    def count_notes(self, start_note, end_note):
        note_count = 0
        if start_note.get('type').lower() == 'sharp':
            note_count -= 0.5
        if end_note.get('type').lower() == 'sharp':
            note_count += 0.5
        start_index = self.__major_notes.index(start_note.get('raw_note'))
        end_index = self.__major_notes.index(end_note.get('raw_note'))
        note_count += (end_index - start_index)
        note_count += 7 * (end_note.get('octave') - start_note.get('octave'))
        return note_count

    def note_to_coords(self, decoded_note):
        distance = self.count_notes(
            self.decode_note(self.__keyboard_params.get('high_key_note')),
            decoded_note
        ) * self.__note_spacing
        y_coord = self.__keyboard_params.get('high_key_y') - distance
        if decoded_note.get('type') == 'sharp':
            x_coord = self.__keyboard_params.get('sharp_x')
        else:
            x_coord = self.__keyboard_params.get('natural_x')
        return x_coord, y_coord

    def play(self, notes):
        for n in notes.split():
            pass


if __name__ == '__main__':
    lineus = LineUs()
    lineus.connect()
    time.sleep(1)
    # pp = pprint.PrettyPrinter(indent=4)
    k = Keyboard()
    x, y = (k.note_to_coords(k.decode_note('c')))
    lineus.g01(x, y, 1000)
    # input('Set to c and press return')
    # n = k.decode_note('a+2/F')
    # pp.pprint(n)
    # print(k.count_notes(k.decode_note('c'), k.decode_note('D+')))
    # print(k.note_to_coords(k.decode_note('A')))
    lineus.send_gcode('G94', 'P50')
    # for note in ('d+', 'e+', 'c+', 'c', ):
    #     x, y = k.note_to_coords(k.decode_note(note))
    #     lineus.g01(x, y, 1000)
    #     # lineus.send_gcode('G00', f'X{x} Y{y} Z1000')
    #     lineus.g01(x, y, 0)
    #     time.sleep(0.6)
    # x, y = k.note_to_coords(k.decode_note('g'))
    # lineus.g01(x, y, 1000)
    # lineus.g01(x, y, 0)
    # time.sleep(1.8)
    # lineus.g01(x, y, 1000)
    # time.sleep(5)

    for note in ('c', 'c', 'g', 'r', 'A-', 'A-', 'f', 'r', 'c', 'c', 'g', 'r', 'A-', 'A-', 'A'):
        if note != 'r':
            x, y = k.note_to_coords(k.decode_note(note))
            lineus.g01(x, y, 1000)
            lineus.g01(x, y, 0)
        time.sleep(0.3)
    for note in ('e'):
        if note != 'r':
            x, y = k.note_to_coords(k.decode_note(note))
            lineus.g01(x, y, 1000)
            lineus.g01(x, y, 0)
        time.sleep(0.15)
    lineus.g01(x, y, 1000)
    time.sleep(5)