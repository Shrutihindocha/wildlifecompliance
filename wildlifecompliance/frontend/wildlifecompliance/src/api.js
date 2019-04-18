var site_url = location.origin

module.exports = {
    organisations: '/api/organisations/',
    organisations_paginated: '/api/organisations_paginated/',
    organisation_requests: '/api/organisation_requests/',
    organisation_requests_paginated: '/api/organisation_requests_paginated/',
    organisation_contacts: '/api/organisation_contacts/',
    organisation_access_group_members: '/api/organisation_access_group_members/',
    users: '/api/users/',
    users_paginated: '/api/users_paginated/',
    my_user_details: '/api/my_user_details/',
    assessor_group:'/api/assessor_group/',
    emailidentities: '/api/emailidentities/',
    profiles: '/api/profiles/',
    my_profiles: '/api/my_profiles/',
    assessment:'/api/assessment/',
    assessment_paginated:'/api/assessment_paginated/',
    amendment:'/api/amendment/',
    is_new_user: '/api/is_new_user/',
    user_profile_completed: '/api/user_profile_completed/',
    countries: "https://restcountries.eu/rest/v1/?fullText=true/",
    application_type:"/api/application_type/",
    applications:"/api/application/",
    applications_paginated:"/api/application_paginated/",
    licences:"/api/licences/",
    licences_paginated:"/api/licences_paginated/",
    returns:"/api/returns/",
    application_standard_conditions:"/api/application_standard_conditions/",
    return_types:"/api/return_types/",
    application_conditions:"/api/application_conditions/",
    discard_application:function (id) {
      return `/api/application/${id}/`;
    },
    site_url: site_url,
    system_name: 'Wildlife Licensing System',
}

