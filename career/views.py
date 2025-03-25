import json
import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from datetime import datetime, timedelta  # Add timedelta import here
import requests
import json
import os
import re
import random

# Get API key
YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY

# Career domain skills mapping
# Update TECH_DOMAINS constant to include art and design fields
TECH_DOMAINS = {
    "web_development": ["HTML", "CSS", "JavaScript", "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask"],
    "data_science": ["Python", "R", "SQL", "Machine Learning", "Statistics", "Data Visualization", "NumPy", "Pandas"],
    "devops": ["Docker", "Kubernetes", "AWS", "Azure", "CI/CD", "Jenkins", "Terraform", "Linux"],
    "mobile_development": ["React Native", "Flutter", "Swift", "Kotlin", "iOS", "Android"],
    "cybersecurity": ["Network Security", "Cryptography", "Ethical Hacking", "Security Tools", "Penetration Testing"],
    # Add art and design domains
    "graphic_design": ["Adobe Illustrator", "Adobe Photoshop", "Typography", "Color Theory", "Layout Design", "Logo Design", "Brand Identity", "Print Design", "Adobe InDesign"],
    "ui_design": ["UI Principles", "Figma", "Sketch", "Adobe XD", "Wireframing", "Prototyping", "Design Systems", "User Flows", "Visual Design"],
    "ux_design": ["User Research", "Usability Testing", "Information Architecture", "UX Writing", "User Personas", "Journey Mapping", "Accessibility", "Interaction Design"],
    "digital_art": ["Digital Painting", "Digital Illustration", "Procreate", "Concept Art", "Character Design", "Environment Design", "Digital Sculpting", "Texture Creation"],
    "traditional_art": ["Drawing Fundamentals", "Painting Techniques", "Color Theory", "Composition", "Perspective", "Anatomy", "Still Life", "Figure Drawing"],
    "animation": ["After Effects", "Character Animation", "Motion Graphics", "Storyboarding", "3D Animation", "2D Animation", "Rigging", "Animation Principles"]
}



@csrf_exempt
@require_http_methods(["POST"])
def generate_roadmap(request):
    """Generate personalized career roadmap based on industry data sources"""
    try:
        # Parse the request data
        data = json.loads(request.body)
        
        # Extract data with simple defaults
        current_skills = data.get('skills', [])
        if isinstance(current_skills, str):
            current_skills = [skill.strip() for skill in current_skills.split(',') if skill.strip()]
            
        career_goal = data.get('goal', '').lower()
        experience_level = data.get('experienceLevel', 'beginner')
        
        # Generate a dynamic roadmap based on career trends data
        required_skills = identify_required_skills(career_goal)
        
        # Create phases based on the required skills and user experience
        phases = generate_career_phases(required_skills, current_skills, experience_level, career_goal)
        
        # Calculate estimated time to completion
        estimated_completion = calculate_estimated_completion(phases, experience_level)
        
        # Build the complete roadmap
        roadmap = {
            'career_goal': career_goal,
            'required_skills': required_skills,
            'estimated_completion': estimated_completion,
            'phases': phases
        }
        
        return JsonResponse({
            'success': True,
            'roadmap': roadmap
        })
    except Exception as e:
        # Get the full traceback for debugging
        error_traceback = traceback.format_exc()
        print(f"Error in generate_roadmap: {e}")
        print(error_traceback)
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def identify_required_skills(goal):
    """Identify skills required for a career goal based on job data"""
    goal_lower = goal.lower()
    
    # Direct domain matching first (e.g., "graphic design" -> graphic_design)
    for domain, skills in TECH_DOMAINS.items():
        domain_name = domain.replace('_', ' ')
        if domain_name in goal_lower:
            return skills[:10]  # Return top skills for this domain
    
    # If no direct domain match, check for keywords
    # Art & Design fields
    if any(keyword in goal_lower for keyword in ['artist', 'art', 'paint', 'draw']):
        if 'digital' in goal_lower:
            return TECH_DOMAINS["digital_art"]
        return TECH_DOMAINS["traditional_art"]
    
    elif any(keyword in goal_lower for keyword in ['ui', 'interface']):
        return TECH_DOMAINS["ui_design"]
    
    elif any(keyword in goal_lower for keyword in ['ux', 'user experience']):
        return TECH_DOMAINS["ux_design"]
    
    elif any(keyword in goal_lower for keyword in ['graphic', 'design', 'designer']):
        return TECH_DOMAINS["graphic_design"]
    
    elif any(keyword in goal_lower for keyword in ['motion', 'animation', 'animate']):
        return TECH_DOMAINS["animation"]
    
    # Tech fields - keep these checks for backward compatibility
    elif any(keyword in goal_lower for keyword in ['web', 'frontend', 'backend']):
        return TECH_DOMAINS["web_development"]
    
    elif any(keyword in goal_lower for keyword in ['data', 'analy', 'scien']):
        return TECH_DOMAINS["data_science"]
    
    elif any(keyword in goal_lower for keyword in ['devops', 'cloud', 'infra']):
        return TECH_DOMAINS["devops"]
    
    elif any(keyword in goal_lower for keyword in ['mobile', 'app', 'android', 'ios']):
        return TECH_DOMAINS["mobile_development"]
    
    elif any(keyword in goal_lower for keyword in ['security', 'cyber', 'hack']):
        return TECH_DOMAINS["cybersecurity"]
    
    elif 'game' in goal_lower:
        # Custom game development skills
        return ["C#", "Unity", "C++", "Unreal Engine", "Game Design", "3D Modeling", "Animation", "Physics"]
    
    # If no match at all, try a more generic match based on what's closest
    for keyword in goal_lower.split():
        for domain, skills in TECH_DOMAINS.items():
            domain_words = domain.replace('_', ' ').split()
            if any(domain_word.startswith(keyword) for domain_word in domain_words):
                return skills
    
    # If nothing matches, make an educated guess based on what they provided as current skills
    if any(skill.lower() in ['figma', 'sketch', 'xd', 'ui', 'ux'] for skill in current_skills):
        return TECH_DOMAINS["ui_design"]
    elif any(skill.lower() in ['photoshop', 'illustrator', 'indesign'] for skill in current_skills):
        return TECH_DOMAINS["graphic_design"]
    
    # Last resort default
    return TECH_DOMAINS["graphic_design"] if "design" in goal_lower else TECH_DOMAINS["traditional_art"]



