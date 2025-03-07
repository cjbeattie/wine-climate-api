from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .serializers import WineRegionSerializer
from .models import WineRegion
from django.core.exceptions import ObjectDoesNotExist
from .providers.climate_data import update_climate_data_for_all_regions

class WineRegionView(APIView):
    def get(self, request, *args, **kwargs):
        wine_regions = WineRegion.objects.all()
        
        wine_regions_serializer = WineRegionSerializer(wine_regions, many=True)
        
        return Response({ 
                'wine_regions': wine_regions_serializer.data 
            }, status=status.HTTP_200_OK) 
    
class ClimateMetricsView(APIView):
    def get(self, request, *args, **kwargs):
            update_data_response = update_climate_data_for_all_regions()
            
            if update_data_response is None:
                return Response({"error": "Failed to fetch climate data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(update_data_response, status=status.HTTP_200_OK)