<template lang="html">
    <div id="CreateInspection">
        <modal transition="modal fade" @ok="ok()" @cancel="cancel()" title="Create New Inspection" large force>
          <div class="container-fluid">
            <div class="row">
                <div class="col-sm-12">
                        <div class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>Region</label>
                            </div>
                            <div class="col-sm-9">
                              <select class="form-control col-sm-9" @change.prevent="updateDistricts()" v-model="region_id">
                                <option  v-for="option in regions" :value="option.id" v-bind:key="option.id">
                                  {{ option.name }} 
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>
                        <div class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>District</label>
                            </div>
                            <div class="col-sm-9">
                              <select class="form-control" @change.prevent="updateAllocatedGroup()" v-model="district_id">
                                <option  v-for="option in availableDistricts" :value="option.district_id" v-bind:key="option.district_id">
                                  {{ option.district_name }} 
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>
                        <div class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>Allocate to</label>
                            </div>
                            <div class="col-sm-9">
                              <select class="form-control" v-model="assigned_to_id">
                                <option  v-for="option in allocatedGroup" :value="option.id" v-bind:key="option.id">
                                  {{ option.full_name }} 
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>

                        <div class="form-group">
                          <div class="row">
                            <div class="col-sm-3">
                              <label>Inspection Type</label>
                            </div>
                            <div class="col-sm-9">
                              <select class="form-control" v-model="inspection_type_id">
                                <option  v-for="option in inspectionTypes" :value="option.id" v-bind:key="option.id">
                                  {{ option.inspection_type }}
                                </option>
                              </select>
                            </div>
                          </div>
                        </div>

                        <div class="form-group">
                          <div class="row">
                              <div class="col-sm-3">
                                  <label class="control-label pull-left" for="details">Details</label>
                              </div>
            			      <div class="col-sm-6">
                                  <textarea class="form-control" placeholder="add details" id="details" v-model="inspectionDetails"/>
                              </div>
                          </div>
                        </div>
                        <div class="form-group">
                            <div class="row">
                                <div class="col-sm-3">
                                    <label class="control-label pull-left"  for="Name">Attachments</label>
                                </div>
            			        <div class="col-sm-9">
                                    <filefield 
                                    ref="comms_log_file" 
                                    name="comms-log-file" 
                                    :isRepeatable="true" 
                                    documentActionUrl="temporary_document" 
                                    @update-temp-doc-coll-id="setTemporaryDocumentCollectionId"/>
                                </div>
                            </div>
                        </div>

                </div>
              
            </div>
          </div>
            <div slot="footer">
                <div v-if="errorResponse" class="form-group">
                    <div class="row">
                        <div class="col-sm-12">
                            <strong>
                                <span style="white-space: pre;">{{ errorResponse }}</span>
                            </strong>
                        </div>
                    </div>
                </div>
                <button type="button" class="btn btn-default" @click="ok">Ok</button>
                <button type="button" class="btn btn-default" @click="cancel">Cancel</button>
            </div>
        </modal>
    </div>
</template>
<script>
import Vue from "vue";
import modal from '@vue-utils/bootstrap-modal.vue';
import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
import { api_endpoints, helpers, cache_helper } from "@/utils/hooks";
import filefield from '@/components/common/compliance_file.vue';
import { required, minLength, between } from 'vuelidate/lib/validators'

