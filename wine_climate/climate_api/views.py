from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import WineRegionSerializer, ClimateInsightsSerializer
from .models import WineRegion, ClimateInsights
from climate_api.services import update_climate_data_for_all_regions, calculate_climate_insights_for_region

class WineRegionView(APIView):
    # FOR TESTING: Simply returns the original list of wine regions
    def get(self, request, *args, **kwargs):
        wine_regions = WineRegion.objects.all()
        
        wine_regions_serializer = WineRegionSerializer(wine_regions, many=True)
        
        return Response({ 
                'wine_regions': wine_regions_serializer.data 
            }, status=status.HTTP_200_OK) 
    
class ClimateMetricsView(APIView):
    # FOR TESTING: Forces a refetch of climate metrics from Open Meteo Climate API, no need for this if the timer works fine
    def get(self, request, *args, **kwargs):
        update_data_response = update_climate_data_for_all_regions()
        
        if update_data_response is None:
            return Response({"error": "Failed to fetch climate data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(update_data_response, status=status.HTTP_200_OK)
    
class ClimateCalculateInsightsForRegionView(APIView):
    # FOR TESTING: Forces a calculation of climate insights, no need for this if the timer works fine
    def get(self, request, *args, **kwargs):
        region_id = kwargs.get('region_id', None)
 
        if region_id is not None:
            calculate_climate_insights_response = calculate_climate_insights_for_region(region_id)
        else:
            calculate_climate_insights_response = calculate_climate_insights_for_region(1)
        
        
        if calculate_climate_insights_response is None:
            return Response({"error": "Failed to calculate climate insights"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(calculate_climate_insights_response, status=status.HTTP_200_OK)
    
class ClimateInsightsView(APIView):
    def get(self, request, *args, **kwargs):
        region_id = kwargs.get('region_id', None)

        try: 
            if region_id is not None:
                insights = ClimateInsights.objects.filter(wine_region=region_id).order_by("-created_at").first()
            else:
                insights = (
                    ClimateInsights.objects.order_by("wine_region", "-created_at")
                    .distinct("wine_region")
                )

            insights_serializer = ClimateInsightsSerializer(insights, many=True)

            return Response(insights_serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": f"Failed to fetch climate insights: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

