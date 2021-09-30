from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from todo_app.models import User, ToDo
from todo_app.serializers import SignupSerializer, LoginSerializer, ToDoListSerializer, ToDoAddSerializer
from todo_project.permissions import IsAllowedUser
from todo_project.utils import CommonUtils, DateTimeUtils
from validators.Error import Error


class BaseView(APIView):
    model = None
    serializer = None

    def get_object(self, obj_id):
        if not self.model:
            raise NotImplementedError
        try:
            query = self.model.objects.get(id=obj_id)
            return query
        except self.model.DoesNotExist:
            return None

    def get_all_objects(self):
        if not self.model:
            raise NotImplementedError
        return self.model.objects.all()

    def get_serialized_object(self, obj_id):
        if not self.model or not self.serializer:
            raise NotImplementedError
        if isinstance(obj_id, int):
            obj = self.model.objects.get(id=obj_id)
        else:
            obj = obj_id
        serializer = self.serializer(obj, many=False)
        return serializer.data

    def get_serialized_objects(self, queryset):
        if not self.serializer:
            raise NotImplementedError
        serializer = self.serializer(queryset, many=True)
        return serializer.data

    def get_paginated_data(self, queryset, page_number, per_page=10):
        if not self.serializer:
            raise NotImplementedError
        paginator = Paginator(object_list=queryset, per_page=per_page)
        count = len(queryset)
        data = []
        if count:
            data = self.serializer(paginator.page(page_number), many=True).data
        return {
            'total_pages': paginator.num_pages,
            'page': page_number,
            'per_page': per_page,
            'total_entries': count,
            'data': data
        }


class SignupView(BaseView):
    permission_classes = (AllowAny, )
    model = User
    serializer = SignupSerializer

    def post(self, request):
        try:
            data = request.data
            username, password = data.get('username'), data.get('password')
            if password:
                del data['password']
                serializer = self.serializer(data=data)
                if serializer.is_valid():
                    serializer_obj = serializer.save()
                    serializer_obj.set_password(password)
                    serializer_obj.save()
                    return CommonUtils.dispatch_success(["SUCCESS"])
                else:
                    return CommonUtils.dispatch_failure(Error.VALIDATION_ERROR, serializer.errors)
            return CommonUtils.dispatch_failure(Error.MISSING_PARAMETERS, "Password is missing.")
        except Exception as e:
            return CommonUtils.dispatch_failure(Error.INTERNAL_SERVER_ERROR, str(e))


class LoginView(BaseView):
    permission_classes = (AllowAny, )
    model = User
    serializer = LoginSerializer

    def post(self, request):
        try:
            data = request.data
            validate_user = LoginSerializer(data=data)
            if validate_user.is_valid():
                user = validate_user.validated_data
                token = CommonUtils.create_access(user)
                result = {'username': user.username, 'token': token['access_token']}
                return CommonUtils.dispatch_success(result)
            return CommonUtils.dispatch_failure(Error.VALIDATION_ERROR, validate_user.errors)
        except Exception as e:
            return CommonUtils.dispatch_failure(Error.INTERNAL_SERVER_ERROR, str(e))


