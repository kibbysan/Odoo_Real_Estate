# Real Estate Management Module for Odoo

## Overview

The **Real Estate** module is a comprehensive estate management solution for Odoo Community Edition (version 19.0) that enables users to manage properties, track offers, and streamline the real estate sales process. This module provides a complete workflow for listing properties, managing buyer offers, and tracking sales transactions.

## Module Information

- **Module Name:** Real Estate
- **Version:** 19.0.0.0.0
- **License:** LGPL-3
- **Odoo Version:** 19.0 Community Edition
- **Dependencies:** base, crm
- **Application Type:** Standalone Application

## Key Features

### 1. **Property Management**
The core functionality for managing real estate properties with comprehensive details:

- **Basic Information:**
  - Property title/name
  - Property description and additional information
  - Postcode/location
  - Date availability (defaults to 3 months from creation)
  - Property state tracking (New → Offer Received → Offer Accepted → Sold/Canceled)

- **Physical Characteristics:**
  - Number of bedrooms (default: 2)
  - Living area in square meters (default: 50)
  - Number of façades
  - Garage availability
  - Garden availability with automatic garden setup on selection
  - Garden area
  - Garden orientation (North, South, East, West)
  - **Computed Fields:**
    - Total area (living area + garden area)
    - Best offer (highest offer price received)

- **Pricing:**
  - Expected selling price (required, must be positive)
  - Actual selling price (auto-filled when offer accepted, read-only)

- **Categorization:**
  - Property type (Apartment, House, Villa, etc.)
  - Tags for additional classification and filtering

- **State Machine:**
  - **New:** Initial state when property is created
  - **Offer Received:** At least one offer has been received
  - **Offer Accepted:** An offer has been formally accepted
  - **Sold:** Property has been marked as sold
  - **Canceled:** Property listing has been canceled

### 2. **Offer Management**
Track and manage buyer offers for properties:

- **Offer Details:**
  - Offer price (must be positive)
  - Partner/buyer information
  - Linked property reference
  - Property type (linked from property)

- **Offer Validity:**
  - Configurable validity period (default: 7 days)
  - Automatic deadline calculation based on creation date
  - Inverse field: adjust validity by changing deadline date

- **Offer Status:**
  - **Accepted:** Buyer's offer has been formally accepted
  - **Refused:** Buyer's offer has been declined

- **Offer Actions:**
  - **Accept Offer:** Converts offer status to accepted, updates property selling price, changes property state to "Offer Accepted"
    - Built-in validation: prevents accepting multiple offers for the same property
  - **Refuse Offer:** Converts offer status to refused
    - Auto-clears selling price if the refused offer was the accepted one

### 3. **Property Type Management**
Categorize properties by type:

- Simple configuration interface for creating and managing property types
- Unique name constraint to prevent duplicates
- Examples: Apartment, House, Villa, Bungalow, etc.
- Used for filtering and organization

### 4. **Property Tags**
Flexible tagging system for properties:

- Add multiple tags to a single property
- Unique tag names to maintain data integrity
- Examples: Featured, Furnished, Modern, Garden, Near School, etc.
- Many-to-many relationship for flexible categorization

---

## Data Models

### 1. **estate.property** (Estate Property)
Main model representing a real estate property.

**Key Fields:**
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `name` | Char | Property title | Required |
| `state` | Selection | Current property state | Required, default='new' |
| `description` | Text | Full property description | Optional |
| `other_info` | Text | Additional information | Optional |
| `postcode` | Char | Location postcode | Optional |
| `date_availability` | Date | When property becomes available | Default: today + 3 months |
| `expected_price` | Float | Asking price | Required, >0 |
| `selling_price` | Float | Final sale price | Read-only, >=0 |
| `bedrooms` | Integer | Number of bedrooms | Default: 2 |
| `living_area` | Integer | Living space (m²) | Default: 50 |
| `facades` | Integer | Number of façades | Optional |
| `garage` | Boolean | Has garage | Optional |
| `garden` | Boolean | Has garden | Optional |
| `garden_area` | Integer | Garden size (m²) | Optional |
| `garden_orientation` | Selection | Garden direction | North/South/East/West |
| `total_area` | Integer | Total area (computed) | living_area + garden_area |
| `best_offer` | Float | Highest offer received (computed) | Max of all offer prices |
| `active` | Boolean | Record active status | Default: True |
| `property_type_id` | Many2one | Property type | Links to estate.property.type |
| `tag_ids` | Many2many | Associated tags | Links to estate.property.tag |
| `offer_ids` | One2many | Related offers | Links to estate.property.offer |

**SQL Constraints:**
- Expected price must be positive
- Selling price must be non-negative

**Computed Fields:**
- `total_area`: Automatically sums living area and garden area
- `best_offer`: Returns the maximum offer price or 0 if no offers exist

