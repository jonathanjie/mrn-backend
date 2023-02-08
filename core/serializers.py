from rest_framework import serializers

from core.models import (
    Company,
    Ship,
    ShipSpecs,
    ShipUser,
    User,
    UserProfile,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['uuid', 'name', 'link']
        read_only_fields = ['uuid']


class UserProfileSerializer(serializers.ModelSerializer):
    company = CompanySerializer()

    class Meta:
        model = UserProfile
        fields = ('uuid', 'company', 'role')


class ShipSpecsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipSpecs
        fields = ('flag', 'deadweight_tonnage', 'cargo_unit', 'fuel_options',
                  'lubricating_oil_options', 'machinery_options',
                  'propeller_pitch')


class ShipSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    shipspecs = ShipSpecsSerializer()

    class Meta:
        model = Ship
        fields = ['uuid', 'name', 'imo_reg',
                  'company', 'ship_type', 'shipspecs']
        read_only_fields = ['uuid', 'name', 'imo_reg', 'company']


class ShipUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipUser
        fields = '__all__'
        read_only_fields = ['uuid']
