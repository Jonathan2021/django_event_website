from res_framework import serializers
from .models import Association, EmailAddress, Member, Manager, President


class AssociationSerializer(serializers.HyperlinkeedModelSerializer):
    class Meta:
        model = Association
        fields = ('name')


class EmailAddressSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.ReadOnlyField(source='profile.get_full_name()')

    class Meta:
        model = EmailAddress
        fields = ('profile', 'email')


class MemberSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.ReadOnlyField(source='profile.get_full_name()')
    association = serializers.ReadOnlyField(source='association_id.name')

    class Meta:
        model = Member
        fields = ('profile', 'association')


class ManagerSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.ReadOnlyField(source='profile.get_full_name()')
    association = serializers.ReadOnlyField(source='association_id.name')

    class Meta:
        model = Manager
        fields = ('profile', 'association')


class PresidentSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.ReadOnlyField(source='profile.get_full_name()')
    association = serializers.ReadOnlyField(source='association_id.name')

    class Meta:
        model = President
        fields = ('profile', 'association')
