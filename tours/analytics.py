from users.models import User
from tours.models import Tour, TourCategory
from django.db.models import Count

def get_admin_analytics():
    user_by_role= User.objects.values('role').annotate(count=Count('id'))
    tours_by_status= Tour.objects.values('status').annotate(count=Count('id'))
    top_categories = TourCategory.objects.annotate(tour_count=Count('tours')).order_by('-tour_count')[:5]


    return {
        'users_by_role': user_by_role,
        'tours_by_status': tours_by_status,
        'top_categories': [
            {'name': cat.name, 'tour_count': cat.tour_count}
            for cat in top_categories
        ]
    }