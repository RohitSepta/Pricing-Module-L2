# Pricing Module L2

## Features

- **Configurable Pricing**: Multiple pricing configurations that can be enabled/disabled
- **Differential Pricing**: Based on distance, time multipliers, and day of week
- **Django Admin Interface**: Easy-to-use admin interface for managing configurations
- **REST API**: Calculate pricing through API endpoints
- **Audit Logging**: Track all configuration changes with timestamps and actors
- **Comprehensive Testing**: Unit tests for all major functionality
- **Responsive UI**: Bootstrap-based frontend for price calculations

## Architecture

### Models
- **PricingConfiguration**: Main model storing pricing rules
- **PricingConfigurationLog**: Audit log for configuration changes

### Key Components
- **Distance Base Price (DBP)**: Base price for initial distance
- **Distance Additional Price (DAP)**: Price per km after base distance
- **Time Multiplier Factor (TMF)**: Tiered multipliers based on trip duration
- **Waiting Charges (WC)**: Charges for waiting time beyond free period

### Pricing Formula
```
    $Price = (DBP + (Dn * DAP)) + (Tn * TMF) + WC
```

## Installation & Setup

### Prerequisites
- Python 3.10+
- pip
- virtualenv (recommended)

### Step 1: Clone the Repository
```bash
git clone https://github.com/RohitSepta/Pricing-Module-L2.git
cd pricing_module_l2
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Settings
Create a `.env` file in the project root (optional):
```
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Step 5: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 7: Run the Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Usage

### Admin Interface
1. Go to `http://127.0.0.1:8000/admin/`
2. Login with superuser credentials
3. Navigate to "Pricing Configurations" to create/manage pricing rules

### Creating a Pricing Configuration
1. Click "Add Pricing Configuration"
2. Fill in the details:
   - **Name**: Unique identifier
   - **Applicable Days**: Select days of the week
   - **Distance Base Price**: Base price for initial distance
   - **Base Distance KM**: Initial distance covered by base price
   - **Distance Additional Price**: Price per km after base distance
   - **Time Multiplier Config**: JSON format for time-based multipliers
   - **Waiting Charges**: Configuration for waiting time charges

### Example Time Multiplier Configuration
```json
{
  "1": 1.0,
  "2": 1.25,
  "3": 2.2
}
```
This means:
- Under 1 hour: 1x multiplier
- 1-2 hours: 1.25x multiplier  
- 2-3 hours: 2.2x multiplier

### Frontend Calculator
Visit `http://127.0.0.1:8000/` to use the price calculator interface.

## API Endpoints

### Calculate Price
**POST** `/api/calculate-price/`

Request Body:
```json
{
  "distance_km": 8.5,
  "total_time_hours": 1.5,
  "waiting_time_minutes": 10,
  "day_of_week": "monday"
}
```

Response:
```json
{
  "total_price": 245.50,
  "breakdown": {
    "distance_base_price": 80.0,
    "base_distance_km": 3.0,
    "additional_distance_km": 5.5,
    "distance_additional_cost": 165.0,
    "total_distance_cost": 245.0,
    "time_multiplier": 1.25,
    "time_adjusted_cost": 306.25,
    "waiting_charges": 15.0,
    "total_price": 321.25
  },
  "configuration_used": {
    "id": 1,
    "name": "Weekday Standard",
    "description": "Standard pricing for weekdays"
  }
}
```

### List Configurations
**GET** `/api/pricing-configs/`

## Testing

Run the complete test suite:
```bash
python manage.py test
```

Run specific test modules:
```bash
python manage.py test pricing.tests.PricingCalculationTest
```

## Project Structure

```
pricing_module_l2/
├── pricing_module_l2/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── calculate_price/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templates/
│   └──|
│      └── calculator.html
├── manage.py
├── requirements.txt
└── README.md
```

## Database Schema

### PricingConfiguration
- `id`: Primary key
- `name`: Configuration name (unique)
- `description`: Optional description
- `is_active`: Boolean flag for enabling/disabling
- `created_at`: Timestamp
- `created_by`: Foreign key to User
- `distance_base_price`: Decimal field for base price
- `base_distance_km`: Decimal field for base distance
- `applicable_days`: JSON field for days of week
- `distance_additional_price`: Decimal field for additional price per km
- `time_multiplier_config`: JSON field for time multipliers
- `waiting_charge_per_interval`: Decimal field for waiting charges
- `waiting_interval_minutes`: Integer field for waiting intervals
- `waiting_free_minutes`: Integer field for free waiting time

### PricingConfigurationLog
- `id`: Primary key
- `configuration`: Foreign key to PricingConfiguration
- `action`: Choice field (created, updated, deleted, etc.)
- `actor`: Foreign key to User
- `timestamp`: Timestamp
- `changes`: JSON field for change details

## Business Logic

### Price Calculation Flow
1. Find active configuration for the given day
2. Calculate base distance cost (DBP)
3. Calculate additional distance cost (DAP)
4. Apply time multiplier (TMF)
5. Calculate waiting charges (WC)
6. Sum all components for final price

### Configuration Management
- Multiple configurations can exist simultaneously
- Only active configurations are used for calculations
- Business team can enable/disable configurations as needed
- All changes are logged with actor and timestamp

## Validation

### Form Validation
- Positive values for all pricing fields
- Valid JSON format for time multipliers
- Required fields validation
- Unique configuration names

### API Validation
- Input parameter validation
- Business rule validation
- Error handling with appropriate HTTP status codes

## Error Handling

- Graceful error handling for missing configurations
- Detailed error messages for validation failures
- Fallback mechanisms for edge cases
- Comprehensive logging for debugging

## Security Considerations

- CSRF protection for forms
- Input validation and sanitization
- SQL injection prevention through ORM
- Authentication required for admin access

## Performance Considerations

- Database indexing on frequently queried fields
- Efficient query optimization
- JSON field usage for flexible configuration
- Minimal API response payload

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request