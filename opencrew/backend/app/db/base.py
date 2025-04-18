# Import all the models, so that Base has them before being
# imported by Alembic
from ..models.user import User  # Add other models here as they are created
from ..models.resume import Resume # Add Resume model import
from ..models.job import Job # Add Job model import
from ..models.application import Application # Add Application model import
# from ..models.payment import Payment
from ..models.user import Base # Import Base from one of your models 