from django.core.management.base import BaseCommand
from meetup.models import Interest

class Command(BaseCommand):
    help = 'Seed the database with initial interests'

    def handle(self, *args, **kwargs):
        interests = [
            "Reading",
            "Photography",
            "Gaming",
            "Music",
            "Travel",
            "Painting",
            "Politics",
            "Charity",
            "Cooking",
            "Pets",
            "Sports",
            "Fashion",
        ]

        for interest_name in interests:
            interest, created = Interest.objects.get_or_create(name=interest_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Interest "{interest_name}" created'))
            else:
                self.stdout.write(f'Interest "{interest_name}" already exists')

        self.stdout.write(self.style.SUCCESS('Interests have been seeded successfully'))
