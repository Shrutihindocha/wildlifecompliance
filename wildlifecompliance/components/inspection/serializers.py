import traceback

from rest_framework.fields import CharField
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometryField

from ledger.accounts.models import EmailUser, Address
from wildlifecompliance.components.call_email.serializers import LocationSerializer, LocationSerializerOptimized
from wildlifecompliance.components.inspection.models import (
    Inspection,
    InspectionUserAction,
    InspectionCommsLogEntry,
    InspectionType,
    InspectionFormDataRecord,
    )
from wildlifecompliance.components.main.related_item import get_related_items
from wildlifecompliance.components.main.serializers import CommunicationLogEntrySerializer
from wildlifecompliance.components.users.serializers import (
    ComplianceUserDetailsOptimisedSerializer,
    #CompliancePermissionGroupMembersSerializer
)
from rest_framework import serializers
from django.core.exceptions import ValidationError
from wildlifecompliance.components.main.fields import CustomChoiceField

from wildlifecompliance.components.users.serializers import (
    ComplianceUserDetailsOptimisedSerializer,
    #CompliancePermissionGroupMembersSerializer,
    UserAddressSerializer,
)
from wildlifecompliance.components.offence.serializers import OrganisationSerializer
from django.contrib.auth.models import Permission, ContentType


class InspectionTypeSerializer(serializers.ModelSerializer):
   class Meta:
       model = InspectionType
       # fields = '__all__'
       fields = (
               'id',
               'inspection_type',
               'description',
               )


class IndividualSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = (
            'id',
            'full_name',
            'email',
            'dob'
        )

    def get_full_name(self, obj):
        if obj.first_name:
            return obj.first_name + ' ' + obj.last_name
        else:
            return obj.last_name


class EmailUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    member_role = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    class Meta:
        model = EmailUser
        fields = (
            'id',
            'full_name',
            'member_role',
            'action'
        )

    def get_full_name(self, obj):
        if obj.first_name:
            return obj.first_name + ' ' + obj.last_name
        else:
            return obj.last_name

    def get_member_role(self, obj):
        inspection_team_lead_id = self.context.get('inspection_team_lead_id')
        if obj.id == inspection_team_lead_id:
            return 'Team Lead'
        else:
            return 'Team Member'

    def get_action(self, obj):
        inspection_team_lead_id = self.context.get('inspection_team_lead_id')
        if obj.id == inspection_team_lead_id:
            return 'Lead'
        else:
            return 'Member'


# class InspectionTeamSerializer(serializers.ModelSerializer):
#     inspection_team = EmailUserSerializer(many=True)
#
#     class Meta:
#         model = Inspection
#         fields = (
#             'inspection_team',
#             'inspection_team_lead_id'
#         )

class InspectionFormDataRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionFormDataRecord
        fields = (
            'field_name',
            'schema_name',
            'component_type',
            'instance_name',
            'comment',
            'deficiency',
            'value',
        )
        read_only_fields = (
            'field_name',
            'schema_name',
            'component_type',
            'instance_name',
            'comment',
            'deficiency',
            'value',
        )

