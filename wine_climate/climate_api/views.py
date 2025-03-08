from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import WineRegionSerializer, ClimateInsightsSerializer
from .models import WineRegion, ClimateInsights
from climate_api.services import update_climate_data_for_all_regions

class WineRegionView(APIView):
    # Simply returns the original list of wine regions
    def get(self, request, *args, **kwargs):
        wine_regions = WineRegion.objects.all()
        
        wine_regions_serializer = WineRegionSerializer(wine_regions, many=True)
        
        return Response({ 
                'wine_regions': wine_regions_serializer.data 
            }, status=status.HTTP_200_OK) 
    
class ClimateMetricsView(APIView):
    # Forces a refetch of climate metrics from Open Meteo Climate API, no need for this if the timer works fine
    def get(self, request, *args, **kwargs):
        update_data_response = update_climate_data_for_all_regions()
        
        if update_data_response is None:
            return Response({"error": "Failed to fetch climate data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(update_data_response, status=status.HTTP_200_OK)
    
class ClimateInsightsView(APIView):
    def get(self, request, *args, **kwargs):
        region_id = kwargs.get('region_id', None)

        try: 
            if region_id is not None:
                insights = ClimateInsights.objects.filter(wine_region=region_id)
            else:
                insights = ClimateInsights.objects.all()

            insights_serializer = ClimateInsightsSerializer(insights, many=True)

            return Response(insights_serializer.data, status=status.HTTP_200_OK)
        
        except:
            return Response({"error": "Failed to fetch climate insights"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

