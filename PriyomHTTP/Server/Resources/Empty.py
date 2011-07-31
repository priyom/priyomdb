from Resource import Resource

class EmptyResource(Resource):
    def respond(self, trans):
        return
