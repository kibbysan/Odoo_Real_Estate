{
    "name": " Real Estate",
    "summary": "Test module",
    "version": "19.0.0.0.0",
    "license": "LGPL-3",
    "depends": ["base","crm","mail"],
    "data":[
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/estate_property_tag_view.xml",
        "views/estate_property_offer_view.xml",
        "views/estate_property_type_view.xml",
        "views/estate_property_views.xml",
        "views/estate_menu.xml"
    ],
    "application": True,
    "demo": [
        "data/demo.xml"
    ]
}