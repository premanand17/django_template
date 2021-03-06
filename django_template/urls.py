from django.conf.urls import include, url
from db.api import CvtermResource, CvtermFullResource, CvResource
from db.api import CvtermpropResource, FeaturelocResource
from db.api import FeaturelocFullResource, FeatureResource, FeatureFullResource
from db.api import FeaturepropResource, FeaturepropFullResource
from db.api import OrganismResource
from tastypie.api import Api
from elastic.tastypie.api import GeneResource, DiseaseResource,\
    MarkerResource

# register tastypie api
api = Api(api_name='dev')
api.register(CvtermResource())
api.register(CvtermFullResource())
api.register(CvResource())
api.register(OrganismResource())
api.register(FeaturelocResource())
api.register(FeaturelocFullResource())
api.register(FeatureResource())
api.register(FeatureFullResource())
api.register(FeaturepropResource())
api.register(FeaturepropFullResource())
api.register(CvtermpropResource())

# register tastypie api
elastic_api = Api(api_name='dev')
elastic_api.register(GeneResource())
elastic_api.register(DiseaseResource())
elastic_api.register(MarkerResource())

urlpatterns = [url(r'^', include('bands.urls', namespace="bands")),
               url(r'^api/', include(api.urls)),
               url(r'^elastic/', include(elastic_api.urls)),
               url(r'^search/', include('elastic.urls', namespace="elastic")),
               url(r'^gene/', include('gene.urls')),
               url(r'^marker/', include('marker.urls')),
               url(r'^region/', include('region.urls')),
               ]