class TodoListView(BaseView):
    permission_classes = (IsAllowedUser, )
    model = ToDo
    serializer = ToDoListSerializer
    add_serializer = ToDoAddSerializer

    def get(self, request):
        """
            Get all tasks with available filters and search parameters
        """
        try:
            queryset = self.get_all_objects().filter(user=request.user, is_active=True)
            sort_by = request.GET.get('sort_by', 'asc')
            page = request.GET.get('page', 1)
            search = request.GET.get('search', '')
            status = request.GET.getlist('status', [])
            priority = request.GET.getlist('priority', [])

            from_start_date = request.GET.get('from_start_date')
            to_start_date = request.GET.get('to_start_date')
            from_end_date = request.GET.get('from_end_date')
            to_end_date = request.GET.get('to_end_date')

            if from_start_date and to_start_date:  # Filter tasks based on start date
                from_start_date = DateTimeUtils.convert_date_string_to_date(from_start_date)
                to_start_date = DateTimeUtils.convert_date_string_to_date(to_start_date)
                queryset = queryset.filter(start_date__range=[from_start_date, to_start_date])

            if from_end_date and to_end_date:  # Filter tasks based on end date
                from_end_date = DateTimeUtils.convert_date_string_to_date(from_end_date)
                to_end_date = DateTimeUtils.convert_date_string_to_date(to_end_date)
                queryset = queryset.filter(end_date__range=[from_end_date, to_end_date])

            # Sorting tasks in ascending or descending order
            if sort_by == 'asc':
                queryset = queryset.order_by('created_at')
            elif sort_by == 'desc':
                queryset = queryset.order_by('-created_at')

            if search:  # Search by task name or task description
                search = search.lower()
                queryset = queryset.filter(Q(task_name__icontains=search) | Q(task_description__icontains=search))
            if status:  # Filter tasks based on status
                queryset = queryset.filter(status__in=status)
            if priority:  # Filter tasks based on priority
                queryset = queryset.filter(priority__in=priority)

            result = self.get_paginated_data(queryset, page)
            return CommonUtils.dispatch_success(result)

        except Exception as e:
            return CommonUtils.dispatch_failure(Error.INTERNAL_SERVER_ERROR, str(e))

    def post(self, request):
        """
            Add a task
        """
        try:
            data = request.data
            data['user'] = request.user.id
            data['start_date'] = DateTimeUtils.convert_date_string_to_date(data['start_date'])
            data['end_date'] = DateTimeUtils.convert_date_string_to_date(data['end_date'])
            if not DateTimeUtils.get_date_difference(data['start_date'], data['end_date']):
                return CommonUtils.dispatch_failure(Error.END_DATE_GREATER_THAN_START_DATE)
            serializer = self.add_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return CommonUtils.dispatch_success(serializer.data)
            return CommonUtils.dispatch_failure(Error.VALIDATION_ERROR, serializer.errors)
        except Exception as e:
            return CommonUtils.dispatch_failure(Error.INTERNAL_SERVER_ERROR, str(e))

    def delete(self, request):
        try:
            task_ids = list(map(int, request.GET.getlist('task_id')))
            queryset = self.model.objects.filter(id__in=task_ids)
            queryset.update(is_active=False)
            return CommonUtils.dispatch_success(["DELETED SUCCESSFULLY"])
        except Exception as e:
            return CommonUtils.dispatch_failure(Error.INTERNAL_SERVER_ERROR, str(e))


class ToDoDetailView(BaseView):
    permission_classes = (IsAllowedUser, )
    model = ToDo
    serializer = ToDoListSerializer
    add_serializer = ToDoAddSerializer

    def get(self, request, todo_id):
        """
            Get detail of a particular task
        """
        try:
            todo_object = self.get_object(todo_id)
            if not todo_object:
                return CommonUtils.dispatch_failure(Error.DATA_NOT_FOUND)
            result = self.get_serialized_object(todo_object)
            return CommonUtils.dispatch_success(result)
        except Exception as e:
            return CommonUtils.dispatch_failure(Error.INTERNAL_SERVER_ERROR, str(e))

    def put(self, request, todo_id):
        """
            Update a particular task
        """
        try:
            data = request.data
            todo_object = self.get_object(todo_id)
            if not todo_object:
                return CommonUtils.dispatch_failure(Error.DATA_NOT_FOUND)
            if data.get('start_date'):
                data['start_date'] = DateTimeUtils.convert_date_string_to_date(data['start_date'])
                if data.get('end_date'):
                    end_date = DateTimeUtils.convert_date_string_to_date(data['end_date'])
                else:
                    end_date = todo_object.end_date
                if not DateTimeUtils.get_date_difference(data['start_date'], end_date):
                    return CommonUtils.dispatch_failure(Error.START_DATE_LESSER_THAN_END_DATE)
            if data.get('end_date'):
                data['end_date'] = DateTimeUtils.convert_date_string_to_date(data['end_date'])
                if data.get('start_date'):
                    start_date = DateTimeUtils.convert_date_string_to_date(data['start_date'])
                else:
                    start_date = todo_object.start_date
                if not DateTimeUtils.get_date_difference(start_date, data['end_date']):
                    return CommonUtils.dispatch_failure(Error.END_DATE_GREATER_THAN_START_DATE)
            serializer = self.add_serializer(todo_object, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return CommonUtils.dispatch_success(serializer.data)
            return CommonUtils.dispatch_failure(Error.VALIDATION_ERROR, serializer.errors)
        except Exception as e:
            return CommonUtils.dispatch_failure(Error.INTERNAL_SERVER_ERROR, str(e))
