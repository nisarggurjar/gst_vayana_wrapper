from abc import ABCMeta, abstractmethod


class TransformerBase(object):

    __metaclass__ = ABCMeta

    RENAME_DATA = None

    def __init__(self, data):

        self.data = data
        self.transformed = False

    def _rename_keys(self, containing_frame, path, new_name):

        if isinstance(containing_frame, list):
            for item in containing_frame:
                self._rename_keys(item, path, new_name)

            return

        sections = path.split(".")

        if len(sections) == 1:
            try:
                self._rename_key(containing_frame, path, new_name)
            except KeyError:
                pass

            return

        current_key = sections[0]
        remaining_path = ".".join(sections[1:])
        containing_frame = containing_frame[current_key]
        self._rename_keys(containing_frame, remaining_path, new_name)

    def _rename_key(self, frame, key_name, new_name):
        frame[new_name] = frame[key_name]
        del frame[key_name]

    def rename_transformation(self):

        for path, new_name in self.RENAME_DATA.items():
            self._rename_keys(self.data, path, new_name)

        return self.data

    @abstractmethod
    def rearrange_transformation(self):
        """
        Implement custom schema changes in this function
        If no transformations schema wise, return data as is
        """
        return

    def transform(self):

        if self.transformed:
            return self.data

        self.rename_transformation()
        self.rearrange_transformation()
        self.transformed = True

        return self.data