class InspectionSerializer(serializers.ModelSerializer):
    inspection_team = serializers.SerializerMethodField()
    all_officers = serializers.SerializerMethodField()
    user_in_group = serializers.SerializerMethodField()
    can_user_action = serializers.SerializerMethodField()
    user_is_assignee = serializers.SerializerMethodField()
    status = CustomChoiceField(read_only=True)
    #inspection_team = EmailUserSerializer(many=True, read_only=True)
    individual_inspected = IndividualSerializer()
    organisation_inspected = OrganisationSerializer(read_only=True)
    #inspection_type = InspectionTypeSerializer()
    related_items = serializers.SerializerMethodField()
    inspection_report = serializers.SerializerMethodField()
    data = InspectionFormDataRecordSerializer(many=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = Inspection
        fields = (
                'id',
                'number',
                'status',
                'title',
                'details',
                'planned_for_date',
                'planned_for_time',
                'party_inspected',
                'assigned_to_id',
                'allocated_group',
                'user_in_group',
                'can_user_action',
                'user_is_assignee',
                'inspection_type_id',
                'inspection_team',
                'inspection_team_lead_id',
                'individual_inspected',
                'organisation_inspected',
                'individual_inspected_id',
                'organisation_inspected_id',
                'related_items',
                'inform_party_being_inspected',
                'call_email_id',
                'legal_case_id',
                'inspection_report',
                'schema',
                'region',
                'district',
                'data',
                'all_officers',
                'location',
                )
        read_only_fields = (
                'id',
                )

    def get_related_items(self, obj):
        return get_related_items(obj)

    def get_user_in_group(self, obj):
        return_val = False
        user_id = self.context.get('request', {}).user.id
        # inspection team should apply if status is 'open'
        if obj.status == 'open' and obj.inspection_team:
            for member in obj.inspection_team.all():
                if user_id == member.id:
                    return_val = True
        elif obj.allocated_group:
           for member in obj.allocated_group.get_members():
               if user_id == member.id:
                  return_val = True
        return return_val

    def get_can_user_action(self, obj):
        return_val = False
        user_id = self.context.get('request', {}).user.id

        if user_id == obj.assigned_to_id:
            return_val = True
        if obj.status == 'open' and obj.inspection_team and not obj.assigned_to_id:
            for member in obj.inspection_team.all():
                if user_id == member.id:
                    return_val = True
        elif obj.allocated_group and not obj.assigned_to_id:
           for member in obj.allocated_group.get_members():
               if user_id == member.id:
                  return_val = True
        return return_val

    def get_user_is_assignee(self, obj):
        return_val = False
        user_id = self.context.get('request', {}).user.id
        if user_id == obj.assigned_to_id:
            return_val = True

        return return_val

    def get_inspection_team(self, obj):
        team = [{
            'id': None,
            'full_name': '',
            'member_role': '',
            'action': ''
            }]

        returned_inspection_team = EmailUserSerializer(
                obj.inspection_team.all(), 
                context={
                     'inspection_team_lead_id': obj.inspection_team_lead_id
                },
                many=True
                )
        for member in returned_inspection_team.data:
            team.append(member)
        return team

    def get_allocated_group(self, obj):
        return ''
        #allocated_group = [{
        #    'email': '',
        #    'first_name': '',
        #    'full_name': '',
        #    'id': None,
        #    'last_name': '',
        #    'title': '',
        #    }]
        #returned_allocated_group = CompliancePermissionGroupMembersSerializer(instance=obj.allocated_group)
        #for member in returned_allocated_group.data['members']:
        #    allocated_group.append(member)

        #return allocated_group

    def get_all_officers(self, obj):
        return []
        #all_officer_objs = []
        #compliance_content_type = ContentType.objects.get(model="compliancepermissiongroup")
        #permission = Permission.objects.filter(codename='officer').filter(content_type_id=compliance_content_type.id).first()
        #for group in permission.group_set.all():
        #    for user in group.user_set.all():
        #        all_officer_objs.append(user)

        #unique_officers = list(set(all_officer_objs))
        #sorted_unique_officers = sorted(unique_officers, key=lambda officer: officer.last_name)

        #serialized_officers = IndividualSerializer(sorted_unique_officers, many=True)
        #returned_data = serialized_officers.data
        #blank_field = [{
        #    'dob': '',
        #    'email': '',
        #    'full_name': '',
        #    'id': None,
        #    }]

        #returned_data.insert(0, blank_field)
        #print(returned_data)
        #return returned_data

    def get_inspection_report(self, obj):
        return [[r.name, r._file.url] for r in obj.report.all()]
    
    # def get_region_id(self, obj):
    #     return obj.region_id
    
    # def get_district_id(self, obj):
    #     return obj.district_id

class SaveInspectionSerializer(serializers.ModelSerializer):
    assigned_to_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)
    allocated_group_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)
    inspection_type_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)
    individual_inspected_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)
    organisation_inspected_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)
    call_email_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)
    legal_case_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)
    location_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)

    class Meta:
        model = Inspection
        fields = (
                'id',
                'title',
                'details',
                'planned_for_date',
                'planned_for_time',
                'party_inspected',
                'assigned_to_id',
                'allocated_group_id',
                'inspection_type_id',
                'individual_inspected_id',
                'organisation_inspected_id',
                'inform_party_being_inspected',
                'call_email_id',
                'legal_case_id',
                'location_id',
                )
        read_only_fields = (
                'id',
                )

