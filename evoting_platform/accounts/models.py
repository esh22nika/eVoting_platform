from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator, MinLengthValidator

class CustomAdminManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class CustomAdmin(AbstractUser):
    # username and email from AbstractUser
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)  # All CustomAdmins are staff by default
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = CustomAdminManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'admins'
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

    def __str__(self):
        return self.username

class Voter(models.Model):
    # Basic Information
    voter_id = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{3}[0-9]{7}$',
                message='Voter ID must be in format: 3 letters followed by 7 digits'
            )
        ]
    )
    password = models.CharField(max_length=128)  # Will store hashed password
    first_name = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(6)]
    )
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    
    # Personal Information
    mobile = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^[6-9][0-9]{9}$',
                message='Mobile number must be 10 digits and start with 6-9'
            )
        ]
    )
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other')
        ]
    )
    parent_spouse_name = models.CharField(max_length=100)
    
    # Address Information
    street_address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=r'^[1-9][0-9]{5}$',
                message='Pincode must be 6 digits starting with non-zero'
            )
        ]
    )
    place_of_birth = models.CharField(max_length=100)
    
    # Identity Information
    aadhar_number = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{12}$',
                message='Aadhar number must be 12 digits'
            )
        ]
    )
    pan_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{5}[0-9]{4}[A-Z]$',
                message='PAN must be in format: 5 letters, 4 digits, 1 letter'
            )
        ]
    )
    
    # Status Fields
    is_active = models.BooleanField(default=True)
    has_voted = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'voters'
        verbose_name = 'Voter'
        verbose_name_plural = 'Voters'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.voter_id})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'votes'
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'

    def __str__(self):
        return f"Vote by {self.voter.voter_id} at {self.timestamp}"