def generate_career_phases(required_skills, current_skills, experience_level, career_goal):
    """Generate career learning phases based on required skills and experience level"""
    # Convert current skills to lowercase for comparison
    current_skills_lower = [skill.lower() for skill in current_skills]
    
    # Filter out skills user already has
    skills_to_learn = []
    for skill in required_skills:
        if not any(current_skill in skill.lower() for current_skill in current_skills_lower):
            skills_to_learn.append(skill)
    
    # If user knows most skills already, keep at least 3 for improvement
    if len(skills_to_learn) < 3:
        skills_to_learn = required_skills[:3]
    
    # Split skills into foundation, core, and advanced based on index position
    foundation_skills = []
    core_skills = []
    advanced_skills = []
    
    # Distribute skills based on their typical learning order
    for i, skill in enumerate(skills_to_learn):
        if i < len(skills_to_learn) // 3:
            foundation_skills.append(skill)
        elif i < (len(skills_to_learn) * 2) // 3:
            core_skills.append(skill)
        else:
            advanced_skills.append(skill)
    
    # Ensure each category has at least one skill
    if not foundation_skills and skills_to_learn:
        foundation_skills = [skills_to_learn[0]]
    if not core_skills and len(skills_to_learn) > 1:
        core_skills = [skills_to_learn[1]]
    if not advanced_skills and len(skills_to_learn) > 2:
        advanced_skills = [skills_to_learn[2]]
    
    # Create phases based on experience level
    phases = []
    
    # Determine if this is an art/design career
    is_art_career = any(art_term in career_goal.lower() for art_term in 
                       ['art', 'design', 'artist', 'graphic', 'ui', 'ux', 'illustrat', 'paint'])
    
    # Foundation phase (beginners only)
    if experience_level == 'beginner' and foundation_skills:
        if is_art_career:
            phase_name = 'Fundamental Art & Design Skills'
        else:
            phase_name = 'Foundation Building'
            
        phases.append({
            'name': phase_name,
            'skills': foundation_skills,
            'duration': '3-4 months',
            'resources': fetch_skill_resources(foundation_skills[0] if foundation_skills else '')
        })
    
    # Core skills phase (all levels)
    if core_skills:
        if is_art_career:
            phase_name = 'Technical Skill Development'
        else:
            phase_name = 'Core Skill Development'
            
        phases.append({
            'name': phase_name,
            'skills': core_skills,
            'duration': '4-6 months',
            'resources': fetch_skill_resources(core_skills[0] if core_skills else '')
        })
    
    # Advanced skills phase (intermediate and advanced)
    if advanced_skills:
        if experience_level != 'beginner' or not phases:  # Add for beginners if it's their first phase
            if is_art_career:
                phase_name = 'Style Development & Specialization'
            else:
                phase_name = 'Advanced Skills'
                
            phases.append({
                'name': phase_name,
                'skills': advanced_skills,
                'duration': '2-4 months',
                'resources': fetch_skill_resources(advanced_skills[0] if advanced_skills else '')
            })
    
    # Project building phase (all levels)
    project_skills = []
    
    # Customize project phase based on career goal
    if is_art_career:
        project_phase_name = 'Portfolio Development'
        
        # Customize project skills based on specific art career
        if 'ui' in career_goal.lower() or 'ux' in career_goal.lower():
            project_skills = ['UI/UX Portfolio', 'Case Studies', 'Interactive Prototypes']
        elif 'graphic' in career_goal.lower():
            project_skills = ['Brand Identity Project', 'Print Design Portfolio', 'Digital Marketing Assets']
        elif 'illustrat' in career_goal.lower() or 'digital' in career_goal.lower():
            project_skills = ['Illustration Series', 'Character Design Portfolio', 'Digital Art Collection']
        elif 'traditional' in career_goal.lower() or 'paint' in career_goal.lower():
            project_skills = ['Art Exhibition Preparation', 'Traditional Media Portfolio', 'Mixed Media Projects']
        else:
            project_skills = ['Portfolio Development', 'Personal Art Projects', 'Exhibition Preparation']
    # Keep existing tech career options
    elif 'web' in career_goal.lower():
        project_phase_name = 'Project Building'
        project_skills = ['Portfolio Website', 'Full Stack Projects', 'API Development']
    elif 'data' in career_goal.lower():
        project_phase_name = 'Project Building'
        project_skills = ['Data Analysis Portfolio', 'Machine Learning Projects', 'Data Visualization']
    elif 'game' in career_goal.lower():
        project_phase_name = 'Project Building'
        project_skills = ['Game Portfolio', 'Small Game Projects', 'Game Design Document']
    elif 'mobile' in career_goal.lower():
        project_phase_name = 'Project Building'
        project_skills = ['Mobile App Portfolio', 'Cross-platform App', 'App Store Deployment']
    else:
        project_phase_name = 'Project Building'
        project_skills = ['Portfolio Development', 'GitHub Projects', 'Documentation']
    
    phases.append({
        'name': project_phase_name,
        'skills': project_skills,
        'duration': '2-3 months',
        'resources': fetch_skill_resources(f"{career_goal} portfolio")
    })
    
    # Interview/career preparation phase (all levels)
    if is_art_career:
        interview_phase_name = 'Career Preparation'
        interview_skills = [
            f"{career_goal.capitalize()} Portfolio Review",
            "Art/Design Interview Skills", 
            "Freelance/Client Management"
        ]
    else:
        interview_phase_name = 'Interview Preparation'
        interview_skills = [
            f"{career_goal.capitalize()} Interview Preparation", 
            "Technical Interview Skills", 
            "Resume Building"
        ]
    
    phases.append({
        'name': interview_phase_name,
        'skills': interview_skills,
        'duration': '1-2 months',
        'resources': fetch_skill_resources(f"{career_goal} interview")
    })
    
    return phases

