from rest_framework import exceptions
from rest_framework.response import Response
from rest_social_auth.serializers import UserTokenSerializer
from rest_social_auth.views import SocialSessionAuthView, decorate_request
from social_core.utils import parse_qs

from socialapp.exceptions import SocialAuthEmailNotExists
from socialapp.serializers import SocialSignUpSerializer
from rest_framework.authentication import TokenAuthentication

class MySocialView(SocialSessionAuthView):
    serializer_class = SocialSignUpSerializer
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider_name = serializer.validated_data['provider']
        decorate_request(request, provider_name)
        authed_user = request.user if not request.user.is_anonymous() else None
        token = serializer.validated_data['access_token']
        if self.oauth_v1() and request.backend.OAUTH_TOKEN_PARAMETER_NAME not in serializer.validated_data:
            request_token = parse_qs(request.backend.set_unauthorized_token())
            return Response(request_token)
        print(dir(request.backend))
        try:
            user = request.backend.do_auth(token, user=authed_user)
        except SocialAuthEmailNotExists:
            raise exceptions.ParseError({'error': "email id not found."})
        except Exception as e:
            return Response({'error': str(e)})
        data = UserTokenSerializer(instance=user).data
        if user.screen_name and user.draw_location:
            data['is_profile_complete'] = True
        else:
            data['is_profile_complete'] = False
        return Response(data)