**Onchange Events:**
- When garden is enabled: automatically sets garden area to 10 m² and orientation to North
- When garden is disabled: clears garden area and orientation
- When availability date is set to past: shows warning notification

---

### 2. **estate.property.offer** (Estate Property Offer)
Model for managing offers on properties.

**Key Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `price` | Float | Offer amount | >0 |
| `status` | Selection | Accepted/Refused |
| `partner_id` | Many2one | Buyer information | Required, links to res.partner |
| `property_id` | Many2one | Associated property | Required, links to estate.property |
| `property_type_id` | Many2one | Property type (related) | Linked from property, stored |
| `validity` | Integer | Validity in days | Default: 7 |
| `date_deadline` | Date | Expiration date (computed) | Calculated from validity |

**SQL Constraints:**
- Offer price must be positive

**Key Methods:**
- `action_accept()`: Accepts an offer
  - Validates no other offer is already accepted
  - Sets offer status to 'accepted'
  - Updates property's selling_price
  - Changes property state to 'accepted'
  
- `action_refuse()`: Refuses an offer
  - Sets offer status to 'refused'
  - Clears property selling_price if this was the accepted offer

**Computed & Inverse Fields:**
- `date_deadline`: Automatically calculated as create_date + validity days
- Inverse setter: Adjust validity when deadline is changed manually

---

### 3. **estate.property.type** (Property Type)
Simple lookup model for property categorization.

**Key Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Type name | Required, Unique |

**SQL Constraints:**
- Type name must be unique

---

### 4. **estate.property.tag** (Property Tag)
Simple lookup model for property tagging.

**Key Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Tag name | Required, Unique |

**SQL Constraints:**
- Tag name must be unique

---

## Views

### Estate Property Views
Comprehensive views for managing properties:

1. **List View:**
   - Displays key property information in a table format
   - Columns: Name, Postcode, Bedrooms, Living Area, Expected Price, Selling Price, Date Availability
   - Quick overview of all properties

2. **Form View:**
   - **Header Section:** Action buttons for property status changes
     - "Mark as Sold" button
     - "Cancel Property" button
   - **Main Information:**
     - Property title with placeholder
     - Tags (displayed as colored badges)
     - Property type selection
     - Postcode and availability date
     - Expected price, best offer, and selling price
   - **Tabs:**
     - **Description Tab:** Physical details (bedrooms, living area, garage, garden, garden orientation, total area)
     - **Offers Tab:** Embedded view of all related offers
     - **Other Info Tab:** Additional property information

3. **Search View:**
   - Search by: Name, Postcode, Expected Price, Bedrooms, Living Area, Façades
   - Filters:
     - "Available" filter: Shows properties in 'New' or 'Offer Received' state
   - Prepared for future grouping by postcode (commented out)

### Estate Property Offer Views
- Detailed form views for managing offers
- Accept/Refuse action buttons
- Price, partner, and deadline information

### Estate Property Type & Tag Views
- Simple list and form views for configuration
- Quick management of property types and tags

---

## Menu Structure

The module adds a dedicated menu to Odoo with the following structure:

```
Real Estate (Root Menu)
├── Advertisements
│   ├── All Properties (property list view)
│   └── Offers (offer management)
└── Settings
    ├── Property Types (type configuration)
    └── Property Tags (tag configuration)
```

---

## Security & Access Control

The module includes role-based access control:

### User Groups:
1. **Regular Users (base.group_user):**
   - Read-only access to properties
   - Full CRUD access to property types, offers, and tags

2. **Estate Admin (estate_admin):**
   - Full CRUD access to all property records
   - Ability to manage and modify properties

### Access Rules (via ir.model.access.csv):
- Regular users can view but not modify properties
- Property types, offers, and tags are fully accessible to all users
- Admin group has complete control over all records

---

## Installation

### Prerequisites:
- Odoo 19.0 Community Edition
- Python 3.8+
- Required dependencies: base, crm modules

### Installation Steps:

1. **Copy Module to Custom Addons:**
   ```bash
   cp -r estate /path/to/odoo/custom_addons/
   ```

2. **Install in Odoo:**
   - Log in to Odoo with admin credentials
   - Go to **Apps** menu
   - Search for "Real Estate"
   - Click **Install**

3. **Post-Installation:**
   - Demo data will be automatically loaded
   - The module menu appears in the main navigation

---

## Usage Workflow

### Workflow 1: Creating and Listing a Property

1. Navigate to **Real Estate → Advertisements → All Properties**
2. Click **Create** to add a new property
3. Fill in required fields:
   - Property name/title
   - Expected selling price
   - Property details (bedrooms, living area, etc.)
4. Select property type and add tags for categorization
5. Set availability date (defaults to 3 months from now)
6. Save the property