def calculate_estimated_completion(phases, experience_level):
    """Calculate the estimated time to complete the roadmap"""
    total_min_months = 0
    total_max_months = 0
    
    for phase in phases:
        duration = phase.get('duration', '')
        if '-' in duration:
            parts = duration.split('-')
            if len(parts) == 2:
                min_months = int(parts[0])
                max_months = int(parts[1].split()[0])  # Extract just the number
                total_min_months += min_months
                total_max_months += max_months
    
    # Adjust based on experience level
    if experience_level == 'intermediate':
        total_min_months = max(total_min_months - 2, 4)  # At least 4 months
        total_max_months = max(total_max_months - 3, 7)  # At least 7 months
    elif experience_level == 'advanced':
        total_min_months = max(total_min_months - 4, 3)  # At least 3 months
        total_max_months = max(total_max_months - 6, 5)  # At least 5 months
    
    return f"{total_min_months}-{total_max_months} months"

@csrf_exempt
@require_http_methods(["POST"])
def get_learning_resources(request):
    """Get personalized learning resources"""
    try:
        data = json.loads(request.body)
        search_term = data.get('searchTerm', '')
        skills = data.get('skills', [])
        
        # Get YouTube videos using the API
        youtube_resources = fetch_youtube_resources(search_term)
        
        # Get GitHub repositories
        github_resources = fetch_github_resources(search_term)
        
        # Get free courses from various sources
        free_courses = fetch_free_courses(search_term, skills)
        
        return JsonResponse({
            "success": True,
            "resources": {
                "videos": youtube_resources,
                "repositories": github_resources,
                "courses": free_courses
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def match_jobs(request):
    """Get India-specific jobs with experience levels"""
    try:
        data = json.loads(request.body)
        skills = data.get('skills', [])
        location = data.get('location', 'India')
        experience = data.get('experience', 'all')
        
        # Generate India-specific jobs
        jobs = generate_india_jobs(skills, location, experience)
        
        return JsonResponse({"success": True, "jobs": jobs})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

def generate_india_jobs(skills, location, experience_level):
    """Generate India-specific jobs"""
    # India-focused companies by city
    indian_companies = {
        "Bangalore": ["Infosys", "Wipro", "TCS", "IBM India", "Amazon India", "Flipkart", "Swiggy", "Ola", "Byju's", "Freshworks"],
        "Hyderabad": ["Microsoft India", "Google India", "Amazon India", "TCS", "Deloitte India", "Accenture", "Cognizant", "Capgemini"],
        "Chennai": ["Zoho", "Freshworks", "TCS", "Cognizant", "HCL Technologies", "Wipro", "PayPal India"],
        "Mumbai": ["TCS", "LTI", "Reliance Digital", "JP Morgan India", "HDFC Bank", "Morgan Stanley India"],
        "Delhi": ["Zomato", "MakeMyTrip", "Paytm", "HCL Technologies", "Samsung India", "Adobe India"],
        "Pune": ["Persistent Systems", "Tech Mahindra", "Cognizant", "Infosys", "Wipro", "Accenture"]
    }
    
    all_indian_companies = []
    for city_companies in indian_companies.values():
        all_indian_companies.extend(city_companies)
    
    # Experience level definitions
    experience_map = {
        "fresher": {"years": "0-1 years", "salary_range": "₹3,00,000 - ₹6,00,000"},
        "junior": {"years": "1-3 years", "salary_range": "₹6,00,000 - ₹10,00,000"},
        "mid": {"years": "3-5 years", "salary_range": "₹10,00,000 - ₹18,00,000"},
        "senior": {"years": "5+ years", "salary_range": "₹18,00,000 - ₹35,00,000"}
    }
    
    # If "All India" is selected, randomly select cities
    if location == "India":
        cities = list(indian_companies.keys())
    else:
        cities = [location]
    
    jobs = []
    job_titles_used = set()
    
    # For each skill, generate relevant jobs
    for skill in skills:
        skill_title = skill.title()
        
        # Generate job titles based on skill and experience
        job_options = []
        
        if experience_level == "fresher" or experience_level == "all":
            job_options.extend([
                f"{skill_title} Trainee",
                f"Junior {skill_title} Developer",
                f"Associate {skill_title} Engineer",
                f"{skill_title} Graduate Trainee"
            ])
        
        if experience_level == "junior" or experience_level == "all":
            job_options.extend([
                f"{skill_title} Developer",
                f"{skill_title} Engineer",
                f"Software Engineer - {skill_title}"
            ])
        
        if experience_level == "mid" or experience_level == "all":
            job_options.extend([
                f"Senior {skill_title} Developer",
                f"{skill_title} Team Lead",
                f"{skill_title} Specialist"
            ])
        
        if experience_level == "senior" or experience_level == "all":
            job_options.extend([
                f"Lead {skill_title} Engineer",
                f"Principal {skill_title} Developer",
                f"Technical Architect - {skill_title}"
            ])
            
        # Create jobs for this skill
        for job_title in job_options:
            if job_title in job_titles_used:
                continue
                
            job_titles_used.add(job_title)
            
            # Pick city and company
            city = random.choice(cities)
            company = random.choice(indian_companies[city])
            
            # Select experience level if "all" was chosen
            if experience_level == "all":
                if "Trainee" in job_title or "Junior" in job_title or "Associate" in job_title:
                    exp = "fresher"
                elif "Senior" in job_title or "Team Lead" in job_title:
                    exp = "mid"
                elif "Lead" in job_title or "Principal" in job_title or "Architect" in job_title:
                    exp = "senior"
                else:
                    exp = "junior"
            else:
                exp = experience_level
                
            # Job details
            job = {
                "title": job_title,
                "company": company,
                "location": city,
                "description": f"Great opportunity to work as a {job_title} at {company} in {city}. You will be working with cutting-edge technology and collaborate with talented professionals.",
                "salary": experience_map[exp]["salary_range"],
                "experience": experience_map[exp]["years"],
                "url": f"https://www.naukri.com/job-listings-{job_title.lower().replace(' ', '-')}-{company.lower().replace(' ', '-')}-{city.lower()}-{random.randint(10000, 99999)}",
                "date_posted": (datetime.now() - timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d")
            }
            
            jobs.append(job)
            
    # Randomize order and return first 10
    random.shuffle(jobs)
    return jobs[:10]    

def get_mock_jobs(skills, location):
    """Generate mock jobs based on skills and location"""
    # Map skills to job titles
    skill_to_titles = {
        'python': ['Python Developer', 'Data Scientist', 'Backend Engineer'],
        'javascript': ['Frontend Developer', 'Full Stack Developer', 'JavaScript Engineer'],
        'react': ['React Developer', 'Frontend Engineer', 'UI Developer'],
        'java': ['Java Developer', 'Software Engineer', 'Backend Developer'],
        'c#': ['.NET Developer', 'C# Engineer', 'Software Developer'],
        'sql': ['Database Administrator', 'Data Analyst', 'SQL Developer'],
        'ruby': ['Ruby Developer', 'Rails Engineer', 'Full Stack Developer'],
        'php': ['PHP Developer', 'Web Developer', 'Backend Engineer'],
        'swift': ['iOS Developer', 'Mobile Engineer', 'Swift Developer'],
        'kotlin': ['Android Developer', 'Kotlin Engineer', 'Mobile Developer'],
    }
    
    # Map location to companies and specific details
    location_map = {
        'remote': {
            'companies': ['Remote Tech Inc.', 'Global Solutions', 'Digital Nomad Co.'],
            'desc': 'Work from anywhere in the world with our distributed team.',
            'salary_range': '$80,000 - $120,000'
        },
        'london': {
            'companies': ['London Tech', 'UK Innovations', 'British Software Ltd'],
            'desc': 'Join our team in the heart of London\'s tech district.',
            'salary_range': '£45,000 - £70,000'
        },
        'new york': {
            'companies': ['NYC Code', 'Manhattan Tech', 'Big Apple Software'],
            'desc': 'Be part of New York\'s vibrant tech ecosystem.',
            'salary_range': '$90,000 - $140,000'
        },
        'san francisco': {
            'companies': ['SF Startups', 'Bay Area Tech', 'Silicon Valley Co.'],
            'desc': 'Work with cutting-edge technology in Silicon Valley.',
            'salary_range': '$110,000 - $180,000'
        },
        'berlin': {
            'companies': ['Berlin Digital', 'German Tech GmbH', 'Deutschland Software'],
            'desc': 'Join Berlin\'s booming tech scene with competitive benefits.',
            'salary_range': '€50,000 - €85,000'
        },
        'toronto': {
            'companies': ['Toronto Solutions', 'Canadian Tech', 'Ontario Software'],
            'desc': 'Be part of Toronto\'s diverse and growing tech community.',
            'salary_range': 'CAD $70,000 - $110,000'
        },
        'sydney': {
            'companies': ['Sydney Tech', 'Aussie Software', 'Down Under Digital'],
            'desc': 'Join our team with great work-life balance in Sydney.',
            'salary_range': 'AUD $80,000 - $130,000'
        },
        'singapore': {
            'companies': ['Singapore Solutions', 'Asian Tech Hub', 'Lion City Code'],
            'desc': 'Be part of Singapore\'s thriving technology sector.',
            'salary_range': 'SGD $60,000 - $120,000'
        },
        'india': {
            'companies': ['Indian Tech Solutions', 'Bangalore Code', 'Mumbai Digital'],
            'desc': 'Join India\'s fastest growing tech companies.',
            'salary_range': '₹8,00,000 - ₹24,00,000'
        },
    }    
    mock_jobs = []
    
    # Determine location details
    location_key = 'remote'  # default
    for loc in location_map:
        if loc in location.lower():
            location_key = loc
            break
    
    loc_details = location_map.get(location_key, location_map['remote'])
    
    # Generate jobs based on skills
    for skill in skills:
        skill = skill.lower()
        if skill in skill_to_titles:
            for title in skill_to_titles[skill]:
                company = random.choice(loc_details['companies'])
                
                # Calculate match score
                match_score = 50 + random.randint(10, 45)  # Base + random component
                
                job = {
                    "title": title,
                    "company": company,
                    "location": location if location else "Remote",
                    "description": f"We're looking for an experienced {title} with strong {skill} skills. {loc_details['desc']}",
                    "url": "https://example.com/apply",
                    "salary": loc_details['salary_range'],
                    "date_posted": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                    "match_score": match_score
                }
                mock_jobs.append(job)
    
    # If no specific skills mapped, generate generic tech jobs
    if not mock_jobs:
        generic_titles = ['Software Developer', 'Web Developer', 'Software Engineer', 'IT Specialist', 'DevOps Engineer']
        
        for i in range(min(5, len(generic_titles))):
            company = random.choice(loc_details['companies'])
            match_score = 50 + random.randint(10, 40)
            
            job = {
                "title": generic_titles[i],
                "company": company,
                "location": location if location else "Remote",
                "description": f"We're looking for a talented {generic_titles[i]} to join our team. {loc_details['desc']}",
                "url": "https://example.com/apply",
                "salary": loc_details['salary_range'],
                "date_posted": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "match_score": match_score
            }
            mock_jobs.append(job)
    
    # Ensure we don't have duplicate job titles from the same company
    unique_jobs = []
    seen_combinations = set()
    
    for job in mock_jobs:
        key = (job['title'], job['company'])
        if key not in seen_combinations:
            seen_combinations.add(key)
            unique_jobs.append(job)
    
    return unique_jobs[:10]  # Limit to 10 jobs maximum
    
def fetch_github_jobs(skills, location):
    try:
        # GitHub Jobs API was deprecated, use alternative like Remotive API
        api_url = "https://remotive.io/api/remote-jobs"
        params = {
            "search": " ".join(skills[:2]),  # Use first 2 skills for search
            "limit": 5
        }
        
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('jobs', []):
                # Calculate match score
                match_score = calculate_match_score(job, skills)
                
                jobs.append({
                    "title": job.get('title', 'Position'),
                    "company": job.get('company_name', 'Company'),
                    "location": job.get('candidate_required_location', 'Remote'),
                    "description": job.get('description', '')[:200] + "...",
                    "url": job.get('url', '#'),
                    "date_posted": job.get('publication_date', ''),
                    "match_score": match_score
                })
            
            return jobs
    except:
        return []
    
    return []

def calculate_match_score(job, user_skills):
    """Calculate job match score based on skills"""
    score = 50  # Base score
    
    # Check job title for skills
    if 'title' in job:
        title = job['title'].lower()
        for skill in user_skills:
            if skill.lower() in title:
                score += 10
    
    # Check job description for skills
    if 'description' in job:
        description = job['description'].lower()
        for skill in user_skills:
            if skill.lower() in description:
                score += 5
    
    # Cap at 100%
    return min(score, 100)

def fetch_reed_jobs(skills, location):
    """Fetch jobs from Reed API (UK focused)"""
    try:
        # Reed API requires API key
        api_key = os.getenv('REED_API_KEY')
        if not api_key:
            return []
        
        api_url = "https://www.reed.co.uk/api/1.0/search"
        params = {
            "keywords": " ".join(skills[:2]),
            "locationName": location if location.lower() != 'remote' else '',
            "resultsToTake": 5
        }
        
        response = requests.get(
            api_url, 
            params=params,
            auth=(api_key, '')
        )
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('results', []):
                # Calculate match score
                match_score = calculate_match_score(job, skills)
                
                jobs.append({
                    "title": job.get('jobTitle', 'Position'),
                    "company": job.get('employerName', 'Company'),
                    "location": job.get('locationName', 'Unknown Location'),
                    "description": job.get('jobDescription', '')[:200] + "...",
                    "url": job.get('jobUrl', '#'),
                    "salary": job.get('maximumSalary') and f"£{job.get('minimumSalary')} - £{job.get('maximumSalary')}",
                    "date_posted": job.get('date', ''),
                    "match_score": match_score
                })
            
            return jobs
    except:
        return []
    
    return []

def fetch_adzuna_jobs(skills, location):
    """Fetch jobs from Adzuna API (multiple countries)"""
    try:
        # Adzuna API requires app_id and api_key
        app_id = os.getenv('ADZUNA_APP_ID')
        api_key = os.getenv('ADZUNA_API_KEY')
        
        if not app_id or not api_key:
            return []
        
        # Determine country code based on location
        country_code = get_country_code(location)
        
        api_url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
        params = {
            "app_id": app_id,
            "app_key": api_key,
            "what": " ".join(skills[:2]),
            "where": location if location.lower() != 'remote' else '',
            "results_per_page": 5
        }
        
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            jobs = []
            
            for job in data.get('results', []):
                # Calculate match score
                match_score = calculate_match_score(job, skills)
                
                jobs.append({
                    "title": job.get('title', 'Position'),
                    "company": job.get('company', {}).get('display_name', 'Company'),
                    "location": job.get('location', {}).get('display_name', 'Unknown Location'),
                    "description": job.get('description', '')[:200] + "...",
                    "url": job.get('redirect_url', '#'),
                    "salary": job.get('salary_is_predicted') == 0 and job.get('salary_min') and 
                             f"{job.get('salary_min')} - {job.get('salary_max')} {job.get('salary_currency_code', '')}",
                    "date_posted": job.get('created', ''),
                    "match_score": match_score
                })
            
            return jobs
    except:
        return []
    
    return []

def get_country_code(location):
    """Get two-letter country code based on location string"""
    location = location.lower()
    
    if any(country in location for country in ['united kingdom', 'uk', 'england', 'scotland', 'wales']):
        return 'gb'
    elif any(country in location for country in ['united states', 'usa', 'us', 'america']):
        return 'us'
    elif 'australia' in location:
        return 'au'
    elif 'germany' in location:
        return 'de'
    elif 'canada' in location:
        return 'ca'
    elif 'india' in location:
        return 'in'
    # Add more countries as needed
    else:
        return 'gb'  # Default to GB


@csrf_exempt
@require_http_methods(["POST"])
def analyze_resume(request):
    """Analyze resume using NLP techniques"""
    try:
        resume_text = ""
        
        # Check if a file is uploaded
        if 'resume' in request.FILES:
            resume_file = request.FILES['resume']
            # Handle file based on type
            file_content = resume_file.read()
            
            # For PDF files
            if resume_file.name.lower().endswith('.pdf'):
                try:
                    import PyPDF2
                    from io import BytesIO
                    
                    pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
                    for page in range(len(pdf_reader.pages)):
                        resume_text += pdf_reader.pages[page].extract_text() + "\n"
                except:
                    return JsonResponse({
                        "success": False, 
                        "error": "Failed to parse PDF file"
                    })
            
            # For DOCX files
            elif resume_file.name.lower().endswith('.docx'):
                try:
                    import docx
                    from io import BytesIO
                    
                    doc = docx.Document(BytesIO(file_content))
                    for para in doc.paragraphs:
                        resume_text += para.text + "\n"
                except:
                    return JsonResponse({
                        "success": False, 
                        "error": "Failed to parse DOCX file"
                    })
            
            # For TXT files
            elif resume_file.name.lower().endswith('.txt'):
                resume_text = file_content.decode('utf-8')
            
            else:
                return JsonResponse({
                    "success": False,
                    "error": "Unsupported file format. Please upload PDF, DOCX, or TXT."
                })
        
        # If no file but resume text is provided
        elif 'resumeText' in request.POST or (request.body and 'resumeText' in json.loads(request.body)):
            # Handle JSON data
            if request.body:
                data = json.loads(request.body)
                resume_text = data.get('resumeText', '')
        
        else:
            return JsonResponse({
                "success": False,
                "error": "No resume provided. Please upload a file or paste resume text."
            })
        
        # Simple keyword-based analysis
        tech_skills = []
        soft_skills = []
        
        # Technical skills to look for
        common_tech_skills = [
            "python", "java", "javascript", "html", "css", "react", "angular",
            "node.js", "django", "flask", "sql", "nosql", "mongodb", "aws",
            "azure", "git", "docker", "kubernetes", "machine learning", "ai"
        ]
        
        # Soft skills to look for
        common_soft_skills = [
            "teamwork", "communication", "leadership", "problem solving",
            "critical thinking", "time management", "creativity", "adaptability",
            "project management", "collaboration", "organizational"
        ]
        
        resume_text_lower = resume_text.lower()
        
        for skill in common_tech_skills:
            if skill in resume_text_lower:
                tech_skills.append(skill.title())
        
        for skill in common_soft_skills:
            if skill in resume_text_lower:
                soft_skills.append(skill.title())
        
        # Generate recommendations
        recommendations = []
        
        if len(tech_skills) < 5:
            recommendations.append("Add more technical skills that are relevant to your target role")
        
        if len(soft_skills) < 3:
            recommendations.append("Include more soft skills to showcase your workplace capabilities")
        
        if "objective" not in resume_text_lower and "summary" not in resume_text_lower:
            recommendations.append("Add a clear professional summary or objective statement")
        
        if "experience" not in resume_text_lower or "work" not in resume_text_lower:
            recommendations.append("Include detailed work experience with accomplishments")
        
        if len(resume_text.split()) < 300:
            recommendations.append("Your resume appears too short. Add more details about your experience")
        
        # Simple ATS compatibility score
        ats_score = 60  # Base score
        
        # Award points for good resume practices
        if len(tech_skills) >= 5:
            ats_score += 10
        
        if len(soft_skills) >= 3:
            ats_score += 5
        
        if "experience" in resume_text_lower or "work" in resume_text_lower:
            ats_score += 10
        
        if "education" in resume_text_lower:
            ats_score += 5
        
        if len(resume_text.split()) >= 300:
            ats_score += 10
        
        # Cap at 100
        ats_score = min(ats_score, 100)
        
        # Format response
        analysis = {
            "skills": {
                "technical": tech_skills,
                "soft": soft_skills
            },
            "recommendations": recommendations[:5],  # Limit to top 5 recommendations
            "ats_compatibility_score": ats_score
        }
        
        return JsonResponse({"success": True, "analysis": analysis})
    
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@csrf_exempt
@require_http_methods(["GET"])
def get_career_trends(request):
    """Get industry and career trends"""
    try:
        industry = request.GET.get('industry', 'technology')
        
        # Get trending skills and technologies
        trends = fetch_career_trends(industry)
        
        return JsonResponse({
            "success": True,
            "trends": trends
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

# Helper functions
def identify_required_skills(goal):
    """Identify skills required for a career goal"""
    goal = goal.lower()
    required_skills = []
    
    # Check which domain the goal belongs to
    for domain, skills in TECH_DOMAINS.items():
        domain_keywords = domain.split('_')
        if any(keyword in goal for keyword in domain_keywords):
            required_skills.extend(skills)
    
    # If no specific domain matched, return a default set
    if not required_skills:
        required_skills = TECH_DOMAINS["web_development"]
    
    return required_skills

def create_personalized_roadmap(user_skills, goal, required_skills, experience):
    """Create a personalized career roadmap"""
    # Convert to lowercase for comparison
    user_skills_lower = [skill.lower() for skill in user_skills]
    
    # Identify missing skills
    missing_skills = [skill for skill in required_skills 
                     if skill.lower() not in user_skills_lower]
    
    # Create roadmap based on experience level
    if experience.lower() == 'beginner':
        timeline = "12-18 months"
        milestones = [
            {
                "title": "Foundation Building",
                "skills": required_skills[:3],
                "duration": "3-4 months",
                "resources": fetch_skill_resources(required_skills[:3][0])
            },
            {
                "title": "Core Skill Development",
                "skills": missing_skills[:3],
                "duration": "4-6 months",
                "resources": fetch_skill_resources(missing_skills[:3][0] if missing_skills else required_skills[0])
            },
            {
                "title": "Project Building",
                "skills": ["Portfolio development", "GitHub presence"],
                "duration": "2-4 months",
                "resources": fetch_skill_resources("portfolio projects")
            },
            {
                "title": "Interview Preparation",
                "skills": ["Technical interview skills", "Resume building"],
                "duration": "1-2 months",
                "resources": fetch_skill_resources("technical interview")
            }
        ]
    else:  # intermediate or advanced
        timeline = "6-12 months"
        milestones = [
            {
                "title": "Skill Gap Filling",
                "skills": missing_skills[:3],
                "duration": "2-3 months",
                "resources": fetch_skill_resources(missing_skills[:3][0] if missing_skills else required_skills[0])
            },
            {
                "title": "Advanced Topics",
                "skills": required_skills[-3:],  # Last 3 skills (more advanced)
                "duration": "3-4 months",
                "resources": fetch_skill_resources(required_skills[-3:][0])
            },
            {
                "title": "Industry Projects",
                "skills": ["Complex project management", "Team collaboration"],
                "duration": "2-3 months",
                "resources": fetch_skill_resources("advanced projects")
            },
            {
                "title": "Career Advancement",
                "skills": ["Leadership", "Domain expertise"],
                "duration": "1-2 months",
                "resources": fetch_skill_resources("career advancement")
            }
        ]
    
    return {
        "goal": goal,
        "timeline": timeline,
        "milestones": milestones,
        "requiredSkills": required_skills,
        "missingSkills": missing_skills
    }

def fetch_youtube_resources(search_term):
    """Fetch relevant YouTube tutorials"""
    try:
        if not YOUTUBE_API_KEY:
            # Return mock data if API key is not available
            return generate_mock_youtube_data(search_term)
        
        # Using YouTube Data API v3
        search_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": f"{search_term} tutorial",
            "type": "video",
            "maxResults": 5,
            "relevanceLanguage": "en",
            "key": YOUTUBE_API_KEY
        }
        
        response = requests.get(search_url, params=params)
        if response.status_code != 200:
            return generate_mock_youtube_data(search_term)
            
        videos = response.json().get('items', [])
        
        return [{
            "title": video['snippet']['title'],
            "description": video['snippet']['description'],
            "thumbnail": video['snippet']['thumbnails']['medium']['url'],
            "videoId": video['id']['videoId'],
            "url": f"https://www.youtube.com/watch?v={video['id']['videoId']}"
        } for video in videos]
    except Exception:
        return generate_mock_youtube_data(search_term)

def generate_mock_youtube_data(search_term):
    """Generate mock YouTube data when API is unavailable"""
    return [
        {
            "title": f"Complete {search_term} Tutorial for Beginners",
            "description": f"Learn {search_term} from scratch with this comprehensive guide",
            "thumbnail": f"https://i.ytimg.com/vi/placeholder/default.jpg",
            "videoId": "dQw4w9WgXcQ",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        },
        {
            "title": f"Advanced {search_term} Techniques",
            "description": f"Master advanced concepts in {search_term}",
            "thumbnail": f"https://i.ytimg.com/vi/placeholder2/default.jpg",
            "videoId": "dQw4w9WgXcQ",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
    ]

def fetch_github_resources(search_term):
    """Fetch trending GitHub repositories for learning"""
    try:
        url = f"https://api.github.com/search/repositories"
        params = {
            "q": f"{search_term} tutorial OR learning",
            "sort": "stars",
            "per_page": 5
        }
        
        response = requests.get(url, params=params)
        repos = response.json().get('items', [])
        
        if not repos:
            return generate_mock_github_data(search_term)
        
        return [{
            "name": repo['name'],
            "description": repo['description'] or f"A repository about {search_term}",
            "url": repo['html_url'],
            "stars": repo['stargazers_count'],
            "language": repo['language']
        } for repo in repos]
    except:
        return generate_mock_github_data(search_term)

def generate_mock_github_data(search_term):
    """Generate mock GitHub data"""
    return [
        {
            "name": f"{search_term}-tutorial",
            "description": f"A comprehensive tutorial on {search_term}",
            "url": f"https://github.com/example/{search_term}-tutorial",
            "stars": 1200,
            "language": "JavaScript"
        },
        {
            "name": f"learn-{search_term}",
            "description": f"Learning resources for {search_term}",
            "url": f"https://github.com/example/learn-{search_term}",
            "stars": 890,
            "language": "Python"
        }
    ]

def fetch_free_courses(search_term, skills):
    """Fetch free courses from various sources"""
    courses = []
    
    # Try to fetch from freeCodeCamp API
    try:
        # freeCodeCamp doesn't have a public API, so we'll use a workaround
        url = "https://www.freecodecamp.org/news/wp-json/wp/v2/posts"
        params = {
            "search": search_term,
            "per_page": 3
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            posts = response.json()
            for post in posts:
                courses.append({
                    "title": post['title']['rendered'],
                    "description": "Free tutorial from freeCodeCamp",
                    "url": post['link'],
                    "platform": "freeCodeCamp",
                    "free": True
                })
    except:
        # If freeCodeCamp fails, add mock freeCodeCamp course
        courses.append({
            "title": f"Learn {search_term}",
            "description": f"Comprehensive free course on {search_term}",
            "url": f"https://www.freecodecamp.org/learn/{search_term.lower().replace(' ', '-')}",
            "platform": "freeCodeCamp",
            "free": True
        })
    
    # Try to fetch from MIT OpenCourseWare
    try:
        mit_url = f"https://ocw.mit.edu/api/v0/search/?q={search_term}&type=course"
        response = requests.get(mit_url)
        if response.status_code == 200:
            mit_courses = response.json().get("results", [])[:2]
            for course in mit_courses:
                courses.append({
                    "title": course['title'],
                    "description": course.get("description", "MIT OpenCourseWare"),
                    "url": f"https://ocw.mit.edu{course['url']}",
                    "platform": "MIT OpenCourseWare",
                    "free": True
                })
    except:
        # If MIT OCW fails, add a mock MIT course
        courses.append({
            "title": f"Introduction to {search_term}",
            "description": f"MIT course covering {search_term} fundamentals",
            "url": f"https://ocw.mit.edu/search/?q={search_term}",
            "platform": "MIT OpenCourseWare",
            "free": True
        })
    
    return courses

def fetch_jobs_data(skills, location):
    """Fetch job listings from GitHub Jobs API or alternatives"""
    try:
        # Try GitHub Jobs API (note: GitHub Jobs API has been deprecated)
        jobs = []
        
        # Try Remotive API as an alternative (free, no auth required)
        remotive_url = "https://remotive.io/api/remote-jobs"
        response = requests.get(remotive_url)
        
        if response.status_code == 200:
            all_jobs = response.json().get('jobs', [])
            
            # Filter jobs based on skills
            for skill in skills:
                filtered_jobs = [job for job in all_jobs if 
                                skill.lower() in job.get('title', '').lower() or 
                                skill.lower() in job.get('description', '').lower()]
                jobs.extend(filtered_jobs[:3])  # Take up to 3 jobs per skill
        
        # If we couldn't get jobs, use mock data
        if not jobs:
            jobs = generate_mock_jobs(skills, location)
            
        return jobs
    except:
        return generate_mock_jobs(skills, location)

def generate_mock_jobs(skills, location):
    """Generate mock job listings based on skills"""
    mock_jobs = []
    companies = ["TechCorp", "InnovateSoft", "DataDynamics", "CodeCraft", "ByteBuilders"]
    
    for skill in skills:
        for i in range(2):  # 2 mock jobs per skill
            mock_jobs.append({
                "title": f"{skill} Developer" if i == 0 else f"Senior {skill} Engineer",
                "company": random.choice(companies),
                "location": location or "Remote",
                "salary": f"${random.randint(70, 150)}k-${random.randint(90, 180)}k",
                "description": f"We are looking for a {skill} developer with experience in building scalable applications.",
                "url": f"https://example.com/jobs/{skill.lower().replace(' ', '-')}-{i}",
                "date_posted": (datetime.now().strftime("%Y-%m-%d"))
            })
    
    return mock_jobs

def calculate_job_matches(jobs, user_skills):
    """Calculate job match score based on user skills"""
    scored_jobs = []
    
    for job in jobs:
        # Initialize score
        score = 50  # Base score
        
        # Calculate match based on skills
        for skill in user_skills:
            skill_lower = skill.lower()
            title = job.get('title', '').lower()
            description = job.get('description', '').lower()
            
            # Skill in title is a strong match
            if skill_lower in title:
                score += 15
            # Skill in description
            elif skill_lower in description:
                score += 10
        
        # Cap score at 100
        score = min(score, 100)
        
        # Add score to job
        job_with_score = job.copy()
        job_with_score['match_score'] = score
        scored_jobs.append(job_with_score)
    
    # Sort by match score
    scored_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    
    return scored_jobs

def analyze_resume_content(resume_text):
    """Analyze resume content for skills and improvement suggestions"""
    # Lists of skills to check for
    tech_skills = []
    for domain_skills in TECH_DOMAINS.values():
        tech_skills.extend(domain_skills)
    
    soft_skills = [
        "Communication", "Leadership", "Teamwork", "Problem Solving", 
        "Critical Thinking", "Time Management", "Adaptability", "Creativity"
    ]
    
    # Check for skills in resume
    found_tech_skills = [skill for skill in tech_skills 
                         if skill.lower() in resume_text.lower()]
    
    found_soft_skills = [skill for skill in soft_skills 
                         if skill.lower() in resume_text.lower()]
    
    # Generate recommendations
    recommendations = []
    
    # Check for standard sections
    if "experience" not in resume_text.lower():
        recommendations.append("Add a dedicated Experience section to highlight your work history")
    
    if "education" not in resume_text.lower():
        recommendations.append("Include an Education section with your academic background")
    
    if len(found_tech_skills) < 5:
        recommendations.append("Add more technical skills relevant to your target role")
    
    if len(found_soft_skills) < 3:
        recommendations.append("Include soft skills like Communication, Leadership, or Problem Solving")
    
    if "project" not in resume_text.lower():
        recommendations.append("Add a Projects section to showcase your practical experience")
    
    # Calculate ATS score
    ats_score = calculate_ats_compatibility(resume_text, found_tech_skills, found_soft_skills)
    
    return {
        "skills": {
            "technical": found_tech_skills,
            "soft": found_soft_skills
        },
        "recommendations": recommendations[:5],  # Limit to top 5 recommendations
        "ats_compatibility_score": ats_score
    }

def calculate_ats_compatibility(resume_text, tech_skills, soft_skills):
    """Calculate ATS compatibility score"""
    score = 60  # Base score
    
    # Score based on skills
    score += min(len(tech_skills) * 3, 15)  # Up to 15 points for technical skills
    score += min(len(soft_skills) * 2, 10)  # Up to 10 points for soft skills
    
    # Check for important sections
    if "experience" in resume_text.lower():
        score += 5
    if "education" in resume_text.lower():
        score += 5
    if "skills" in resume_text.lower():
        score += 5
    
    # Length check (ATS prefers reasonably detailed resumes)
    word_count = len(resume_text.split())
    if word_count > 300:
        score += 5
    
    # Cap at 100
    return min(score, 100)

def fetch_career_trends(industry):
    """Fetch career trends data from GitHub and other sources"""
    try:
        # Get trending repositories for industry
        github_url = f"https://api.github.com/search/repositories"
        params = {
            "q": f"topic:{industry}",
            "sort": "stars",
            "order": "desc",
            "per_page": 10
        }
        
        response = requests.get(github_url, params=params)
        if response.status_code != 200:
            return generate_mock_trends(industry)
            
        repos = response.json().get('items', [])
        
        # Extract trending technologies
        languages = {}
        topics = {}
        
        for repo in repos:
            # Count languages
            lang = repo.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
            
            # Count topics
            repo_topics = repo.get('topics', [])
            for topic in repo_topics:
                topics[topic] = topics.get(topic, 0) + 1
        
        # Sort by count
        trending_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        trending_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        
        # Generate trend data for charts
        trend_data = generate_trend_chart_data(industry, trending_languages[:3])
        
        return {
            "trending_technologies": [{"name": lang, "count": count} 
                                     for lang, count in trending_languages[:5]],
            "trending_topics": [{"name": topic, "count": count} 
                              for topic, count in trending_topics[:5]],
            "trend_data": trend_data,
            "industry_insights": generate_industry_insights(industry)
        }
    except:
        return generate_mock_trends(industry)

def generate_trend_chart_data(industry, top_languages):
    """Generate trend chart data for visualizations"""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    chart_data = []
    
    for month in months:
        data_point = {"month": month}
        
        # Add data for each top language with some random variation
        for lang, _ in top_languages:
            base_value = random.randint(70, 85)
            monthly_change = random.randint(-5, 8)
            data_point[lang] = base_value + monthly_change
            
        chart_data.append(data_point)
    
    return chart_data

def generate_industry_insights(industry):
    """Generate industry insights based on industry"""
    insights = {
        "technology": {
            "jobGrowth": "+15%",
            "averageSalary": "$110,000",
            "topSkills": ["JavaScript", "Python", "Cloud Computing"]
        },
        "data": {
            "jobGrowth": "+18%",
            "averageSalary": "$120,000",
            "topSkills": ["Python", "SQL", "Machine Learning"]
        },
        "design": {
            "jobGrowth": "+10%",
            "averageSalary": "$90,000",
            "topSkills": ["UI/UX", "Figma", "Adobe Creative Suite"]
        },
        "marketing": {
            "jobGrowth": "+8%",
            "averageSalary": "$85,000",
            "topSkills": ["Digital Marketing", "SEO", "Social Media"]
        }
    }
    
    # Return matching insights or default to technology
    for key in insights.keys():
        if key in industry.lower():
            return insights[key]
    
    return insights["technology"]

def generate_mock_trends(industry):
    """Generate mock trend data when API fails"""
    return {
        "trending_technologies": [
            {"name": "Python", "count": 42},
            {"name": "JavaScript", "count": 38},
            {"name": "React", "count": 27}
        ],
        "trending_topics": [
            {"name": "machine-learning", "count": 18},
            {"name": "web-development", "count": 15},
            {"name": "data-science", "count": 12}
        ],
        "trend_data": [
            {"month": "Jan", "Python": 75, "JavaScript": 85, "React": 65},
            {"month": "Feb", "Python": 78, "JavaScript": 82, "React": 70},
            {"month": "Mar", "Python": 82, "JavaScript": 80, "React": 75},
            {"month": "Apr", "Python": 85, "JavaScript": 83, "React": 78},
            {"month": "May", "Python": 88, "JavaScript": 85, "React": 80},
            {"month": "Jun", "Python": 92, "JavaScript": 87, "React": 85}
        ],
        "industry_insights": {
            "jobGrowth": "+15%",
            "averageSalary": "$110,000",
            "topSkills": ["JavaScript", "Python", "Cloud Computing"]
        }
    }

def fetch_skill_resources(skill):
    """Get learning resources for a specific skill"""
    # Get YouTube tutorials
    videos = fetch_youtube_resources(skill)[:2]
    
    # Mock course data (simpler than making API calls for each skill)
    courses = [
        {
            "title": f"Complete {skill} Course",
            "platform": "freeCodeCamp",
            "url": f"https://www.freecodecamp.org/learn/{skill.lower().replace(' ', '-')}",
            "free": True
        },
        {
            "title": f"{skill} for Beginners",
            "platform": "MIT OpenCourseWare",
            "url": f"https://ocw.mit.edu/search/?q={skill.lower().replace(' ', '+')}",
            "free": True
        }
    ]
    
    return {
        "videos": videos,
        "courses": courses
    }