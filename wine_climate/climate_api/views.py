from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .serializers import WineRegionSerializer
from .models import WineRegion
from django.core.exceptions import ObjectDoesNotExist



class WineRegionView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            wine_regions = WineRegion.objects.all()
        except ObjectDoesNotExist:
            return Response({
                'message': 'Wine regions not found'
            }, 
            status=status.HTTP_400_BAD_REQUEST)
        
        wine_regions_serializer = WineRegionSerializer(wine_regions, many=True)
        
        return Response({ 
                'wine_regions': wine_regions_serializer.data 
            }, status=status.HTTP_200_OK) 
