class SocialAuthEmailNotExists(Exception):

    def __init__(self, msg):
        super(SocialAuthEmailNotExists, self).__init__()