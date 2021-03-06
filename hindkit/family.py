from __future__ import division, print_function, unicode_literals

import os
import robofab.world
import hindkit as kit

class Family(object):

    def __init__(
        self,
        trademark = '',
        script = '',
        hide_script_name = False,
    ):

        self.trademark = trademark
        self.script = script
        self.hide_script_name = hide_script_name

        self.name = self.trademark
        if self.script and not self.hide_script_name:
            self.name += ' ' + self.script
        self.name_postscript = self.name.replace(' ', '')

        self.output_name_affix = '{}'
        self.goadb_path = kit.paths.GOADB
        self.working_directory = os.path.realpath(os.getcwd())

    @property
    def output_name(self):
        return self.output_name_affix.format(self.name)

    @property
    def output_name_postscript(self):
        return self.output_name.replace(' ', '')

    @property
    def goadb(self):

        with open(self.goadb_path, 'r') as file:
            goadb_content = file.read()

        goadb = []
        for line in goadb_content.splitlines():
            content = line.partition('#')[0].strip()
            if content:
                row = content.split()
                if len(row) == 2:
                    production_name, development_name = row
                    unicode_mapping = None
                elif len(row) == 3:
                    production_name, development_name, unicode_mapping = row
                goadb.append((production_name, development_name, unicode_mapping))

        return goadb

    def set_masters(self, masters = [], modules = []):

        self.masters = masters
        if not self.masters:
            self.masters = [Master(self, 'Light', 0), Master(self, 'Bold', 100)]

        for module in [
            'kerning',
            'mark_positioning',
            'mark_to_mark_positioning',
            'devanagari_matra_i_variants',
        ]:
            if module in modules:
                self.__dict__['has_' + module] = True
            else:
                self.__dict__['has_' + module] = False

    def set_styles(self, style_scheme = kit.styles.STANDARD_CamelCase):

        self.styles = []

        for style_name, interpolation_value, weight_class in style_scheme:
            style = Style(
                self,
                name = style_name,
                interpolation_value = interpolation_value,
                weight_class = weight_class,
            )
            self.styles.append(style)

    def dump(self):
        dictionary = self.__dict__.copy()
        for i in ['output_name', 'output_name_postscript']:
            dictionary[i] = self.__getattribute__(i)
        for i in ['masters', 'styles']:
            dictionary[i] = [j.dump() for j in self.__getattribute__(i)]
        return dictionary

class _BaseStyle(object):

    def __init__(
        self,
        _family,
        name = '',
        interpolation_value = 0,
        _file_name = None,
    ):
        self._family = _family
        self.name = name
        self.interpolation_value = interpolation_value
        self._file_name = _file_name

    @property
    def directory(self):
        return ''

    @property
    def file_name(self):
        if self._file_name:
            return self._file_name
        else:
            return ''

    @property
    def path(self):
        return os.path.join(self.directory, self.file_name)

    def open_font(self):
        return robofab.world.OpenFont(self.path)

    def dump(self):
        dictionary = self.__dict__.copy()
        dictionary['_family'] = repr(dictionary['_family'])
        for i in ['directory', 'file_name', 'path']:
            dictionary[i] = self.__getattribute__(i)
        return dictionary

class Master(_BaseStyle):

    @property
    def directory(self):
        return kit.paths.MASTERS

    @property
    def file_name(self):
        if self._file_name:
            return self._file_name
        else:
            return '{}-{}.ufo'.format(self._family.name, self.name)

class Style(_BaseStyle):

    def __init__(
        self,
        _family,
        name = '',
        interpolation_value = 0,
        weight_class = 400,
        is_bold = None,
        is_italic = None,
        is_oblique = None,
    ):

        super(Style, self).__init__(_family, name, interpolation_value)

        self.name_postscript = self.name.replace(' ', '')

        self.full_name = _family.name + ' ' + self.name
        self.full_name_postscript = _family.name_postscript + '-' + self.name_postscript

        self.weight_class = weight_class

        self.is_bold = is_bold
        self.is_italic = is_italic
        self.is_oblique = is_oblique
        if is_bold is None:
            self.is_bold = True if 'Bold' in self.name.split() else False
        if is_italic is None:
            self.is_italic = True if 'Italic' in self.name.split() else False
        if is_oblique is None:
            self.is_oblique = True if 'Oblique' in self.name.split() else False

    @property
    def directory(self):
        return os.path.join(kit.paths.INSTANCES, self.name_postscript)

    @property
    def file_name(self):
        if self._file_name:
            return self._file_name
        else:
            return 'font.ufo'

    @property
    def output_full_name(self):
        output_full_name = self._family.output_name + ' ' + self.name
        return output_full_name

    @property
    def output_full_name_postscript(self):
        output_full_name_postscript = self._family.output_name_postscript + '-' + self.name_postscript
        return output_full_name_postscript

    def dump(self):
        dictionary = self.__dict__.copy()
        dictionary['_family'] = repr(dictionary['_family'])
        for i in ['directory', 'file_name', 'path', 'output_full_name', 'output_full_name_postscript']:
            dictionary[i] = self.__getattribute__(i)
        return dictionary
