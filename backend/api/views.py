from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Comment, Ticket, Topic
from .permission import IsStaff
from services.serializer import CommentSerializer, TicketSerializer, TopicSerializer, UserSerializer
from rest_framework import status
# Create your views here.

#################### TICKET ####################


@swagger_auto_schema(
    method="get",
    operation_description='List of tickets for which the active user is a receiver',
    operation_summary='Ticket list received by the active user',
    responses={200: openapi.Response('OK', TicketSerializer(many=True)),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsStaff])
def ticketListReceiver(request):
    tickets = Ticket.objects.filter(receivers=request.user)
    if tickets.count() == 0:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


test_param = openapi.Parameter('creator_id', openapi.IN_PATH,
                               description="ID of Ticket Creator", type=openapi.TYPE_NUMBER)


@swagger_auto_schema(
    method="get",
    operation_description='List of tickets for which the active user is a creator',
    operation_summary='Ticket list created by the active user',
    responses={200: openapi.Response('OK', TicketSerializer(many=True)),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def ticketListCreator(request, pk):
    tickets = Ticket.objects.filter(creator=pk)
    if tickets.count() == 0:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="get",
    operation_description='List of tickets for a specific group',
    operation_summary='Ticket list for a specific group',
    responses={200: openapi.Response('OK', TicketSerializer(many=True)),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsStaff])
def ticketListGroup(request, pk):
    tickets = Ticket.objects.filter(groups__id=pk)
    if tickets.count() == 0:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="get",
    operation_description='List of ticket receivers',
    operation_summary='List of ticket receivers',
    responses={200: openapi.Response('OK', UserSerializer(many=True)),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def ticketReceiversList(request, pk):
    try:
        ticket = Ticket.objects.get(id=pk)
    except Ticket.DoesNotExist:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = TicketSerializer(ticket, many=False)
    return Response(serializer.data['receivers'], status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="get",
    operation_description='Returns all information of a ticket',
    operation_summary='Ticket detail',
    responses={200: openapi.Response('OK', TicketSerializer),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def ticketDetail(request, pk):
    try:
        ticket = Ticket.objects.get(id=pk)
    except Ticket.DoesNotExist:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = TicketSerializer(ticket, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="post",
    operation_description='Creation of a new Ticket',
    operation_summary='Ticket Creation',
    request_body=TicketSerializer,
    responses={201: openapi.Response('Created', TicketSerializer),
               400: openapi.Response('Bad Request')})
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def ticketCreate(request):
    serializer = TicketSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="put",
    operation_description='Change of ticket status for creator who can only put Closed or Open',
    operation_summary='Ticket status update for Creator',
    request_body=TicketSerializer,
    responses={200: openapi.Response('OK', TicketSerializer),
               400: openapi.Response('Bad Request'),
               404: openapi.Response('Not Found')})
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def ticketCreatorUpdate(request, pk):
    serializer = TicketSerializer(data=request.data)
    if (serializer.is_valid()):
        if request.data['status'] not in ('CL', 'OP'):
            return Response('Only Closed or Open are possible', status=status.HTTP_400_BAD_REQUEST)
        try:
            ticket = Ticket.objects.get(id=pk, creator=request.user)
        except Ticket.DoesNotExist:
            return Response('Not Found', status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    serializer = TicketSerializer(instance=ticket, data=request.data)
    if (serializer.is_valid()):
        serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="put",
    operation_description='Change of ticket status for receiver who can only put Pending or Resolved',
    operation_summary='Ticket status update for Receiver',
    request_body=TicketSerializer,
    responses={200: openapi.Response('OK', TicketSerializer),
               400: openapi.Response('Bad Request'),
               404: openapi.Response('Not Found')})
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def ticketReceiverUpdate(request, pk):
    serializer = TicketSerializer(data=request.data)
    if (serializer.is_valid()):
        if request.data['status'] not in ('PE', 'RE'):
            return Response('Only Pendign or Resolved are possible', status.HTTP_400_BAD_REQUEST)
        try:
            ticket = Ticket.objects.get(id=pk, receivers=request.user)
        except Ticket.DoesNotExist:
            return Response('Not Found', status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    serializer = TicketSerializer(instance=ticket, data=request.data)
    if (serializer.is_valid()):
        serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)


# TODO
# lo staff può mettere in qualsiasi stato, per comodità.. però tranne expired, che dipende dalla data
# nel caso, per uno dello staff sarebbe meglio cambiare la data
# pk identifica il ticket
@swagger_auto_schema(
    method="put",
    operation_description='Change of ticket status for is_staff user who can put every state',
    operation_summary='Ticket status update for is_staff user',
    request_body=TicketSerializer,
    responses={200: openapi.Response('OK', TicketSerializer),
               400: openapi.Response('Bad Request'),
               404: openapi.Response('Not Found')})
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsStaff])
def ticketStaffUpdate(request, pk):
    serializer = TicketSerializer(data=request.data)
    if (serializer.is_valid()):
        if request.data['status'] in ('EX'):
            return Response('Expired is not possible', status=status.HTTP_400_BAD_REQUEST)
        try:
            ticket = Ticket.objects.get(id=pk)
        except Ticket.DoesNotExist:
            return Response('Not Found', status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    serializer = TicketSerializer(instance=ticket, data=request.data)
    if (serializer.is_valid()):
        serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="delete",
    operation_description='Delete of a ticket',
    operation_summary='Delete of a ticket',
    responses={200: openapi.Response('Delete OK'),
               404: openapi.Response('Not Found')})
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsStaff])
def ticketDelete(request, pk):
    try:
        ticket = Ticket.objects.get(id=pk)
    except Ticket.DoesNotExist:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    ticket.delete()

    return Response('Delete OK', status=status.HTTP_200_OK)


