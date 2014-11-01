
class Query:

    def __init__(self, args):
        self.component = args.component.lower()
        self.resolution_max = args.resolution_max

    def get_filter_names(self):
        filters = []
        if self.resolution_max is not None:
            filters.append("Maximal resolution: {0}".format(self.resolution_max))
        return filters
