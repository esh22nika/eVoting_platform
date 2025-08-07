from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from .models import Voter, CustomAdmin

# Placeholder pages
def results_page(request):
    return render(request, 'results.html')

def contact_page(request):
    return render(request, 'contact.html')

def landing_page(request):
    return render(request, 'landing_page.html')

def auth_page(request):
    return render(request, 'auth.html')

@login_required
def admin_page(request):
    if not request.session.get('is_admin', False):
        return redirect('auth_page')
    return render(request, 'admin.html')

@login_required
def voter_page(request):
    if not request.session.get('voter_id'):
        return redirect('auth_page')
    voter = Voter.objects.get(voter_id=request.session['voter_id'])
    return render(request, 'voter.html', {'voter': voter})

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = request.POST
            voter_id = data.get('voterId')
            password = data.get('password')
            first_name = data.get('firstName')
            last_name = data.get('lastName')
            
            # Basic validation
            if not all([voter_id, password, first_name, last_name]):
                return JsonResponse({
                    'success': False,
                    'message': 'Please fill all required fields'
                })
            
            # Check if voter already exists
            if Voter.objects.filter(voter_id=voter_id).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Voter ID already registered'
                })

            if Voter.objects.filter(email=data.get('email')).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Email already registered'
                })

            if Voter.objects.filter(aadhar_number=data.get('aadharNumber')).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Aadhar number already registered'
                })

            if Voter.objects.filter(pan_number=data.get('panNumber')).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'PAN number already registered'
                })
            
            # Create new voter
            voter = Voter(
                voter_id=voter_id.upper(),
                password=make_password(password),  # Hash the password
                first_name=first_name,
                last_name=last_name,
                email=data.get('email'),
                mobile=data.get('mobile'),
                date_of_birth=data.get('dob'),
                gender=data.get('gender'),
                parent_spouse_name=data.get('parentSpouseName'),
                street_address=data.get('streetAddress'),
                city=data.get('city'),
                state=data.get('state'),
                pincode=data.get('pincode'),
                place_of_birth=data.get('placeOfBirth'),
                aadhar_number=data.get('aadharNumber'),
                pan_number=data.get('panNumber').upper()
            )
            
            # Save the voter to database
            voter.save()
            
            print(f"Registered new voter: {voter_id}")  # Debug log
            return JsonResponse({
                'success': True,
                'message': 'Registration successful'
            })
            
        except Exception as e:
            print(f"Registration error: {str(e)}")  # Debug log
            return JsonResponse({
                'success': False,
                'message': str(e) if settings.DEBUG else 'Registration failed. Please try again.'
            })
            
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@csrf_exempt
def do_login(request):
    if request.method == 'POST':
        try:
            # Get the voter_id and password from POST data
            voter_id = request.POST.get('voter_id', '').upper()
            password = request.POST.get('password', '')
            
            print(f"Login attempt for: {voter_id}")  # Debug log
            
            # Check if fields are empty
            if not voter_id or not password:
                return JsonResponse({
                    'success': False,
                    'message': 'Please fill all fields'
                })
            
            # Check if it's an admin login
            if voter_id.lower().startswith('admin'):
                try:
                    admin = CustomAdmin.objects.get(username=voter_id.lower())
                    if admin.check_password(password):
                        login(request, admin)
                        request.session['is_admin'] = True
                        print(f"Admin login successful: {voter_id}")  # Debug log
                        return JsonResponse({
                            'success': True,
                            'message': 'Login successful',
                            'role': 'admin'
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': 'Invalid password'
                        })
                except CustomAdmin.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'Admin account not found'
                    })

            # For voter login
            try:
                voter = Voter.objects.get(voter_id=voter_id)
                
                # Check if voter is active
                if not voter.is_active:
                    return JsonResponse({
                        'success': False,
                        'message': 'Account is inactive. Please contact support.'
                    })
                
                # Verify password
                if check_password(password, voter.password):
                    # Update last login time
                    voter.last_login = timezone.now()
                    voter.save(update_fields=['last_login'])
                    
                    # Store voter info in session
                    request.session['voter_id'] = voter_id
                    request.session['is_admin'] = False
                    
                    print(f"Voter login successful: {voter_id}")  # Debug log
                    return JsonResponse({
                        'success': True,
                        'message': 'Login successful',
                        'role': 'voter'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid password'
                    })
                    
            except Voter.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Voter ID not found'
                })
                
        except Exception as e:
            print(f"Login error: {str(e)}")  # Debug log
            return JsonResponse({
                'success': False,
                'message': str(e) if settings.DEBUG else 'Login failed. Please try again.'
            })
            
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })

@login_required
def logout_view(request):
    request.session.flush()
    return redirect('landing')