#################### TOPIC ####################

@swagger_auto_schema(
    method="get",
    operation_description='Retrieve all topic information',
    operation_summary='Get topic Detail',
    responses={200: openapi.Response('OK', TopicSerializer),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def topicDetail(request, pk):
    try:
        topic = Topic.objects.get(id=pk)
    except Topic.DoesNotExist:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = TopicSerializer(topic, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="get",
    operation_description='List of topics of a particular group ',
    operation_summary='List of topics of a group',
    responses={200: openapi.Response('OK', TopicSerializer(many=True)),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def topicGroupList(request, pk):
    topics = Topic.objects.filter(group__name=pk)
    if topics.count() == 0:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# TODO
# OCCHIO CHE QUA DENTRO NON ABBIAMO LE STRUTTURE DATI, SOLO GLI ID
# lista dei topic di un gruppo a cui l'utente è iscritto
# pk è il gruppo
@swagger_auto_schema(
    method="get",
    operation_description='List of topics of a group to which the active user is subscribed',
    operation_summary='List of topics of a group user is subscribed',
    responses={200: openapi.Response('OK', TopicSerializer(many=True)),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def topicsUserGroupList(request, pk):
    topics = Topic.objects.filter(group=pk, users=request.user.id)
    if topics.count() == 0:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="get",
    operation_description='List of topics to which a staff user is not subscribed',
    operation_summary='List of topics is_staff user is not subscribed',
    responses={200: openapi.Response('OK', TopicSerializer(many=True)),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsStaff])
def topicNotStaffList(request):
    topics = Topic.objects.exclude(
        Topic.objects.filter(users_id=request.user.id))
    if topics.count() == 0:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# TODO
# questa non va
@swagger_auto_schema(
    method="get",
    operation_description='List of all topics of the groups to which active user belongs',
    operation_summary='List of all topics of the groups to which active user belongs',
    responses={200: openapi.Response('OK', TopicSerializer(many=True)),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def topicUserList(request):
    groups = request.user.groups
    topics = Topic.objects.filter(group__in=groups.all())
    if topics.count() == 0:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method="get",
    operation_description='List of users subscribed to the topic',
    operation_summary='List users subscribed to the topic',
    responses={200: openapi.Response('OK', UserSerializer(many=True)),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def topicUsers(request, pk):
    try:
        topic = Topic.objects.get(id=pk)  # oppure name=
    except Topic.DoesNotExist:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = TopicSerializer(topic, many=False)
    return Response(serializer.data['users'], status.HTTP_200_OK)


@swagger_auto_schema(
    method="post",
    operation_description='Creation of a new topic',
    operation_summary='Creation of a topic',
    request_body=TopicSerializer,
    responses={201: openapi.Response('Created', TopicSerializer),
               400: openapi.Response('Bad Request')})
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsStaff])
def topicCreate(request):
    serializer = TopicSerializer(data=request.data)
    if (serializer.is_valid()):
        serializer.save()
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method="put",
    operation_description='Subscribe user to selected topic',
    operation_summary='Add user to Topic',
    responses={200: openapi.Response('OK'),
               404: openapi.Response('Not Found')})
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def topicUsersAdd(request, pk):
    try:
        topic = Topic.objects.get(id=pk)  # oppure name=
    except Topic.DoesNotExist:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return Response('Not Found user', status=status.HTTP_404_NOT_FOUND)

    topic.users.add(user)

    return Response('You have been subscribed to the Topic', status.HTTP_200_OK)


@swagger_auto_schema(
    method="delete",
    operation_description='Delete of a topic',
    operation_summary='Delete of a topic',
    responses={200: openapi.Response('Delete OK'),
               404: openapi.Response('Not Found')})
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsStaff])
def topicDelete(request, pk):
    try:
        topic = Topic.objects.get(id=pk)
    except Topic.DoesNotExist:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    topic.delete()

    return Response('Delete OK', status=status.HTTP_200_OK)


#################### COMMENT ####################

@swagger_auto_schema(
    method="get",
    operation_description='Retrieve all comment information',
    operation_summary='Get comment info',
    responses={200: openapi.Response('OK', CommentSerializer),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def commentDetail(request, pk):
    try:
        comment = Comment.objects.get(id=pk)
    except Comment.DoesNotExist:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = CommentSerializer(comment, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="get",
    operation_description='List of Comments of a particular Ticket',
    operation_summary='List of Comments of a Ticket',
    responses={200: openapi.Response('OK', CommentSerializer(many=True)),
               404: openapi.Response('Not Found')})
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def commentTicketList(request, pk):
    try:
        ticket = Ticket.objects.get(id=pk)  # oppure name=
    except Topic.DoesNotExist:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    serializer = TicketSerializer(ticket, many=False)
    return Response(serializer.data['comments'], status.HTTP_200_OK)


@swagger_auto_schema(
    method="post",
    operation_description='Add a comment to a ticket',
    operation_summary='Add comment to ticket',
    request_body=CommentSerializer,
    responses={201: openapi.Response('Created', CommentSerializer),
               400: openapi.Response('Bad Request')})
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, ])
def commentCreate(request):
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    else:
        Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method="delete",
    operation_description='Delete of a Comment',
    operation_summary='Delete of a Comment',
    responses={200: openapi.Response('Delete OK'),
               404: openapi.Response('Not Found')})
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsStaff])
def commentDelete(request, pk):
    try:
        comment = Comment.objects.get(id=pk)
    except Comment.DoesNotExist:
        return Response('Not Found', status=status.HTTP_404_NOT_FOUND)

    comment.delete()
    return Response('Delete OK', status=status.HTTP_200_OK)
