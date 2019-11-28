from lineus import LineUs
import re
import time


class Keyboard:
    """A class to control a small keyboard like a Stylophone using a Line-us"""

    _line_us = None
    _default_keyboard = 'VolcaFM'
    _keyboard = _default_keyboard
    _keyboard_params_list = {
        'VolcaFM': {
            'home_note': 'c',
            'high_key_note': 'g-',
            'high_key_y': 1550,
            'low_key_note': 'f+',
            'low_key_y': -1450,
            'natural_x': 1000,
            'sharp_x': 1300,
        },
        'VolcaFMLow': {
            'home_note': 'c',
            'high_key_note': 'f-',
            'high_key_y': 1500,
            'low_key_note': 'e+',
            'low_key_y': -1450,
            'natural_x': 1000,
            'sharp_x': 1300,
        },
        'Stylophone': {
            'high_key_note': 'a-',
            'high_key_y': 1000,
            'low_key_note': 'e+',
            'low_key_y': -1200,
            'natural_x': 1000,
            'sharp_x': 1200,
        },
    }
    _keyboard_params = None
    _note_spacing = 0
    _bpm = 90
    _note_time_ms = 60 / _bpm * 1000

    _notes = ('c', 'C', 'd', 'D', 'e', 'f', 'F', 'g', 'G', 'a', 'A', 'b')
    _major_notes = ('c', 'd', 'e', 'f', 'g', 'a', 'b')
    _minor_notes = ('C', 'D', '_', 'F', 'G', 'A', '_')

    def __init__(self, line_us, keyboard=None):
        self._line_us = line_us
        # Set up Line-us, fast pen up moves and disable gestures
        self._line_us.send_gcode('G94', 'P50')
        if keyboard is not None:
            self._keyboard = keyboard
        self._keyboard_params = self._keyboard_params_list.get(self._keyboard)
        total_notes = self.count_notes(
            self.decode_note(self._keyboard_params.get('high_key_note')),
            self.decode_note(self._keyboard_params.get('low_key_note'))
        )
        self._note_spacing = (self._keyboard_params.get('high_key_y') -
                              self._keyboard_params.get('low_key_y')) / (total_notes - 1)
        self.play_note(self._keyboard_params.get('home_note', 'c'), only_move=True)

    def set_bpm(self, bpm):
        self._bpm = bpm
        self._note_time_ms = 60 / self._bpm * 1000

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
            if raw_note[0] in self._major_notes:
                decoded_note['type'] = 'natural'
        except ValueError:
            pass
        try:
            if raw_note[0] in self._minor_notes:
                decoded_note['type'] = 'sharp'
        except ValueError:
            pass
        if raw_note[0] == 'r':
            decoded_note['type'] = 'rest'
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
            decoded_note['length'] = float(duration.group(1))
            raw_note = duration.group(2)

        if len(raw_note) == 0:
            return decoded_note

        # portamento not currently implemented
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
        start_index = self._major_notes.index(start_note.get('raw_note'))
        end_index = self._major_notes.index(end_note.get('raw_note'))
        note_count += (end_index - start_index)
        note_count += 7 * (end_note.get('octave') - start_note.get('octave'))
        return note_count + 1

    def note_to_coords(self, decoded_note):
        distance = (self.count_notes(
            self.decode_note(self._keyboard_params.get('high_key_note')),
            decoded_note
        ) - 1) * self._note_spacing
        y_coord = self._keyboard_params.get('high_key_y') - distance
        if decoded_note.get('type') == 'sharp':
            x_coord = self._keyboard_params.get('sharp_x')
        else:
            x_coord = self._keyboard_params.get('natural_x')
        return x_coord, y_coord

    def play_note(self, note, only_move=False):
        decoded_note = self.decode_note(note)
        if decoded_note.get('type') == 'rest':
            time.sleep(self._note_time_ms * decoded_note.get('length', 1) / 1000)
        else:
            x, y = self.note_to_coords(decoded_note)
            # print(f'{decoded_note["raw_note"]}:{x}:{y}')
            self._line_us.g01(x, y, 1000)
            if not only_move:
                self._line_us.g01(x, y, 0)
                time.sleep(self._note_time_ms * decoded_note.get('length', 1) / 1000)
                self._line_us.g01(x, y, 1000)


if __name__ == '__main__':

    areFriendsElectric = ('c', 'c', 'g', 'r', 'A-', 'A-', 'f', 'r', 'c', 'c', 'g', 'r', 'A-', 'A-', 'A', 'e')
    closeEncounters = ('g', 'a', 'f', 'f-', 'c')
    low_volca_scale = ('f-', 'g-', 'a-', 'b-', 'c', 'd', 'e', 'f', 'g', 'a', 'b', 'c+', 'd+', 'e+')
    volca_scale = ('g-', 'a-', 'b-', 'c', 'd', 'e', 'f', 'g', 'a', 'b', 'c+', 'd+', 'e+', 'f+')
    stylophone_scale = ('a-', 'A-', 'b-', 'c', 'd', 'e', 'f', 'g', 'a', 'b', 'c+', 'd+', 'e+')

    song = areFriendsElectric

    my_lineus = LineUs()
    my_lineus.connect('line-us.local')
    k = Keyboard(my_lineus, keyboard='Stylophone')
    k.set_bpm(100)

    input('Set Line-us to \'c\':')

    for song_note in song:
        k.play_note(song_note)