#class SaveInspectionSerializer(serializers.ModelSerializer):
 #   title = models.CharField(max_length=200, blank=True, null=True)
  #  details = models.TextField(blank=True, null=True)
   # number = models.CharField(max_length=50, blank=True, null=True)
    #planned_for_date = models.DateField(null=True)
    #planned_for_time = models.CharField(max_length=20, blank=True, null=True)



class InspectionUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')

    class Meta:
        model = InspectionUserAction
        fields = '__all__'


class InspectionCommsLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = InspectionCommsLogEntry
        fields = '__all__'
        read_only_fields = (
            'customer',
        )

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class InspectionOptimisedSerializer(serializers.ModelSerializer):
    location = LocationSerializerOptimized()

    class Meta:
        model = Inspection
        fields = (
            'id',
            'status',
            'location',
            'number',
        )
        read_only_fields = ('id', )


class InspectionDatatableSerializer(serializers.ModelSerializer):
    user_action = serializers.SerializerMethodField()
    inspection_type = InspectionTypeSerializer()
    planned_for = serializers.SerializerMethodField()
    status = CustomChoiceField(read_only=True)
    assigned_to = ComplianceUserDetailsOptimisedSerializer(read_only=True)
    inspection_team_lead = EmailUserSerializer()
    
    class Meta:
        model = Inspection
        fields = (
                'number',
                'title',
                'inspection_type',
                'status',
                'planned_for',
                'inspection_team_lead',
                'user_action',
                'assigned_to',
                'assigned_to_id',
                )

    def get_user_action(self, obj):
        user_id = self.context.get('request', {}).user.id
        view_url = '<a href=/internal/inspection/' + str(obj.id) + '>View</a>'
        process_url = '<a href=/internal/inspection/' + str(obj.id) + '>Process</a>'
        returned_url = ''

        if obj.status == 'closed':
            returned_url = view_url
        elif user_id == obj.assigned_to_id:
            returned_url = process_url
        if obj.status == 'open' and obj.inspection_team and not obj.assigned_to_id:
            for member in obj.inspection_team.all():
                if user_id == member.id:
                    returned_url = process_url
        elif (obj.allocated_group
                and not obj.assigned_to_id):
            for member in obj.allocated_group.get_members():
                if user_id == member.id:
                    returned_url = process_url

        if not returned_url:
            returned_url = view_url

        return returned_url

    def get_planned_for(self, obj):
        if obj.planned_for_date:
            if obj.planned_for_time:
                return obj.planned_for_date.strftime("%d/%m/%Y") + '  ' + obj.planned_for_time.strftime('%H:%M')
            else:
                return obj.planned_for_date.strftime("%d/%m/%Y")
        else:
            return None

class UpdateAssignedToIdSerializer(serializers.ModelSerializer):
    assigned_to_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)
    
    class Meta:
        model = Inspection
        fields = (
            'assigned_to_id',
        )

class InspectionTypeSchemaSerializer(serializers.ModelSerializer):
    inspection_type_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)        

    class Meta:
        model = Inspection
        fields = (
            'id',
            'schema',
            'inspection_type_id',
        )
        read_only_fields = (
            'id', 
            )
