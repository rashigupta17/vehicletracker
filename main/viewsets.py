from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status , permissions
from rest_framework.validators import ValidationError
from django.core.paginator import EmptyPage,Paginator
from django.http import JsonResponse 

class DetailsAPI(APIView):
    """
    Retrieve, update or delete a objects instance.
    """
    model_class = None
    serializer_class = None
    permission_classes = None
    instance_name = None

    def get_object(self, pk):

        try:
            return self.model_class.objects.get(pk=pk)
        except self.model_class.DoesNotExist:
            raise ValidationError({
                'status': False,
                'message': f"failed to find {self.instance_name}",
                "data": {}
            })

    def get(self, request, pk=None, format=None):
        obj = self.get_object(pk)
        serializer = self.serializer_class(obj)
        return Response(
            data={
                "status": True,
                "message":f"{self.instance_name} reterived sucessfully",
                "data": serializer.data
            })

    def put(self, request, pk=None, format=None):
        obj = self.get_object(pk)
        serializer = self.serializer_class(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={
                    "status": True,
                    "message": "{self.instance_name} updated sucessfully",
                    "data": serializer.data
                })
        return Response(data={
            "status": False,
            "message": f"{self.instance_name} update failed",
            "data": serializer.errors
        },
                        status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = self.serializer_class(obj,
                                           data=request.data,
                                           partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={
                    "status": True,
                    "message": f"{self.instance_name} updated sucessfully",
                    "data": serializer.data
                })
        return Response(data={
            "status": False,
            "message": f"{self.instance_name} update failed",
            "data": serializer.errors
        },
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None, format=None):
        obj = self.get_object(pk)
        obj.delete()
        return Response(data={
            "status": True,
            "message":f"{self.instance_name} deleted sucessfully",
            "data": {}
        },
                        status=status.HTTP_200_OK)


class UserAttributeList(APIView):
    """
    A Base API class for listing attributes based on user
    """
    model_class = None
    serializer_class = None
    instance_name = None
    permission_classes = None

    def get(self, request, format=None):
        try:
            obj = self.model_class.objects.all()
            serializer = self.serializer_class(obj, many=True)
            response_data = {
                'status': True,
                'message': f'{self.instance_name} reterieved sucessfully',
                'data': serializer.data
            }
            return Response(response_data)
        except:
            response_data = {
                'status': False,
                'message': 'error in user key',
                'data': {}
            }
            return Response(response_data)


class CreateAttribute(APIView):
    """
    custom class to save data
    """

    model_class = None
    serializer_class = None
    instance_name = None
    message =None
    permission_classes = None

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            response_data = {
                "status": True,
                'message': f'{self.instance_name} created',
                'data': serializer.data
            }
            return Response(data=response_data)
        response_data = {
            'status': False,
            'message': f'error creating {self.instance_name}',
            'data': serializer.errors
        }
        return Response(data=response_data, status=400)



class PaginationList(APIView):
    """
    A Base API class for listing attributes based on user
    """
    model_class = None
    serializer_class = None
    instance_name = None
    permission_classes = None

    def get(self, request, format=None):
        
        try:
            activity_list = self.model_class.objects.all().order_by('-id').values()
            pagenumber = request.GET.get('page', 1)
            record_num = request.GET.get('records',10)
            if record_num == 10:
                paginator = Paginator(activity_list, 10)
                data = pagination(paginator, pagenumber)
            elif record_num == 25:
                paginator = Paginator(activity_list, 25)
                data = pagination(paginator, pagenumber)
            elif record_num == 50:
                paginator = Paginator(activity_list, 50)
                data = pagination(paginator, pagenumber)
            elif record_num == 100:
                paginator = Paginator(activity_list, 100)
                data = pagination(paginator, pagenumber)
            response_data = {
                'status': False,
                'message': 'data retreived',
                'data': data
            }
            return Response(response_data)

        except:
            response_data = {
                'status': False,
                'message': 'error in user key',
                'data': {}
            }
            return Response(response_data)

class PaginationList(APIView):
    """
    A Base API class for listing attributes based on user
    """
    model_class = None
    serializer_class = None
    instance_name = None
    permission_classes = None

    def get(self, request, format=None):
        try:
            obj = self.model_class.objects.all().values()
            pagenumber = request.GET.get('page', 1)
            record_num = request.GET.get('records',10)
            if record_num == 10:
                paginator = Paginator(activity_list, 10)
                data = common_methods.pagination(paginator, pagenumber)
            elif record_num == 25:
                paginator = Paginator(activity_list, 25)
                data = common_methods.pagination(paginator, pagenumber)
            elif record_num == 50:
                paginator = Paginator(activity_list, 50)
                data = common_methods.pagination(paginator, pagenumber)
            elif record_num == 100:
                paginator = Paginator(activity_list, 100)
                data = common_methods.pagination(paginator, pagenumber)
            return JsonResponse(data, safe=False)
        except:
            response_data = {
                'status': False,
                'message': 'error in user key',
                'data': {}
            }
            return Response(response_data)