export default {
    name: "CreateInspection",
    data: function() {
      return {
            officers: [],
            isModalOpen: false,
            processingDetails: false,
            form: null,
            regions: [],
            availableDistricts: [],
            casePriorities: [],
            inspectionTypes: [],
            externalOrganisations: [],
            inspectionDetails: '',
            errorResponse: "",
            region_id: null,
            district_id: null,
            assigned_to_id: null,
            inspection_type_id: null,
            advice_details: "",
            allocatedGroup: [],
            allocated_group_id: null,
            documentActionUrl: '',
            temporary_document_collection_id: null,
      }
    },
    components: {
      modal,
      filefield,
    },
    validations: {
        region_id: {
            required,
        },
        assigned_to_id: {
            required,
        },
        inspection_type_id: {
            required,
        },
    },
    computed: {
      ...mapGetters('inspectionStore', {
        inspection: "inspection",
      }),
      ...mapGetters('callemailStore', {
        call_email: "call_email",
      }),
      ...mapGetters('legalCaseStore', {
        legal_case: "legal_case",
      }),
      parent_legal_case: function() {
          if (this.legal_case && this.legal_case.id) {
              return true;
          }
      },
      parent_call_email: function() {
          if (this.call_email && this.call_email.id) {
              return true;
          }
      },
    },
    filters: {
      formatDate: function(data) {
          return data ? moment(data).format("DD/MM/YYYY HH:mm:ss") : "";
      }
    },
    methods: {
      ...mapActions('inspectionStore', {
          saveInspection: 'saveInspection',
          loadInspection: 'loadInspection',
          setInspection: 'setInspection',
      }),
      ...mapActions({
          loadAllocatedGroup: 'loadAllocatedGroup',
      }),
      ...mapActions('callemailStore', {
          loadCallEmail: 'loadCallEmail',
      }),
      ...mapActions('legalCaseStore', {
          loadLegalCase: 'loadLegalCase',
      }),
      setTemporaryDocumentCollectionId: function(val) {
          this.temporary_document_collection_id = val;
      },
      updateDistricts: function() {
        this.availableDistricts = [];
        for (let region of this.regions) {
          if (this.region_id === region.id) {
            this.availableDistricts=region.districts
          }
        }
        this.availableDistricts.splice(0, 0, 
        {
          district_id: "", 
          district_name: "",
          district: "",
          districts: [],
          region: null,
        });
        // ensure security group members list is up to date
        // this.updateAllocatedGroup();
      },
      updateAllocatedGroup: async function() {
          this.errorResponse = "";
          Vue.set(this, 'allocatedGroup', []);
          if (this.region_id) {
              let allocatedGroupResponse = await this.loadAllocatedGroup({
                workflow_type: 'allocate_for_inspection',
                region_id: this.region_id,
                district_id: this.district_id ? this.district_id : null,
              });
              if (allocatedGroupResponse.ok) {
                  Vue.set(this, 'allocatedGroup', allocatedGroupResponse.body);
                  this.allocated_group_id = allocatedGroupResponse.body.group_id;
              } else {
                  // Display http error response on modal
                  this.errorResponse = allocatedGroupResponse.statusText;
              }
              // Display empty group error on modal
              if (!this.errorResponse &&
                  this.allocatedGroup &&
                  this.allocatedGroup.length <= 1) {
                  this.errorResponse = 'This group has no members';
              }
          } else {
              this.allocatedGroup = [];
          }
      },

      ok: async function () {
          let is_valid_form = this.isValidForm();
          if (is_valid_form) {
              const response = await this.sendData();
              if (response.ok) {
                  const returnedInspection = response.body;
                  // For Inspection Dashboard
                  if (this.$parent.$refs.inspection_table) {
                      this.$parent.$refs.inspection_table.vmDataTable.ajax.reload()
                  }
                  // For related items table
                  let parent_update_function_payload = null;
                  if (this.parent_call_email) {
                      await this.loadCallEmail({
                          call_email_id: this.call_email.id,
                      });
                  } else if (this.parent_legal_case) {
                      await this.loadLegalCase({
                          legal_case_id: this.legal_case.id,
                      });
                  }
                  if (this.$parent.$refs.related_items_table) {
                      this.$parent.constructRelatedItemsTable();
                  }
                  if (returnedInspection && returnedInspection.id) {
                      this.$emit(
                          'inspection-created', 
                          {
                              'inspection': returnedInspection.id,
                          });
                  }
                  this.close();
                  //this.$router.push({ name: 'internal-inspection-dash' });
              }
          }
      },
      isValidForm: function() {
          this.$v.$touch();
          if (this.$v.$invalid) {
              this.errorResponse = 'Invalid form:\n';
              if (this.$v.region_id.$invalid) {
                  this.errorResponse += 'Region is required\n';
              }
              if (this.$v.assigned_to_id.$invalid) {
                  this.errorResponse += 'Officer must be assigned\n';
              }
              if (this.$v.inspection_type_id.$invalid) {
                  this.errorResponse += 'Choose Inspection Type\n';
              }
              return false;
          } else {
              return true;
          }
      },
      cancel: async function() {
          await this.$refs.comms_log_file.cancel();
          this.isModalOpen = false;
          this.close();
      },
      close: function () {
          let vm = this;
          this.isModalOpen = false;
      },
      sendData: async function() {
          let post_url = '';
          if (!this.inspection.id) {
              post_url = '/api/inspection/';
          } else {
              post_url = '/api/inspection/' + this.inspection.id + '/workflow_action/';
          }
          
          let payload = new FormData();
          payload.append('details', this.inspectionDetails);
          this.$refs.comms_log_file.commsLogId ? payload.append('inspection_comms_log_id', this.$refs.comms_log_file.commsLogId) : null;
          this.parent_call_email ? payload.append('call_email_id', this.call_email.id) : null;
          this.parent_legal_case ? payload.append('legal_case_id', this.legal_case.id) : null;
          this.district_id ? payload.append('district_id', this.district_id) : null;
          this.assigned_to_id ? payload.append('assigned_to_id', this.assigned_to_id) : null;
          this.inspection_type_id ? payload.append('inspection_type_id', this.inspection_type_id) : null;
          this.region_id ? payload.append('region_id', this.region_id) : null;
          this.allocated_group_id ? payload.append('allocated_group_id', this.allocated_group_id) : null;
          this.temporary_document_collection_id ? payload.append('temporary_document_collection_id', this.temporary_document_collection_id.temp_doc_id) : null;

          this.workflow_type ? payload.append('workflow_type', this.workflow_type) : null;
          !payload.has('allocated_group') ? payload.append('allocated_group', this.allocatedGroup) : null;

          try {
              let res = await Vue.http.post(post_url, payload);
              if (res.ok) {
                  return res
              }
          } catch(err) {
                  this.errorResponse = 'Error:' + err.statusText;
              }
          
      },
      createDocumentActionUrl: async function(done) {
        if (!this.inspection.id) {
            // create inspection and update vuex
            let returned_inspection = await this.saveInspection({ create: true, internal: true })
            await this.loadInspection({inspection_id: returned_inspection.body.id});
        }
        // populate filefield document_action_url
        this.$refs.comms_log_file.document_action_url = this.inspection.createInspectionProcessCommsLogsDocumentUrl;
        return done(true);
      },

    },
    created: async function() {
        // regions
        
        let returned_regions = await cache_helper.getSetCacheList('Regions', '/api/regions/');
        Object.assign(this.regions, returned_regions);

        // blank entry allows user to clear selection
        this.regions.splice(0, 0, 
            {
              id: "", 
              display_name: "",
              district: "",
              districts: [],
              region: null,
            });

        // inspection_types
        let returned_inspection_types = await cache_helper.getSetCacheList(
            'InspectionTypes',
            api_endpoints.inspection_types
            );
        Object.assign(this.inspectionTypes, returned_inspection_types);
        // blank entry allows user to clear selection
        this.inspectionTypes.splice(0, 0, 
            {
              id: "", 
              description: "",
            });
        // If exists, get parent component details from vuex
        if (this.parent_call_email) {
             // Set region_id and district_id based on GIS lookup
          if (this.call_email && this.call_email.region_gis) {
              const region = this.regions.find(obj => obj.name === this.call_email.region_gis)
              if (region) {
                  this.region_id = region.id
                  if (this.call_email.district_gis) {
                      const district = region.districts.find(obj => obj.district_name === this.call_email.district_gis)
                      if (district) {
                          this.district_id = district.district_id
                      }
                  }
              }
          }
        }
        
        // If no Region/District selected, initialise region as Kensington
        // if (!this.regionDistrictId) {
        //     for (let record of this.regionDistricts) {
        //         if (record.district === 'KENSINGTON') {
        //             this.district_id = null;
        //             this.region_id = record.id;
        //         }
        //     }
        // }
        
        // ensure availableDistricts and allocated group is current
        this.updateDistricts();
        // await this.updateAllocatedGroup();
        
    },
};
</script>

<style lang="css">
.btn-file {
    position: relative;
    overflow: hidden;
}
.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
.top-buffer{margin-top: 5px;}
.top-buffer-2x{margin-top: 10px;}
</style>
