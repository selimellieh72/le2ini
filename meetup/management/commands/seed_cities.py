from django.core.management.base import BaseCommand
from meetup.models import City

class Command(BaseCommand):
    help = 'Seed the database with initial cities'

    def handle(self, *args, **kwargs):
        cities = [
    "Akkar",
    "Minieh-Danniyeh",
    "Tripoli",
    "Zgharta",
    "Bcharre",
    "Koura",
    "Batroun",
    "Jbeil",
    "Keserwan",
    "Metn",
    "Baabda",
    "Aley",
    "Chouf",
    "Jezzine",
    "Saida",
    "Tyre",
    "Nabatieh",
    "Marjeyoun",
    "Hasbaya",
    "Bint Jbeil",
    "West Bekaa",
    "Rachaya",
    "Zahle",
    "Baalbek",
    "Hermel"
]

        for city_name in cities:
            interest, created = City.objects.get_or_create(name=city_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Interest "{city_name}" created'))
            else:
                self.stdout.write(f'Interest "{city_name}" already exists')

        self.stdout.write(self.style.SUCCESS('Interests have been seeded successfully'))
