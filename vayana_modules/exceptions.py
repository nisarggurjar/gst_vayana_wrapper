class VayanaAuthException(Exception):
    pass


class APIException(Exception):

    def __init__(self, json_data):
        self.message = json_data['message']
        self.error_code = json_data['error_cd']

    def __str__(self):
        return self.message + ":" + self.error_code

    def __repr__(self):
        return self.message + ":" + self.error_code
