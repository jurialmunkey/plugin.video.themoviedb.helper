from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.files.futils import (
    validify_filename,
    make_path,
    write_to_file
)


class FileWriter:

    file_extension = 'strm'
    clean_url = True

    def __init__(self, *folders, content=None):
        self.content = content
        self.folders = folders

    @staticmethod
    def replace_content(content, old, new):
        content = content.replace(old, new)
        return FileWriter.replace_content(content, old, new) if old in content else content

    @staticmethod
    def clean_content(content, details='info=play'):
        content = content.replace('info=related', details)
        content = content.replace('info=flatseasons', details)
        content = content.replace('info=details', details)
        content = content.replace('widget=True', '')
        content = content.replace('localdb=True', '')
        content = content.replace('nextpage=True', '')
        content = FileWriter.replace_content(content, '&amp;', '&')
        content = FileWriter.replace_content(content, '&&', '&')
        content = FileWriter.replace_content(content, '?&', '?')
        content = content + '&islocal=True' if '&islocal=True' not in content else content
        return content

    @cached_property
    def contents(self):
        contents = FileWriter.clean_content(self.content) if self.clean_url else self.content
        return contents

    @cached_property
    def filename(self):
        filename = self.folders[-1] or ''
        filename = validify_filename(filename)
        return f'{filename}.{self.file_extension}' if filename else None

    @cached_property
    def filepath(self):
        filepath = [self.folders[0].replace('\\', '/')]  # First folder is basedir, just convert DOS to UNIX style paths
        filepath = filepath + [validify_filename(f) for f in self.folders[1:-1]]
        return '/'.join(filepath)

    @cached_property
    def filename_and_path(self):
        return f'{self.filepath}/{self.filename}'

    ERROR_FILENAME = 1
    ERROR_FILEPATH = 2
    ERROR_CONTENTS = 3
    ERROR_MAKEPATH = 4

    @cached_property
    def error(self):
        if not self.filename:
            return self.ERROR_FILENAME
        if not self.filepath:
            return self.ERROR_FILEPATH
        if not self.contents:
            return self.ERROR_CONTENTS
        if not make_path(self.filepath, warn_dialog=True):  # Check that we can actually make the path
            return self.ERROR_MAKEPATH
        return 0

    @cached_property
    def success(self):
        if not self.error:
            write_to_file(self.contents, self.filepath, self.filename, join_addon_data=False)
            return True
        return False
