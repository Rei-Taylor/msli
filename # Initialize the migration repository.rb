# Initialize the migration repository
flask db init

# Generate the initial migration
flask db migrate -m "Initial migration"

# Apply the initial migration
flask db upgrade

# Ensure your models have the indexes defined

# Generate the migration for indexes
flask db migrate -m "Add indexes to ColdStoreIn, ExportIn, and ProcessingIn models"

# Apply the migration for indexes
flask db upgrade