from datetime import datetime


def year(request):
    this_year = datetime.now().year
    return {'year': this_year}
