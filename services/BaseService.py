
class BaseService():
    def __init__(self, locale):
        pass

    def serialise(self, model):
        pass

    def deserialise(self, model, instance):
        pass

    def post_to_translator(self, item_type, item_id):
        pass

    def get_from_translator(self, request):
        pass
