from django.core.serializers.json import DjangoJSONEncoder  # to handle the datetime serialization
from django.db.models.fields.files import FieldFile
from django_countries.fields import Country
from django.utils.encoding import smart_text


class WildlifeLicensingJSONEncoder(DjangoJSONEncoder):
    """
    DjangoJSONEncoder subclass that encode file file object as its URL and country object to its name
    """
    def default(self, o):
        if isinstance(o, FieldFile):
            return o.url
        elif isinstance(o, Country):
            return smart_text(o.name)
        else:
            return super(WildlifeLicensingJSONEncoder, self).default(o)