### Workflow 2: Managing Offers

1. Navigate to a property in the list
2. Open the property form view
3. Go to the **Offers** tab
4. Add offers from interested buyers:
   - Select buyer (partner)
   - Enter offer price
   - Set validity period (default 7 days)
5. Once deadline passes, action is required

### Workflow 3: Accepting an Offer

1. Open a property with offers
2. Go to **Offers** tab
3. Click on the desired offer
4. Click **Accept Offer** button
   - System validates only one offer is accepted
   - Property selling price updates
   - Property state changes to "Offer Accepted"
5. Other offers can then be refused

### Workflow 4: Completing a Sale

1. After accepting an offer, property state is "Offer Accepted"
2. Once transaction is complete, click **Mark as Sold** button
3. Property state changes to "Sold"

### Workflow 5: Canceling a Property

1. If property is no longer available, click **Cancel Property** button
2. Property state changes to "Canceled"
3. Property remains in system for historical reference

---

## Demo Data

The module includes sample demo data in `data/demo.xml` that provides:
- Sample property listings
- Different property types
- Sample offers on properties
- Tags for categorization

Load demo data during installation for testing and evaluation purposes.

---

## Configuration

### Property Types Setup:
1. Navigate to **Real Estate → Settings → Property Types**
2. Create property types as needed:
   - Apartment
   - House
   - Villa
   - Bungalow
   - Townhouse
   - Studio
   - Other

### Property Tags Setup:
1. Navigate to **Real Estate → Settings → Property Tags**
2. Create tags for property characteristics:
   - Featured
   - Furnished
   - Modern
   - Garden
   - Garage
   - Pool
   - Near School

---

## Technical Architecture

### Module Structure:
```
estate/
├── __manifest__.py          # Module manifest with metadata
├── __init__.py              # Package initializer
├── models/
│   ├── __init__.py
│   ├── estate_property.py       # Main property model
│   ├── estate_property_offer.py # Offer model
│   ├── estate_property_type.py  # Type lookup
│   └── estate_property_tag.py   # Tag lookup
├── views/
│   ├── estate_menu.xml          # Menu structure
│   ├── estate_property_views.xml # Property views (list, form, search)
│   ├── estate_property_offer_view.xml
│   ├── estate_property_type_view.xml
│   └── estate_property_tag_view.xml
├── security/
│   ├── res_groups.xml           # User group definitions
│   └── ir.model.access.csv      # Access control rules
├── data/
│   └── demo.xml                 # Demo data
└── README.md                    # This file
```

### Key Technologies:
- **ORM:** Odoo ORM with relationships (Many2one, One2many, Many2many)
- **Computed Fields:** Dynamic field calculation using `@api.depends`
- **Constraints:** Both field-level and database-level validation
- **Workflows:** State machine pattern for property lifecycle
- **Date Handling:** `dateutil.relativedelta` for date calculations

---

## Future Enhancements

Potential features for future versions:

1. **Property Images:** Image gallery for property listings
2. **Advanced Search:** Filter by price range, area range, specific features
3. **Notifications:** Alerts when offers expire or new offers received
4. **Reports:** Sales analytics, property value trends, agent performance
5. **CRM Integration:** Link properties to CRM opportunities and customers
6. **Document Management:** Attach contracts, deeds, and inspection reports
7. **Property Valuation:** Automated pricing recommendations based on market data
8. **Viewing Appointments:** Schedule property viewings
9. **Commission Management:** Track commissions for sales agents
10. **API Integration:** Connect with external property listing platforms

---

## Troubleshooting

### Common Issues:

**Issue:** Module not appearing in Apps menu after installation
- **Solution:** Clear Odoo cache and refresh browser (Ctrl+Shift+R)

**Issue:** "Error: Check all installed modules" on installation
- **Solution:** Verify all dependencies (base, crm) are installed

**Issue:** Cannot modify properties as regular user
- **Solution:** Check security access rules; only Estate Admin group can modify properties

**Issue:** Multiple offers showing as accepted
- **Solution:** This should be prevented by validation; check database constraints

---

## Support & Contribution

This module is part of the Odoo Community Edition ecosystem. For:
- **Bug Reports:** Document issues with clear reproduction steps
- **Feature Requests:** Provide detailed use cases
- **Contributions:** Follow Odoo coding standards and provide comprehensive commit messages

---

## License

This module is distributed under the **LGPL-3 License** (GNU Lesser General Public License version 3). See LICENSE file for full terms.

---

## Author & Contributors

Created as a custom module for Odoo 19.0 Community Edition real estate management.

---

## Changelog

### Version 19.0.0.0.0
- Initial release
- Property management system
- Offer tracking and acceptance workflow
- Property type and tag management
- Role-based access control
- Search and filtering capabilities
