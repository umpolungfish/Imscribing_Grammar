"""Lossless native JSON graphs for a resident inference view.

Canonical tool records stay untouched in the bank. Repeated subobjects and
ROTAT words have shared definitions; list order and every observation survive.
"""
import hashlib
import json
PREFIX = 'Retained native JSON graph (D=schema and values, L=list, R=object reference, W=left ROTAT):\n'
TEXT_PREFIX = 'Retained text with exact native JSON segments (literal strings retain their positions):\n'

class NativeJSONView:
    def __init__(self, alphabet=()):
        self.alphabet = set(alphabet)
        self.schemas = {}
        self.objects = {}
        self.words = []
        self.decoded_schemas = {}
        self.decoded_objects = {}
        self.decoded_words = {}

    def encode_text(self, text):
        """Share native JSON embedded in a task frame without losing layout."""
        decoder = json.JSONDecoder()
        parts = []
        cursor = scan = 0
        while True:
            start = text.find('{', scan)
            if start < 0:
                break
            try:
                value, end = decoder.raw_decode(text, start)
            except ValueError:
                scan = start + 1
                continue
            raw = text[start:end]
            layouts = [indent for indent in (None, 2, 4) if json.dumps(value, ensure_ascii=False, indent=indent) == raw]
            if len(raw) < 2048 or not layouts:
                scan = end
                continue
            canonical = json.dumps(value, ensure_ascii=False)
            encoded = self.encode_body(canonical)
            if not encoded.startswith(PREFIX):
                scan = end
                continue
            parts.append(text[cursor:start])
            parts.append({'native_json': json.loads(encoded[len(PREFIX):]), 'indent': layouts[0],
                          'source_sha256': hashlib.sha256(raw.encode()).hexdigest()})
            cursor = scan = end
        if not parts:
            return text
        parts.append(text[cursor:])
        return TEXT_PREFIX + json.dumps(parts, ensure_ascii=False, separators=(',', ':'))

    def decode_text(self, text):
        if not text.startswith(TEXT_PREFIX):
            return text
        parts = []
        for part in json.loads(text[len(TEXT_PREFIX):]):
            if isinstance(part, str):
                parts.append(part)
            else:
                canonical = self.decode_body(PREFIX + json.dumps(part['native_json'], ensure_ascii=False))
                raw = json.dumps(json.loads(canonical), ensure_ascii=False, indent=part['indent'])
                if hashlib.sha256(raw.encode()).hexdigest() != part['source_sha256']:
                    raise ValueError('Embedded native JSON changed its source layout')
                parts.append(raw)
        return ''.join(parts)

    def encode_body(self, body):
        if len(body) < 2048:
            return body
        try:
            value = json.loads(body)
        except (ValueError, TypeError):
            return body
        if json.dumps(value, ensure_ascii=False) != body:
            return body
        definitions = []
        words = []
        schemas = []

        def encode(value):
            if isinstance(value, str) and len(value) >= 16 and set(value) <= self.alphabet:
                for index, base in enumerate(self.words):
                    if len(base) == len(value):
                        offset = (base + base).find(value)
                        if 0 <= offset < len(base):
                            return ['W', index, offset]
                index = len(self.words)
                self.words.append(value)
                words.append([index, value])
                return ['W', index, 0]
            if not isinstance(value, (dict, list)):
                return value
            raw = json.dumps(value, ensure_ascii=False)
            shared = len(raw) >= 128
            if shared and raw in self.objects:
                return ['R', self.objects[raw]]
            if isinstance(value, dict):
                keys = tuple(value)
                if keys not in self.schemas:
                    self.schemas[keys] = len(self.schemas)
                    schemas.append([self.schemas[keys], list(keys)])
                encoded = ['D', self.schemas[keys], [encode(item) for item in value.values()]]
            else:
                encoded = ['L', [encode(item) for item in value]]
            if shared:
                index = len(self.objects)
                self.objects[raw] = index
                definitions.append([index, encoded])
                return ['R', index]
            return encoded

        encoded = encode(value)
        envelope = {'words': words, 'schemas': schemas, 'definitions': definitions, 'value': encoded,
                    'sha256': hashlib.sha256(body.encode()).hexdigest()}
        return PREFIX + json.dumps(envelope, ensure_ascii=False, separators=(',', ':'))

    def decode_body(self, body):
        if not body.startswith(PREFIX):
            return body
        envelope = json.loads(body[len(PREFIX):])
        for index, keys in envelope.get('schemas', []):
            if index in self.decoded_schemas:
                raise ValueError('Native object schema was reassigned')
            self.decoded_schemas[index] = keys
        for index, word in envelope['words']:
            if index in self.decoded_words:
                raise ValueError('Native word definition was reassigned')
            self.decoded_words[index] = word

        def decode(value):
            if not isinstance(value, list):
                return value
            tag = value[0]
            if tag == 'W':
                base = self.decoded_words[value[1]]
                return base[value[2]:] + base[:value[2]]
            if tag == 'R':
                return self.decoded_objects[value[1]]
            if tag == 'D':
                return dict(zip(self.decoded_schemas[value[1]], map(decode, value[2])))
            if tag == 'L':
                return [decode(item) for item in value[1]]
            raise ValueError('Unknown native JSON graph constructor')

        for index, encoded in envelope['definitions']:
            if index in self.decoded_objects:
                raise ValueError('Native object definition was reassigned')
            self.decoded_objects[index] = decode(encoded)
        restored = json.dumps(decode(envelope['value']), ensure_ascii=False)
        if hashlib.sha256(restored.encode()).hexdigest() != envelope['sha256']:
            raise ValueError('Native JSON graph changed its source record')
        return restored
